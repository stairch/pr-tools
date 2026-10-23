# -*- coding: utf-8 -*-
"""Foodstoffi Menu Scraper"""

from __future__ import annotations

__copyright__ = "Copyright (c) 2024 STAIR. All Rights Reserved."
__email__ = "info@stair.ch"

from dataclasses import dataclass, field
from typing import Any
import re
import json
import datetime
import logging

import aiohttp
import discord
import bs4
from pyaddict import JDict, JList

from common.aioschedule import AioSchedule
from common.constants import STAIR_GREEN
from db.datamodels.announcement import AnnouncementType
from integration.discord.stan import Stan
from integration.discord.persona import PersonaSender, Persona

URL = "https://app.food2050.ch/de/zfv/hslu,standort-rotkreuz/hslu-iandw/mittagsverpflegung/menu/weekly"  # pylint: disable=line-too-long


_RSC_CHUNK = re.compile(r"self\.__next_f\.push\((.*)\)", re.DOTALL)
_RSC_REF = re.compile(r"\$([0-9a-f]+):(.+)")
_MENU_CATEGORY_KEY = '"menuCategory":'


_PERSONA = Persona.get("Chef Stan-dwich", Persona.default())
_ANNOUNCEMENT_TYPE = AnnouncementType.get("canteen-menu", AnnouncementType.default())


def _resolve_rsc_refs(node: Any, row_id: str, row: Any) -> Any:
    """Replace RSC references into `row` with the objects they point to"""
    if isinstance(node, list):
        return [_resolve_rsc_refs(x, row_id, row) for x in node]
    if isinstance(node, dict):
        return {k: _resolve_rsc_refs(v, row_id, row) for k, v in node.items()}
    match = _RSC_REF.fullmatch(node) if isinstance(node, str) else None
    if not match or match.group(1) != row_id:
        return node
    target = row
    for key in match.group(2).split(":"):
        if isinstance(target, dict):
            target = target[key]
        elif target[:1] == ["$"] and key == "props":
            target = target[3]
        else:
            target = target[int(key)]
    return _resolve_rsc_refs(target, row_id, row)


@dataclass
class Dish:  # pylint: disable=too-many-instance-attributes
    """A recipe"""

    typename: str
    id: str
    category: str
    is_balanced: bool
    title: str
    climate_prediction: str
    slug: str
    is_vegan: bool
    is_vegetarian: bool
    _allergens: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, value: JDict, category: str) -> Dish | None:
        """Create a recipe from a dictionary"""
        if not value:
            return None

        if "Geschlossen" in value.ensure("title", str):
            return None

        return cls(
            typename=value.ensure("__typename", str),
            id=value.ensure("id", str),
            category=category,
            is_balanced=value.chain().ensure(
                "stats.food2050HealthRating.isBalanced", bool
            ),
            title=value.ensure("name", str),
            climate_prediction=value.chain()
            .ensure("stats.food2050climateImpact.rating", str)
            .lower(),
            slug=value.ensure("slug", str),
            _allergens=[
                JDict(allergen).chain().ensure("allergen.externalId", str)
                for allergen in value.ensure("allergens", list)
            ],
            is_vegan=value.ensure("isVegan", bool),
            is_vegetarian=value.ensure("isVegetarian", bool),
        )

    @property
    def allergens(self) -> list[str]:
        """Get the allergens"""
        return [
            re.sub(r"(?<=[a-z])(?=[A-Z])", " ", allergen).title()
            for allergen in self._allergens
            if allergen != ""
        ]

    @property
    def as_embed(self) -> discord.Embed:
        """Get the recipe as an embed"""
        embed = discord.Embed(
            title=self.category,
            description=self.title,
            color=STAIR_GREEN,
        )
        tags: list[str] = []
        if self.is_vegan:
            tags.append("🌱 Vegan")
        elif self.is_vegetarian:
            tags.append("🌿 Vegetarian")
        if self.is_balanced:
            tags.append("⚖️ Balanced")
        if self.climate_prediction:
            tags.append(f" 🌍 {self.climate_prediction.title()} Climate Impact")
        if self.allergens:
            tags.append(f"🚫 {', '.join(self.allergens)}")
        embed.set_footer(text=" | ".join(tags))
        return embed


@dataclass
class MenuItem:
    """A recipe item"""

    typename: str
    date: datetime.date
    recipe: Dish | None

    @classmethod
    def from_dict(cls, value: JDict, date: datetime.date) -> MenuItem | None:
        """Create a recipe item from a dictionary"""
        category = value.chain().ensure("category.name", str)
        item = cls(
            typename=value.ensure("__typename", str),
            date=date,
            recipe=Dish.from_dict(value.ensureCast("dish", JDict), category),
        )
        if not item.recipe:
            return None
        return item


