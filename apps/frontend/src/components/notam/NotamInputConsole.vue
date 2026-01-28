<template>
  <section :class="section" ref="containerRef">
    <div :class="panelTitle">{{ pref.t('console.title') }}</div>
    
    <div :class="topPane" :style="{ height: `${splitRatio * 100}%` }">
      <NotamEditor
        v-model="rawText"
        :engine-ready="engineReady"
        @execute="emitExecute"
        @clear="handleClear"
        @load-example="emitLoadExample"
        @batch-upload="handleBatchUpload"
      />
    </div>

    <div 
      :class="resizer" 
      @mousedown.prevent="startDrag"
    >
      <div :class="resizerHandle"></div>
    </div>

    <div :class="bottomPane" :style="{ height: `${(1 - splitRatio) * 100}%` }">
      <NotamRadar />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, watch, ref, onUnmounted } from "vue";
import { css } from "@/styled-system/css";
import { useNotamRunStore } from "@/stores/notamRunStore";
import NotamEditor from "@/components/notam/NotamEditor.vue";
import NotamRadar from "@/components/notam/NotamRadar.vue";
import { NotamEvents } from "@/constants/events";
import { usePreferenceStore } from "@/stores/preferenceStore";
const pref = usePreferenceStore();

const props = defineProps<{
  modelValue: string;
  engineReady: boolean;
}>();

const emit = defineEmits<{
  (e: typeof NotamEvents.UPDATE_MODEL, value: string): void;
  (e: typeof NotamEvents.EXECUTE): void;
  (e: typeof NotamEvents.LOAD_EXAMPLE): void;
}>();

const notamRunStore = useNotamRunStore();

const rawText = computed({
  get: () => props.modelValue,
  set: (value: string) => emit(NotamEvents.UPDATE_MODEL, value),
});

const handleClear = () => {
  emit(NotamEvents.UPDATE_MODEL, "");
  notamRunStore.updateGrounding("");
};

const emitExecute = () => emit(NotamEvents.EXECUTE);
const emitLoadExample = () => emit(NotamEvents.LOAD_EXAMPLE);

watch(
  () => rawText.value,
  (value) => {
    // console.log("[Console] Input change:", value); // 调试用
    notamRunStore.updateGrounding(value);
  },
  { immediate: true } // [新增] 确保组件加载时如果有默认值也能触发
);

const handleBatchUpload = (file: File) => {
  // 模拟读取文件：在实际应用中这里应该用 FileReader 读取内容
  // 这里我们直接启动一个模拟的 Batch Run
  const runId = notamRunStore.startRun(
    `[BATCH IMPORT] ${file.name}`, 
    props.engineReady ? "default" : undefined, 
    "batch", 
    { filename: file.name, total: 42 } // 模拟 42 个文件
  );
  
  notamRunStore.simulateBatchRun(runId);
};

// --- Resizer Logic ---
const containerRef = ref<HTMLElement | null>(null);
const splitRatio = ref(0.6); // 默认 Editor 占 60%
const isDragging = ref(false);

const startDrag = () => {
  isDragging.value = true;
  window.addEventListener("mousemove", onDrag);
  window.addEventListener("mouseup", stopDrag);
  document.body.style.cursor = "row-resize";
  document.body.style.userSelect = "none"; // 防止拖拽时选中文字
};

const onDrag = (e: MouseEvent) => {
  if (!containerRef.value) return;
  const rect = containerRef.value.getBoundingClientRect();
  const offsetY = e.clientY - rect.top;
  // 限制拖拽范围在 20% - 80% 之间
  const newRatio = Math.max(0.2, Math.min(0.8, offsetY / rect.height));
  splitRatio.value = newRatio;
};

const stopDrag = () => {
  isDragging.value = false;
  window.removeEventListener("mousemove", onDrag);
  window.removeEventListener("mouseup", stopDrag);
  document.body.style.cursor = "";
  document.body.style.userSelect = "";
};

onUnmounted(() => {
  window.removeEventListener("mousemove", onDrag);
  window.removeEventListener("mouseup", stopDrag);
});

// --- Styles ---

const section = css({ 
  display: "flex", 
  flexDirection: "column", 
  height: "100%", // 占满左侧栏高度
  overflow: "hidden", // 内部无滚动
  position: "relative"
});

const panelTitle = css({ 
  color: "surface.textDim", 
  fontSize: "10px", 
  fontWeight: "bold", 
  letterSpacing: "1px", 
  mb: "2",
  flexShrink: 0 
});

const topPane = css({
  overflow: "hidden",
  minHeight: "100px", // 最小保护高度
  pb: "2" // 给 Resizer 留一点间隙
});

const bottomPane = css({
  overflow: "hidden",
  minHeight: "100px",
  pt: "2"
});

const resizer = css({
  height: "12px", // 增加热区高度，方便抓取
  margin: "-6px 0", // 负 margin 抵消高度，使其不占用视觉布局空间
  cursor: "row-resize",
  zIndex: "10",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  transition: "all 0.2s",
  _hover: {
    "& > div": { bg: "brand.primary", width: "40px", height: "4px" } // Hover 时变宽变亮
  }
});

const resizerHandle = css({
  width: "24px",
  height: "3px",
  bg: "surface.outlineStrong",
  borderRadius: "full",
  transition: "all 0.2s"
});
</script>
