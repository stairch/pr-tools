<script setup lang="ts">
    import * as monaco from "monaco-editor";
    import { onMounted, onUnmounted, ref, watch } from "vue";
    import { initialiseMonacoCommands } from "@/monaco/commands";

    const props = defineProps({
        language: {
            type: String,
            default: "md",
        },
        modelValue: {
            type: String,
            default: "",
        },
        value: {
            type: String,
            default: "",
        },
        readOnly: {
            type: Boolean,
            default: false,
        },
    });

    const emit = defineEmits(["update:modelValue"]);

    let editor: monaco.editor.IStandaloneCodeEditor;
    const container = ref<HTMLDivElement>();
    let latestValue = props.modelValue;

    const prefersDark = window.matchMedia(
        "(prefers-color-scheme: dark)"
    ).matches;

    onMounted(() => {
        editor = monaco.editor.create(container.value!, {
            value: props.modelValue,
            language: props.language,
            readOnly: props.readOnly,
            scrollBeyondLastLine: false,
            wordWrap: "on",
            theme: prefersDark ? "vs-dark" : "vs",
        });
        editor.getModel()?.onDidChangeContent(() => {
            latestValue = editor.getValue();
            emit("update:modelValue", latestValue);
        });

        initialiseMonacoCommands(editor);
    });

    onUnmounted(() => {
        editor.dispose();
    });

    const updateEditor = (value: string) => {
        if (editor) {
            if (value !== latestValue) {
                latestValue = value;
                editor.setValue(value);
            }
        }
    };

    watch(() => props.value, updateEditor);
    watch(() => props.modelValue, updateEditor);
</script>

<template>
    <div
        ref="container"
        style="height: 100%"
    ></div>
</template>

<style scoped>
    div {
        min-height: calc(10 * 19px);
    }

    @media screen and (max-width: 600px) {
        div {
            min-height: calc(20 * 19px);
        }
    }
</style>
