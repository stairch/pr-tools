<script setup lang="ts">
    import { watch, ref, type PropType, onMounted } from "vue";
    import { toUnicodeVariant } from "@/assets/toUnicodeVariant";
    import Step from "@/components/Step.vue";
    import ToastNotification from "@/components/ToastNotification.vue";
    import type { IAnnouncement } from "@/api";

    const text = ref<string>("");
    const toast = ref<typeof ToastNotification>();

    const props = defineProps({
        modelValue: { type: Object as PropType<IAnnouncement>, required: true },
    });

    const buildText = () => {
        const fullText =
            props.modelValue.message.de +
            "\n\n---\n\n" +
            props.modelValue.message.en;

        // replace markdown with unicode

        // links are replaced by "Link in bio"
        const linkRegex =
            /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g;
        const linkReplacer = (match: string, p1: string, p2: string) => {
            return "**Link in bio**";
        };

        const hyperlinkText = fullText.replace(linkRegex, linkReplacer);

        // bold text is surrounded by * or **
        const boldRegex = /\*\*(.*?)\*\*|\*(.*?)\*/g;
        const boldReplacer = (match: string, ...groups: string[]) => {
            const p = groups.filter((g) => g)[0];
            return toUnicodeVariant(p, "bold sans");
        };
        const boldText = hyperlinkText.replace(boldRegex, boldReplacer);

        // italic text is surrounded by _ or __
        const italicRegex = /__(.*?)__|_(.*?)_/g;
        const italicReplacer = (match: string, ...groups: string[]) => {
            const p = groups.filter((g) => g)[0];
            return toUnicodeVariant(p, "italic sans");
        };
        const italicText = boldText.replace(italicRegex, italicReplacer);

        return italicText;
    };

    const copyToClipbaord = () => {
        navigator.clipboard.writeText(text.value);
        toast.value?.showToast({
            message: "Copied to Clipboard!",
            style: "success",
            icon: "done",
        });
    };

    onMounted(async () => {
        text.value = buildText();
    });

    watch(
        () => props.modelValue,
        () => {
            text.value = buildText();
        },
        { deep: true }
    );
</script>

<template>
    <ToastNotification ref="toast" />
    <div class="checklist">
        <h2>Checklist</h2>
        <div class="checklist">
            <Step
                title="Add Location"
                description="Where is the Event going to be?"
            />
            <Step
                title="Add Reminder"
                description="People will be able to set a reminder for the Event."
            />
            <Step
                title="Tag Accounts (optional)"
                description="For example @schafluzern"
            />
            <Step
                title="Post!"
                description="You're ready to go!"
            />
            <Step
                title="Share to Story"
                description="Share to your Instagram Story."
            />
        </div>
    </div>
    <h2>Caption</h2>
    <div class="textarea">
        <textarea
            class="instagram"
            v-model="text"
        ></textarea>
        <span
            class="material-symbols-rounded"
            @click="copyToClipbaord"
            title="Copy All"
        >
            content_copy
        </span>
    </div>
</template>

<style scoped>
    textarea.instagram {
        height: 50ch;
        width: 100%;
    }

    .checklist {
        display: flex;
        flex-direction: column;
        gap: 1em;
    }

    .textarea {
        position: relative;
        width: 100%;

        .material-symbols-rounded {
            position: absolute;
            right: 0.5em;
            top: 0.5em;
            cursor: pointer;
            background: var(--bg-base);
            padding: 0.25em;
            font-size: 1.8em;
            border: 1px solid var(--bg-muted);
            border-radius: 0.25em;

            &:hover {
                color: var(--c-accent);
                border-color: var(--c-accent);
            }
        }
    }
</style>