@dataclass
class CanteenDay:
    """A category of recipes"""

    typename: str
    id: str
    date: datetime.date
    recipes: list[MenuItem]

    @classmethod
    def from_dict(cls, value: JDict) -> CanteenDay:
        """Create a category from a dictionary"""
        date = datetime.datetime.fromisoformat(
            value.chain().ensure("from.dateLocal", str)
        ).date()
        recipes = [
            MenuItem.from_dict(recipe, date)
            for recipe in value.ensureCast("menuItems", JList)
            .iterator()
            .ensureCast(JDict)
        ]
        recipes = [recipe for recipe in recipes if recipe]
        return cls(
            typename=value.ensure("__typename", str),
            id=value.ensure("id", str),
            date=date,
            recipes=recipes,  # type: ignore
        )


@dataclass
class Menu:
    """A menu"""

    typename: str
    id: str
    note: str
    categories: list[CanteenDay]

    @classmethod
    def _from_dict(cls, value: JDict) -> Menu:
        return cls(
            typename=value.ensure("__typename", str),
            id=value.ensure("id", str),
            note=value.ensure("note", str),
            categories=[
                CanteenDay.from_dict(category)
                for category in value.chain()
                .ensureCast("calendar.week.daily", JList)
                .iterator()
                .ensureCast(JDict)
            ],
        )

    @property
    def todays_dishes(self) -> list[Dish]:
        """Get the recipes for today"""
        for category in self.categories:
            if category.date == datetime.date.today():
                return [item.recipe for item in category.recipes if item.recipe]
        return []

    @staticmethod
    def _extract_menu_category(html: str) -> JDict | None:
        """Extract the menu category from the page's RSC payload"""
        soup = bs4.BeautifulSoup(html, "html.parser")
        payload = ""
        for script in soup.find_all("script"):
            if not isinstance(script, bs4.Tag):
                continue
            match = _RSC_CHUNK.fullmatch(script.string or "")
            if not match:
                continue
            chunk = json.loads(match.group(1))
            if chunk[0] == 1:
                payload += chunk[1]
        start = payload.find(_MENU_CATEGORY_KEY)
        if start == -1:
            return None
        decoder = json.JSONDecoder()

        row_start = payload.rfind("\n", 0, start) + 1
        row_id, _, row = payload[row_start:].partition(":")
        raw_menu, _ = decoder.raw_decode(payload, start + len(_MENU_CATEGORY_KEY))
        return JDict(_resolve_rsc_refs(raw_menu, row_id, decoder.raw_decode(row)[0]))

    @staticmethod
    async def get_todays_menu() -> list[Dish] | None:
        """Get the menu for today"""
        async with aiohttp.ClientSession() as session, session.get(URL) as response:
            html = await response.text()
        raw_menu = Menu._extract_menu_category(html)
        if raw_menu is None:
            logging.getLogger("FoodstoffiMenu").error(
                "Could not find menu data on %s, did they change the page again? ._.",
                URL,
            )
            return None
        menu = Menu._from_dict(raw_menu)
        today_recipes = menu.todays_dishes
        if not today_recipes:
            return None
        if any("ferien" in x.title.lower() for x in today_recipes):
            return None
        return today_recipes


class SendFoodstoffiMenuTask:
    """Task to send the Foodstoffi menu"""

    def __init__(self, discord_bot: Stan) -> None:
        self._logger = logging.getLogger("FoodstoffiMenu")
        self._discord_bot = discord_bot

    async def start(self) -> None:
        """Start the task"""
        AioSchedule.run_daily_at(
            datetime.time(hour=8, minute=0),  # in UTC
            self.trigger,
        )

    async def trigger(self) -> None:
        """Send a foodstoffi menu update to all servers"""
        todays_menu = await Menu.get_todays_menu()
        if todays_menu is None:
            self._logger.warning("No menu available")
            return
        self._logger.debug("Sending today's menu to servers: %s", todays_menu)

        for server in self._discord_bot.servers.values():
            channel = server.get_announcement_channel(_ANNOUNCEMENT_TYPE)

            if channel is None:
                self._logger.warning("No channel found for server %s", server.guild)
                continue

            role = server.get_announcement_role(_ANNOUNCEMENT_TYPE)

            await PersonaSender(channel, _PERSONA).send(
                f"Hiya, {role.mention}! This is today's menu:",
                [x.as_embed for x in todays_menu],
            )
