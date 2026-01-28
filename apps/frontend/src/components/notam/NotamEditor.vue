<template>
  <div 
    :class="editor"
    @dragover.prevent="isDragging = true"
    @dragleave.prevent="isDragging = false"
    @drop.prevent="handleDrop"
  >
  <transition name="fade">
    <div v-if="isDragging" :class="dropOverlay">
      <div :class="dropContent">
        <div :class="dropIcon">📂</div>
        <div :class="dropText">{{ pref.t('console.dropText') }}</div>
        <div :class="dropSub">{{ pref.t('console.dropSub') }}</div>
      </div>
    </div>
  </transition>

    <div :class="toolbar">
      <div :class="tabsGroup">
        <div :class="tabActive">{{ pref.t('console.manual') }}</div>
        <div :class="tabInactive">{{ pref.t('console.live') }} <span :class="betaTag">{{ pref.t('console.beta') }}</span></div>
      </div>
      
      <div :class="toolbarActions">
        <div :class="btnGroup">
          <button :class="actionBtn" type="button" @click="$emit(NotamEvents.CLEAR)" title="Clear All">
            {{ pref.t('action.clear') }}
          </button>
          <!-- <div :class="separator"></div> -->
          <button :class="actionBtn" type="button" @click="$emit(NotamEvents.LOAD_EXAMPLE)" title="Load Demo">
            {{ pref.t('action.loadExample') }}
          </button>
        </div>
      </div>
    </div>

    <div :class="textareaWrapper">
      <div :class="lineNumbers">
        <span v-for="n in 18" :key="n">{{ n }}</span>
      </div>
      <textarea
        :class="ideTextarea"
        :value="modelValue"
        :placeholder="pref.t('console.placeholder')"
        spellcheck="false"
        @input="handleInput"
        @keydown.enter.ctrl.prevent="handleShortcut"
      ></textarea>
    </div>

    <div :class="footer">
      <div :class="hint">
        <span>{{ pref.t('console.ln') }} {{ lineCount }}, {{ pref.t('console.col') }} {{ colCount }}</span>
        <span :class="divider">|</span>
        <span><b>Ctrl+Enter</b> {{ pref.t('console.runTip') }}</span>
      </div>

      <input
        type="file"
        ref="fileInputRef"
        style="display: none"
        accept=".txt,.json,.pdf,.xml"
        @change="handleFileSelect"
      />

      <div :class="footerActions">
        <button 
          :class="iconBtn" 
          type="button" 
          title="Upload File"
          @click="triggerUpload"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
          </svg>
        </button>

        <div :class="footerDivider"></div>

        <button :class="executeBtn" type="button" @click="emit(NotamEvents.EXECUTE)" :disabled="!engineReady || !modelValue.trim()">
          {{ pref.t('action.run') }}
        </button>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { css } from "@/styled-system/css";
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
  (e: typeof NotamEvents.CLEAR): void;
  (e: typeof NotamEvents.LOAD_EXAMPLE): void;
  (e: typeof NotamEvents.BATCH_UPLOAD, file: File): void;
}>();

const lineCount = computed(() => (props.modelValue ? props.modelValue.split("\n").length : 1));
const colCount = computed(() => (props.modelValue ? props.modelValue.length : 0));

const handleInput = (event: Event) => {
  const value = (event.target as HTMLTextAreaElement).value;
  emit(NotamEvents.UPDATE_MODEL, value);
};

const handleShortcut = () => {
  // 核心检查：只有当引擎就绪 且 内容不为空时，才允许执行
  if (props.engineReady && props.modelValue.trim()) {
    emit(NotamEvents.EXECUTE);
  }
};

// [新增] 拖拽逻辑
const isDragging = ref(false);

const handleDrop = (e: DragEvent) => {
  isDragging.value = false;
  if (e.dataTransfer?.files.length) {
    const file = e.dataTransfer.files[0];
    emit(NotamEvents.BATCH_UPLOAD, file);
  }
};

// [新增] 手动上传逻辑
const fileInputRef = ref<HTMLInputElement | null>(null);
const triggerUpload = () => {
  fileInputRef.value?.click();
};
const handleFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files.length > 0) {
    const file = input.files[0];
    emit(NotamEvents.BATCH_UPLOAD, file);
    // 清空 value，允许重复上传同一个文件
    input.value = "";
  }
};

