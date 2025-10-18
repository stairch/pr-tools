<script setup lang="ts">
    import { RouterLink, RouterView } from "vue-router";
    import "@discord-message-components/vue/styles";
    import { ref, onMounted } from "vue";
    import Forbidden from "./views/Forbidden.vue";

    const userData = ref<any | null>(null);
    const showUserOptions = ref(false);

    onMounted(async () => {
        const res = await fetch("/api/auth/me");
        if (res.ok) {
            userData.value = await res.json();
        } else {
            userData.value = false;
        }

        document.body.addEventListener("click", () => {
            showUserOptions.value = false;
        });
    });
</script>

<template>
    <Forbidden v-if="userData == false" />
    <div
        id="body"
        v-else-if="userData"
    >
        <aside>
            <router-link to="/">
                <img
                    alt="Stair Logo"
                    class="logo"
                    src="/logo/pr.svg"
                    height="80"
                />
            </router-link>
            <nav>
                <RouterLink
                    title="Announcements"
                    to="/announcements"
                >
                    <span class="material-symbols-rounded">campaign</span>
                    <span class="name">Announcements</span>
                </RouterLink>
                <RouterLink
                    title="Manage Discord Users"
                    to="/discord/users"
                >
                    <span class="material-symbols-rounded">group</span>
                    <span class="name">Discord Users</span>
                </RouterLink>
                <RouterLink
                    title="Promotion Schedule"
                    to="/promotion-schedule"
                >
                    <span class="material-symbols-rounded">
                        calendar_month
                    </span>
                    <span class="name">Promotion Schedule</span>
                </RouterLink>
            </nav>
            <div
                @click.stop="showUserOptions = true"
                class="user"
            >
                <span>{{ userData.displayName }}</span>
                <div
                    @click.stop
                    class="options"
                    v-if="showUserOptions"
                >
                    <div class="action">
                        <a href="/api/auth/signout">
                            <span>Sign out</span>
                            <span class="material-symbols-rounded">logout</span>
                        </a>
                    </div>
                    <div class="data">
                        <h2>{{ userData.userPrincipalName }}</h2>
                        <p>{{ userData.mail }}</p>
                    </div>
                </div>
            </div>
        </aside>

        <div id="container">
            <RouterView />
        </div>
    </div>
</template>

<style scoped>
    #body {
        min-height: 100vh;
        min-height: 100svh;

        --sidebar-width: 270px;
        --sidebar-height: 0;

        display: grid;
        grid-template-columns: minmax(var(--sidebar-width), 350px) 1fr;
    }

    @media screen and (max-width: 768px) {
        #body {
            --sidebar-width: 0;
            --sidebar-height: 80px;
            display: block;

            aside {
                flex-direction: row;
                width: 100%;
                padding: 1em;
                height: var(--sidebar-height) !important;

                nav {
                    flex-direction: row;
                }

                a:has(img) {
                    display: none;
                }

                nav a {
                    justify-content: center;
                    aspect-ratio: 1 / 1;
                    padding: 0.5em;

                    & .name {
                        display: none;
                    }
                }
            }

            .user .options {
                bottom: auto;
                top: 100%;
                right: 0;
                left: auto;
            }
        }
    }

    aside {
        background: var(--bg-soft);
        border-right: 2px solid var(--bg-muted);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 2em;

        position: fixed;
        top: 0;
        left: 0;
        z-index: 1000;
    }

    nav {
        display: flex;
        flex-direction: column;
        font-size: 1rem;

        & a {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5em 1em;
            width: 100%;
            color: var(--fg-text-muted);
            border-radius: 0.25em;
            border: 1px solid transparent;

            &:hover {
                color: var(--c-accent);
                background: var(--bg-muted);
            }

            &.router-link-active {
                color: var(--fg-text);
                background: var(--bg-muted);
            }
        }
    }

    .user {
        cursor: pointer;
        position: relative;
        display: flex;
        align-items: center;
        padding: 0.5rem;

        &:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        .options {
            position: absolute;
            cursor: auto;
            bottom: 100%;
            left: 0;
            background: var(--bg-soft);
            border: 1px solid var(--bg-muted);
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
            border-radius: 0.5rem;
            padding: 1rem;
            display: flex;
            flex-direction: column;
            gap: 1em;
            color: var(--fg-text);

            .action {
                display: flex;
                justify-content: flex-end;
            }

            a {
                color: var(--fg-text);
                display: flex;
                align-items: center;
                padding: 0.5rem;
                text-align: center;
                text-decoration: none;

                &:hover {
                    color: var(--c-accent);
                    background: var(--bg-muted);
                    border-radius: 0.25em;
                }

                & span.material-symbols-rounded {
                    font-size: 1rem;
                    margin-left: 0.5em;
                }
            }

            .data {
                padding: 0 1rem;
            }
        }
    }

    #container {
        padding: 0;
        height: 100%;
        min-height: 100%;
        position: relative;
        overflow: clip;
        grid-column: 2;
        padding-top: var(--sidebar-height);
        width: 100%;
        max-width: calc(100svw - var(--sidebar-width));

        & > main {
            max-width: 1280px;
            width: 100%;
            padding: 2rem;
            overflow: auto;
            height: 100%;
            display: block;
        }
    }
</style>
