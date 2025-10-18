<script setup lang="ts">
    const signin = () => (window.location.href = "/api/auth/signin");
</script>

<template>
    <div class="forbidden">
        <main>
            <div class="panel">
                <img
                    alt="Stair Logo"
                    class="logo"
                    src="/logo/stair.svg"
                    height="25"
                />
                <h1>Sign in</h1>
                <button @click="signin">
                    <span class="material-symbols-rounded">login</span>
                    Continue with Microsoft
                </button>
            </div>
        </main>
        <aside>
            <img
                class="stan"
                src="@/assets/img/default-hat.svg"
                type="image/svg+xml"
            />
        </aside>
    </div>
</template>

<style scoped>
    .forbidden {
        display: grid;
        grid-template-columns: 2fr 3fr;
        width: 100%;
        min-height: 100vh;
        min-height: 100svh;
        background: var(--c-white-1);
    }

    main {
        display: flex;
        justify-content: center;
        align-items: center;

        .panel {
            min-width: 300px;
            width: 60%;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 3em;

            & button {
                width: 100%;
            }
        }
    }

    aside {
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: var(--c-stair-graphite);

        .stan {
            max-height: 80vh;
        }
    }

    @media screen and (max-width: 1200px) {
        aside {
            display: none;
        }
        .forbidden {
            grid-template-columns: 1fr;
        }
    }
</style>
