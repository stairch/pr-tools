<script setup lang="ts">
    import {
        computed,
        onMounted,
        onUnmounted,
        ref,
        watch,
        type PropType,
    } from "vue";
    import { api, type IAnnouncement } from "@/api";
    import router from "@/router";
    import MultiFileMonaco from "@/components/MultiFileMonaco.vue";
    import HelpModal from "./HelpModal.vue";

    const props = defineProps({
        modelValue: { type: Object as PropType<IAnnouncement>, required: true },
    });

    const openLanguage = ref<string | null>(null);
    const helpModal = ref<InstanceType<typeof HelpModal> | null>(null);
    const announcement = ref<IAnnouncement>(
        JSON.parse(JSON.stringify(props.modelValue))
    );
    const canTranslate = computed(() => {
        return (
            openLanguage.value &&
            Object.values(announcement.value.message).some((v) => v) &&
            !(announcement.value.message as any)[openLanguage.value]
        );
    });

    const translateWithDeepl = async () => {
        if (!canTranslate.value) return;

        const fromLanguage = Object.keys(announcement.value.message).find(
            (key) =>
                (announcement.value.message as any)[key] &&
                key !== openLanguage.value
        )!;
        const toLanguage = openLanguage.value;
        const text = (announcement.value.message as any)[fromLanguage];

        window.open(
            `https://www.deepl.com/translator#${fromLanguage}/${toLanguage}/${encodeURIComponent(
                text
            )}`,
            "_blank"
        );
    };

    watch(
        () => props.modelValue,
        (value) => {
            announcement.value = JSON.parse(JSON.stringify(value));
        },
        { deep: true }
    );

    const emit = defineEmits(["update:modelValue"]);

    const save = async () => {
        let result;

        if (announcement.value.id) {
            result = await api.announements.update(announcement.value);
        } else {
            result = await api.announements.create(announcement.value);
            router.push(`/announcements/${result.id}`);
        }
        emit("update:modelValue", result);
    };

    const saveDisabled = computed(() => {
        return (
            JSON.stringify(announcement.value) ===
            JSON.stringify(props.modelValue)
        );
    });

    const deleteAnnouncement = async () => {
        if (announcement.value.id) {
            await api.announements.delete(announcement.value.id);
            router.push("/announcements");
        }
    };

    const onKeydown = (event: KeyboardEvent) => {
        // Save on Ctrl + S
        if (event.key === "s" && (event.ctrlKey || event.metaKey)) {
            event.preventDefault();
            save();
        }
    };

    onMounted(() => {
        window.addEventListener("keydown", onKeydown);
    });
    onUnmounted(() => {
        window.removeEventListener("keydown", onKeydown);
    });
</script>

<template>
    <HelpModal ref="helpModal" />
    <div class="title-and-delete">
        <input
            type="text"
            v-model="announcement.title"
            placeholder="Title"
        />
        <button
            @click="deleteAnnouncement"
            class="secondary danger small"
            :disabled="!announcement.id"
        >
            <span class="material-symbols-rounded">delete</span>
            Delete
        </button>
    </div>
    <MultiFileMonaco
        v-model="announcement.message"
        :filenames="{ de: 'German Content', en: 'English Content' }"
        offers-help
        @switch-tab="openLanguage = $event"
        @help="helpModal?.open"
    />
    <div class="actions">
        <button
            @click="translateWithDeepl"
            class="primary"
            v-if="canTranslate"
        >
            Translate with Deepl
        </button>
        <button
            @click="save"
            :disabled="saveDisabled"
        >
            {{ announcement.id ? "Save" : "Create" }}
        </button>
    </div>
</template>

<style scoped>
    .announcement {
        display: grid;
        grid-template-columns: 25ch 1fr;
        align-items: start;
        gap: 1em;
    }

    .title-and-delete {
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 1em;
        align-items: center;
    }

    main {
        display: flex;
        flex-direction: column;
        gap: 1em;
    }

    aside {
        background-color: var(--bg-soft);
        border: 1px solid var(--bg-muted);
        border-radius: 0.5em;
    }

    .server {
        display: flex;
        align-items: center;
        padding: 1em;
        gap: 1em;
        border-radius: 0.5em;

        &.selected {
            background-color: var(--bg-muted);
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
</style>
