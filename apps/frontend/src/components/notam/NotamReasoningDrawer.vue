<template>
  <div :class="drawerWrap">
    <div :class="drawerHeader" @click="toggle">
      <div :class="drawerTitle">
        <span :class="iconStyle">{{ expanded ? "▼" : "▶" }}</span>
        <span>{{ title }}</span>
      </div>
      <span :class="countBadge">{{ items.length }} OPS</span>
    </div>
    <n-collapse-transition :show="expanded">
      <div :class="drawerBody">
        <div v-for="item in items" :key="item.id" :class="line">
          <span :class="agentTag(item.agent)">{{ item.agent }}</span>
          <span :class="text">
            {{ item.text }}
            <span v-if="item.isStreaming" :class="cursor">_</span>
          </span>
        </div>
      </div>
    </n-collapse-transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { css } from "@/styled-system/css";
// [新增] 引入 Naive UI 的折叠过渡组件
import { NCollapseTransition } from "naive-ui";
import { usePreferenceStore } from "@/stores/preferenceStore";
const pref = usePreferenceStore();

interface ReasoningItem {
  id: string;
  agent: string;
  text: string;
  isStreaming?: boolean;
}

const props = withDefaults(
  defineProps<{
    items: ReasoningItem[];
    defaultOpen?: boolean;
    isStreaming?: boolean;
    title?: string;
  }>(),
  {
    items: () => [],
    defaultOpen: false,
    isStreaming: false,
    title: "Reasoning Chain",
  }
);

const expanded = ref(props.defaultOpen);
const toggle = () => {
  expanded.value = !expanded.value;
};

// 如果有新的流进来，自动展开
watch(() => props.isStreaming, (newVal) => {
  if (newVal) expanded.value = true;
});

const drawerWrap = css({ borderTop: "1px solid token(colors.surface.outline)" });
// [修改] 头部样式：增加高度、内边距、字号，增加点击手感
const drawerHeader = css({
  p: "3 4", // 原为 "2 3"，增加内边距
  fontSize: "xs", // 原为 "10px"，调大字号
  height: "32px", // 固定高度，增加点击区域
  fontWeight: "600", // 加粗
  color: "surface.textDim",
  cursor: "pointer",
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  bg: "surface.sunken",
  // borderTop: "1px solid token(colors.surface.outline)",
  userSelect: "none", // 防止快速点击时选中文本
  transition: "background 0.2s",
  _hover: { bg: "rgba(0, 0, 0, 0.04)" } // 增加悬停反馈
});
// [新增] 箭头的样式，防止它忽大忽小
const iconStyle = css({
  display: "inline-block",
  width: "16px",
  textAlign: "center",
  mr: "1",
  fontSize: "10px"
});
const drawerTitle = css({ display: "flex", alignItems: "center", gap: "2" });
const countBadge = css({
  bg: "rgba(0,0,0,0.12)",
  px: "1.5",
  borderRadius: "sm",
  fontSize: "9px",
  mr: "2" // <--- [新增] 增加右侧间距
});// [修改] 内容体：增加内边距，解决文字贴边问题
const drawerBody = css({
  p: "4", // 原为 "3"，让内容呼吸感更强
  bg: "surface.sunken", // 保持深色背景
  borderTop: "1px solid rgba(0,0,0,0.06)", // 增加一条分割线
  display: "grid",
  gap: "3", // 原为 "2"，增加行间距
  maxHeight: "300px",
  overflowY: "auto",
  fontFamily: "mono" // 强制等宽
});
const line = css({ display: "flex", gap: "3", fontSize: "11px", fontFamily: "mono" });
const agentTag = (agent: string) =>
  css({
    color:
      agent === "DISCOVERY"
        ? "#1a74ff"
        : agent === "ANALYST"
        ? "#a855f7"
        : agent === "INPUT"
        ? "#64748b"
        : "#10b981",
    fontWeight: "bold",
    minWidth: "72px", // 稍微加宽
    textAlign: "right",
    fontSize: "10px", // 原为 9px
    lineHeight: "1.6",
    opacity: 0.9
  });
// [修改] 日志文本：增加行高，优化阅读体验
const text = css({
  color: "surface.textDim",
  // lineHeight: "1.6",
  wordBreak: "break-word"
});
const typingIndicator = css({ color: "surface.textDim", fontSize: "lg", lineHeight: "0.5", pl: "84px" });

// [新增] 光标样式
const cursor = css({
  display: "inline-block",
  color: "#22c55e",
  fontWeight: "bold",
  animation: "blink 1s step-end infinite"
});
</script>

<style scoped>
/* 强制加速折叠动画 (原默认约 0.3s) */
.n-collapse-transition {
  transition-duration: 0.15s !important;
}
.dot {
  display: inline-block;
  animation: blink 1.2s infinite;
}
.dot:nth-child(2) {
  animation-delay: 0.2s;
}
.dot:nth-child(3) {
  animation-delay: 0.4s;
}
@keyframes blink {
  0%, 80%, 100% { opacity: 0.3; }
  40% { opacity: 1; }
}
</style>