const editor = css({
  height: "100%", // [修改] 跟随父容器高度
  // flexShrink: 0, // [删除] 交给父容器控制
  display: "flex",
  flexDirection: "column",
  bg: "surface.base",
  border: "1px solid token(colors.surface.outline)",
  borderRadius: "xl", // 统一用 xl (12px) 或 2xl (16px)
  overflow: "hidden",
  boxShadow: "0 4px 20px rgba(0, 0, 0, 0.05)"
});

// [新增] 拖拽覆盖层样式
const dropOverlay = css({
  position: "absolute", inset: "0", zIndex: "50",
  bg: "rgba(26, 116, 255, 0.05)", // 这里的颜色可以调整
  backdropFilter: "blur(4px)",
  display: "flex", alignItems: "center", justifyContent: "center",
  border: "2px dashed token(colors.brand.primary)",
  borderRadius: "xl",
  m: "2"
});
const dropContent = css({ textAlign: "center" });
const dropIcon = css({ fontSize: "48px", mb: "4" });
const dropText = css({ fontSize: "lg", fontWeight: "bold", color: "brand.primary" });
const dropSub = css({ fontSize: "sm", color: "surface.textDim" });

// [修改] 工具栏：浅灰色背景
const toolbar = css({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "flex-end", // [关键] 让 Tab 沉底
  bg: "surface.sunken",   // 顶部深色背景
  borderBottom: "1px solid token(colors.surface.outline)",
  h: "44px",
  px: "4",
  pt: "2"
});
const tabsGroup = css({
  display: "flex",
  height: "100%",
  gap: "8px", // 稍微拉开一点间距给反圆角留位置
  alignItems: "flex-end",
  pl: "2" // 左侧留白
});

// Chrome 风格 Tab 基础
const tabBase = {
  display: "flex", alignItems: "center", gap: "2",
  fontSize: "12px", px: "4", py: "2", cursor: "pointer",
  borderTopLeftRadius: "10px", // [关键] 顶部圆角
  borderTopRightRadius: "10px",
  transition: "background 0.1s, color 0.1s",
  height: "32px", // Tab 高度
  fontWeight: "500",
  position: "relative" as const, // 为了 z-index
  mb: "-1px" // [关键] 下沉 1px 盖住边框
};

// 激活态：白色背景，覆盖底边框
const tabActive = css({
  ...tabBase,
  color: "brand.primary",
  bg: "surface.base", // 本体背景色
  fontWeight: "600",
  zIndex: "10",
  
  // 核心样式：
  borderTopLeftRadius: "10px",
  borderTopRightRadius: "10px",
  
  height: "36px", // 稍微增高
  // [关键修复]
  // 1. 底部 margin 设为 -1px，让它物理下沉，盖住 toolbar 的边框
  mb: "-1px", 
  // 2. 增加 1px 的 padding-bottom 来补偿高度，保持文字垂直居中
  pb: "2px", 
  // 3. 显式设置底部边框颜色为【背景色】，像修正液一样涂掉下面的灰线
  borderBottom: "1px solid token(colors.surface.base)",
  
  // [关键魔法] 利用伪元素制造左右两侧的“反圆角裙边”
  _before: {
    content: '""',
    position: "absolute",
    bottom: "0px",
    left: "-10px", // 裙边宽度
    width: "10px",
    height: "10px",

    mb: "-2px", 
    // pb: "2px", 
    borderBottom: "1px solid token(colors.surface.base)",

    borderBottomRightRadius: "10px", // 裙边的圆角
    boxShadow: "5px 0 0 0 token(colors.surface.base)", // 用阴影模拟填充色
    zIndex: "1"
  },
  _after: {
    content: '""',
    position: "absolute",
    bottom: "0px",
    right: "-10px",
    width: "10px",
    height: "10px",

    mb: "-2px", 
    // pb: "2px", 
    borderBottom: "1px solid token(colors.surface.base)",

    borderBottomLeftRadius: "10px",
    boxShadow: "-5px 0 0 0 token(colors.surface.base)",
    zIndex: "1"
  },
  
  // 简单的顶部高亮条（可选，Chrome 其实没有，但很多类 Chrome UI 有）
  // 如果想要纯粹 Chrome 风格，可以删掉这个 _hover 或者是上面的 color 设置
});

// 未激活态：稍微透明，没有边框
const tabInactive = css({
  ...tabBase,
  color: "surface.textDim",
  bg: "transparent",
  mb: "4px", // 非激活状态稍微矮一点
  pb: "0px",
  // borderTopLeftRadius: "8px",
  // borderTopRightRadius: "8px",
  borderRightRadius: "8px",
  borderLeftRadius: "8px",
  _hover: { 
    bg: "rgba(0,0,0,0.05)",
    color: "surface.text" 
  }
});

