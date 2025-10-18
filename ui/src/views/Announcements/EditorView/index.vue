<script setup lang="ts">
    import { onMounted, ref, watch } from "vue";
    import { useRoute, useRouter } from "vue-router";
    import { api, type IAnnouncement } from "@/api";
    import Edit from "./Edit.vue";
    import Discord from "./Discord.vue";
    import Telegram from "./Telegram.vue";
    import { useAnnouncementStore } from "@/stores/announcements";
    import Instagram from "./Instagram.vue";
    import WhatsApp from "./WhatsApp.vue";
    import Schedule from "./Schedule.vue";

    const announcement = ref<IAnnouncement>({
        title: "",
        message: {
            en: "",
            de: "",
        },
    });

    const route = useRoute();
    const router = useRouter();
    const announcementStore = useAnnouncementStore();

    const TABS = [
        {
            name: "Edit",
            component: Edit,
            icon: "edit",
        },
        {
            name: "Discord",
            component: Discord,
            icon: "discord",
        },
        {
            name: "Telegram",
            component: Telegram,
            icon: "telegram",
        },
        {
            name: "Instagram",
            component: Instagram,
            icon: "instagram",
        },
        {
            name: "WhatsApp",
            component: WhatsApp,
            icon: "whatsapp",
        },
        {
            name: "Schedule",
            component: Schedule,
            icon: "schedule",
        },
    ];
    let requestTab = route.query.tab as string;
    const activeTab = ref<number>(0);
    activeTab.value = requestTab
        ? TABS.findIndex((x) => x.name === requestTab)
        : 0;

    watch(activeTab, (x) => {
        const query = { tab: TABS[x].name };
        router.replace({ query });
    });

    onMounted(async () => {
        const announcementId = Number(route.params.id);
        if (announcementId) {
            announcement.value = await api.announements.get(announcementId);
        }
    });

    watch(route, async () => {
        const announcementId = Number(route.params.id);
        if (announcementId) {
            announcement.value = await api.announements.get(announcementId);
        } else {
            announcement.value = {
                title: "",
                message: {
                    en: "",
                    de: "",
                },
            };
        }
    });
</script>

<template>
    <main>
        <router-link to="/announcements">
            <h1>Announcements</h1>
        </router-link>
        <div class="announcement">
            <div class="tab-list">
                <span
                    v-for="(tab, i) in TABS"
                    :class="{ active: i === activeTab }"
                >
                    <div
                        class="content"
                        @click="activeTab = i"
                    >
                        <i :class="'icon-' + tab.icon"></i>
                        {{ tab.name }}
                    </div>
                </span>
            </div>
            <component
                :is="TABS[activeTab].component"
                v-model="announcement"
            />
        </div>
    </main>
</template>

<style scoped>
    .announcement {
        display: flex;
        flex-direction: column;
        gap: 1em;
    }

    a h1:hover {
        text-decoration: underline;
    }

    aside {
        background-color: var(--bg-soft);
        border: 1px solid var(--bg-muted);
        border-radius: 0.5em;

        & a {
            color: inherit;
        }
    }

    .server {
        display: flex;
        align-items: center;
        padding: 1em;
        gap: 1em;
        border-radius: 0.5em;

        &.selected {
            background-color: var(--bg-muted);
            color: var(--c-accent);
        }

        & img {
            width: 2em;
            height: 2em;
            border-radius: 0.25em;
        }
    }

    .actions {
        display: flex;
        gap: 1em;
        justify-content: flex-end;
    }

    .tab-list {
        display: flex;
        overflow-x: auto;

        & span {
            padding: 0.5em;
            cursor: pointer;
            border-bottom: 1px solid var(--bg-muted);
            transition: all 0.2s;

            .content {
                min-width: max-content;
                display: flex;
                align-items: center;
                gap: 0.5em;
                padding: 0.5em 1.5em;
                border-radius: 0.5em;
            }

            &.active {
                border-bottom: 1px solid var(--c-accent);
            }

            &:hover {
                .content {
                    background-color: var(--bg-muted);
                    color: var(--c-accent);
                }
            }
        }
    }
</style>
