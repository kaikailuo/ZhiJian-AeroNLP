<template>
  <div :class="container">
    <div :class="headerBar" @click="toggle">
      <div :class="iconWrapper">
        <div v-if="isThinking" :class="spinner"></div>
        <n-icon
          v-else-if="isDone"
          :class="doneIcon"
          :component="CheckmarkCircle16Filled"
        />
        <n-icon v-else :class="idleIcon" :component="Sparkle16Regular" />
      </div>

      <div :class="summaryContent">
        <template v-if="isThinking && lastLog">
          <span :class="cx(badgeBase, agentStyles[lastLog.agent])">{{
            lastLog.agent
          }}</span>
          <span :class="typingText">{{
            lastLog.content || pref.t('reasoningDrawer.idleThinking')
          }}</span>
        </template>

        <template v-else-if="isDone">
          <span :class="finishedText"
            >{{ pref.t('reasoningDrawer.finished') }} 
            ({{
              model.thoughts.length
            }}
            {{ pref.t('reasoningDrawer.ops') }})</span
          >
        </template>

        <template v-else>
          <span :class="idleText">{{ pref.t('reasoningDrawer.idle') }}</span>
        </template>
      </div>

      <n-icon :size="14" :class="arrowIcon(isOpen)">
        <ChevronDown16Regular />
      </n-icon>
    </div>

    <n-collapse-transition :show="isOpen">
      <div :class="detailBody">
        <div v-for="log in model.thoughts" :key="log.id" :class="logRow">
          <div :class="logAgentCol">
            <span :class="agentTag(log.agent)">{{ log.agent }}</span>
            <div :class="timelineLine"></div>
          </div>
          <div :class="logContent">
            {{ log.content }}
            <span v-if="log.isStreaming" :class="cursor">_</span>
          </div>
        </div>
      </div>
    </n-collapse-transition>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { NIcon, NCollapseTransition } from "naive-ui";
import {
  ChevronDown16Regular,
  Sparkle16Regular,
  CheckmarkCircle16Filled,
} from "@vicons/fluent";
import { css, cx } from "@/styled-system/css"; // [新增] 引入 cx
import { type NotamCardModel, type AgentType, NotamStage } from "@/models/NotamCard";
import { usePreferenceStore } from '@/stores/preferenceStore';

const pref = usePreferenceStore();
const props = defineProps<{ model: NotamCardModel }>();
const isOpen = ref(false);
const toggle = () => (isOpen.value = !isOpen.value);

const isThinkingStage: readonly NotamStage[] =  
  [NotamStage.CONNECTING, NotamStage.DISCOVERING, NotamStage.ANALYZING, NotamStage.VALIDATING] as const;

const isThinking = computed(() => 
  isThinkingStage.includes(props.model.stage)
);
const isDone = computed(() => props.model.stage === NotamStage.FINALIZED);
const lastLog = computed(() => {
  const len = props.model.thoughts.length;
  return len > 0 ? props.model.thoughts[len - 1] : null;
});

// --- Styles ---

// [新增] 1. 基础 Badge 样式
const badgeBase = css({
  fontSize: "12px",
  fontWeight: "bold",
  px: "1.5",
  borderRadius: "sm",
  flexShrink: 0,
});

// [新增] 2. 静态颜色映射 (使用旧版 hex 确保颜色一致)
// PandaCSS 能扫描到这些静态 css() 调用，从而正确生成类名
const agentStyles: Record<string, string> = {
  DISCOVERY: css({ bg: "rgba(26, 116, 255, 0.1)", color: "#1a74ff" }), // Blue
  ANALYST: css({ bg: "rgba(168, 85, 247, 0.1)", color: "#a855f7" }), // Purple
  VALIDATOR: css({ bg: "rgba(16, 185, 129, 0.1)", color: "#10b981" }), // Green
};

// [修改] 详情列表里的 Tag 样式逻辑
const agentTag = (agent: AgentType) =>
  css({
    fontSize: "12px",
    fontWeight: "bold",
    // 这里如果是纯文本颜色，可以直接用 ternary，因为 css 属性值支持简单条件
    // 但为了保险，建议也用映射，或者直接硬编码 color
    color:
      agent === "DISCOVERY"
        ? "#1a74ff"
        : agent === "ANALYST"
          ? "#a855f7"
          : "#10b981",
    opacity: 0.9,
    textAlign: "right",
  });

// ... (其他样式保持不变) ...
const container = css({
  mt: "2",
  borderRadius: "md",
  overflow: "hidden",
  bg: "surface.sunken",
  border: "1px solid transparent",
  transition: "border-color 0.2s",
  _hover: { borderColor: "token(colors.surface.outlineStrong)" },
});
const headerBar = css({
  display: "flex",
  alignItems: "center",
  gap: "2",
  px: "2.5",
  py: "2",
  cursor: "pointer",
  userSelect: "none",
});
const iconWrapper = css({
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  w: "16px",
  h: "16px",
  flexShrink: 0,
});
const spinner = css({
  w: "12px",
  h: "12px",
  borderRadius: "50%",
  border: "2px solid token(colors.brand.primary)",
  borderTopColor: "transparent",
  animation: "spin 0.8s linear infinite",
});
const doneIcon = css({ color: "status.active" });
const idleIcon = css({ color: "surface.textDim" });
const summaryContent = css({
  flex: 1,
  display: "flex",
  alignItems: "center",
  gap: "2",
  overflow: "hidden",
  whiteSpace: "nowrap",
});
const typingText = css({
  fontSize: "11px",
  color: "surface.text",
  overflow: "hidden",
  textOverflow: "ellipsis",
  flex: 1,
});
const finishedText = css({ fontSize: "11px", color: "surface.textDim" });
const idleText = css({
  fontSize: "11px",
  color: "surface.textDim",
  fontStyle: "italic",
});
const arrowIcon = (open: boolean) =>
  css({
    color: "surface.textDim",
    transition: "transform 0.2s",
    transform: open ? "rotate(180deg)" : "rotate(0deg)",
  });
const detailBody = css({
  borderTop: "1px solid token(colors.surface.outline)",
  p: "3",
  bg: "surface.canvas",
});
const logRow = css({
  display: "flex",
  gap: "3",
  mb: "2",
  fontSize: "11px",
  fontFamily: "mono",
  lineHeight: "1.5",
});
const logAgentCol = css({
  display: "flex",
  flexDirection: "column",
  alignItems: "flex-end",
  minWidth: "70px",
  gap: "1",
});
const timelineLine = css({
  w: "1px",
  flex: 1,
  bg: "surface.outline",
  my: "0.5",
});
const logContent = css({
  flex: 1,
  color: "surface.text",
  wordBreak: "break-word",
});
const cursor = css({ animation: "blink 1s infinite" });
</script>

<style scoped>
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
@keyframes blink {
  50% {
    opacity: 0;
  }
}
</style>