const betaTag = css({ 
  fontSize: "9px", 
  bg: "rgba(26, 116, 255, 0.1)", 
  color: "brand.primary", 
  px: "1.5", 
  borderRadius: "sm", 
  fontWeight: "bold" 
});

const toolbarActions = css({ 
  display: "flex", 
  alignItems: "center", 
  pb: "6px" // 稍微居中一点
});

// [修复] 按钮组：放弃 group 容器，改为独立按钮容器
const btnGroup = css({
  display: "flex",
  alignItems: "center",
  gap: "8px" // 按钮分开
});

// [修复] 独立按钮样式：看得见的圆角
const actionBtn = css({
  bg: "surface.base", // 白色背景
  color: "surface.textDim",
  fontSize: "11px",
  fontWeight: "600",
  px: "3",
  py: "1",
  borderRadius: "md", // [关键] 明显的圆角
  border: "1px solid token(colors.surface.outline)", // 淡淡的描边
  cursor: "pointer",
  transition: "all 0.2s",
  boxShadow: "0 1px 2px rgba(0,0,0,0.02)",
  _hover: { 
    color: "brand.primary", 
    borderColor: "brand.primary",
    transform: "translateY(-1px)",
    boxShadow: "0 2px 4px rgba(26, 116, 255, 0.15)"
  }
});

// const separator = css({ w: "1px", h: "12px", bg: "surface.outline" });

// [修改] 编辑器区域
const textareaWrapper = css({ 
  flex: "1", 
  display: "flex", 
  overflow: "hidden", 
  bg: "surface.base" // 确保背景连贯
});

const lineNumbers = css({
  w: "48px",
  bg: "surface.base",
  color: "surface.textDim",
  fontSize: "13px",
  fontFamily: "mono",
  textAlign: "right",
  pt: "5",
  pr: "3",
  userSelect: "none",
  display: "flex",
  flexDirection: "column",
  gap: "1",
  opacity: 0.6,
  lineHeight: "1.6"
});

const ideTextarea = css({
  flex: "1",
  w: "100%",
  h: "100%",
  bg: "transparent",
  color: "surface.text",
  border: "none",
  resize: "none",
  p: "5",
  fontFamily: "mono",
  fontSize: "13px",
  lineHeight: "1.6",
  outline: "none",
  _placeholder: { color: "surface.textDim", opacity: 0.5 }
});

// [修改] 底部栏：增加留白，解决贴边问题
const footer = css({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  px: "4", // [修改] 左右大留白
  py: "2", // [修改] 上下大留白
  bg: "surface.sunken",
  borderTop: "1px solid token(colors.surface.outline)",
});
// (其他底部样式保持原有名词定义，只需适配颜色即可)
const hint = css({ fontSize: "11px", color: "surface.textDim", display: "flex", alignItems: "center", gap: "3" });
const divider = css({ color: "surface.outlineStrong" });

// [新增/修改] 底部右侧样式
const footerActions = css({ 
  display: "flex", 
  alignItems: "center", 
  gap: "3" 
});

const footerDivider = css({ 
  w: "1px", 
  h: "16px", 
  bg: "surface.outlineStrong" 
});

const iconBtn = css({
  display: "flex", alignItems: "center", justifyContent: "center",
  color: "surface.textDim",
  cursor: "pointer",
  p: "2",
  borderRadius: "lg",
  border: "none",       // [关键] 移除所有边框
  outline: "none",      // [关键] 移除点击时的黑框
  bg: "transparent",
  transition: "all 0.2s",
  _hover: { 
    color: "brand.primary", 
    bg: "rgba(0,0,0,0.05)",
    transform: "scale(1.1)" // 微微放大
  }
});

const executeBtn = css({
  bg: "brand.primary",
  color: "white",
  px: "5",
  py: "2",
  borderRadius: "lg", // 按钮圆角也加大
  fontWeight: "600",
  fontSize: "11px",
  cursor: "pointer",
  transition: "all 0.2s",
  boxShadow: "0 2px 8px rgba(26, 116, 255, 0.25)", // 增加投影
  _hover: { bg: "brand.hover", transform: "translateY(-1px)", boxShadow: "0 4px 12px rgba(26, 116, 255, 0.35)" },
  _active: { transform: "translateY(0)" },
  _disabled: { opacity: 0.5, cursor: "not-allowed", boxShadow: "none", transform: "none" }
});

</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
