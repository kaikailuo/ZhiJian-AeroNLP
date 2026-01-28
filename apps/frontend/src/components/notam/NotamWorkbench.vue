<template>
  <div :class="grid">
    <section :class="colLeft">
      <slot name="left" />
    </section>
    <section :class="colRight">
      <slot name="right" />
    </section>
  </div>
</template>

<script setup lang="ts">
import { css } from "@/styled-system/css";

const grid = css({
  display: "grid",
  gridTemplateColumns: "38% 1fr",
  gap: "6",
  flex: "1",
  height: "100%", // 确保占满 MainPanel
  minHeight: "0",
  overflow: "hidden", // 防止整个页面出现双滚动条
});

const colLeft = css({ 
  display: "flex", 
  flexDirection: "column", 
  overflow: "hidden", // [回滚] 恢复 hidden，禁止出现系统滚动条
  height: "100%",
  pr: "0", // 既然没有滚动条了，padding 也可以去掉
});
const colRight = css({ 
  display: "flex", 
  flexDirection: "column", 
  overflowY: "auto", // [关键] 整个右侧区域是滚动视窗
  overflowX: "hidden",
  height: "100%",
  pr: "2" // 优化滚动条体验
});
</script>
