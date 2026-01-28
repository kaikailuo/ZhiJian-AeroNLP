<template>
  <div class="page-shell">
    <SideNav />

    <main class="main-panel fade-in" :class="notamMain">
      <header :class="headerStyle">
        <div :class="titleGroup">
          <h2 :class="titleStyle">{{ pref.t("app.title") }}</h2>
          <p :class="subTitleStyle">{{ pref.t("app.subtitle") }}</p>
        </div>

        <div :class="controlIsland">
          <div :class="selectWrapper">
            <select v-model="selectedKeyId" :class="selectStyle">
              <option value="" disabled>
                -- {{ pref.t("action.selectEngine") }} --
              </option>
              <option v-for="k in keyStore.keys" :key="k.id" :value="k.id">
                {{ k.provider }} - {{ k.name }}
              </option>
            </select>
            <div :class="selectArrow">▼</div>
          </div>

          <div :class="divider"></div>

          <button
            :class="iconBtn"
            @click="pref.toggleTheme"
            :title="pref.t('action.toggleTheme')"
          >
            <svg
              v-if="!pref.isDark"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="12" cy="12" r="5"></circle>
              <line x1="12" y1="1" x2="12" y2="3"></line>
              <line x1="12" y1="21" x2="12" y2="23"></line>
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
              <line x1="1" y1="12" x2="3" y2="12"></line>
              <line x1="21" y1="12" x2="23" y2="12"></line>
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
            <svg
              v-else
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            </svg>
          </button>

          <button
            :class="langBtn"
            @click="pref.toggleLocale"
            :title="pref.t('action.switchLang')"
          >
            {{ pref.locale === "zh" ? "中" : "EN" }}
          </button>
        </div>
      </header>

      <NotamWorkbench>
        <template #left>
          <NotamInputConsole
            v-model="rawInput"
            :engine-ready="Boolean(selectedKeyId)"
            @execute="handleExecute"
            @load-example="loadExample"
          />
        </template>
        <template #right>
          <NotamStream />
        </template>
      </NotamWorkbench>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useKeyStore } from "@/stores/keyStore";
import { useNotamRunStore } from "@/stores/notamRunStore";
import { usePreferenceStore } from "@/stores/preferenceStore";
import { css } from "@/styled-system/css";
import SideNav from "@/components/layout/SideNav.vue";
import NotamWorkbench from "@/components/notam/NotamWorkbench.vue";
import NotamInputConsole from "@/components/notam/NotamInputConsole.vue";
import NotamStream from "@/components/notam/NotamStream.vue";

const keyStore = useKeyStore();
const notamRunStore = useNotamRunStore();
const pref = usePreferenceStore();
const rawInput = ref("");
const selectedKeyId = ref("");

if (keyStore.keys.length > 0) selectedKeyId.value = keyStore.keys[0].id;

const handleExecute = () => {
  if (!rawInput.value.trim()) return;
  const runId = notamRunStore.startRun(rawInput.value, selectedKeyId.value);
  notamRunStore.simulateRun(runId);
  rawInput.value = "";
  notamRunStore.updateGrounding("");
};

const loadExample = () => {
  rawInput.value = `(A0123/24 NOTAMN
Q) ZBPE/QRTCA/IV/BO/W/000/197/3956N11623E025
A) ZBPE B) 2402010000 C) 2402152359
D) DAILY 0000-0400 0800-1200
E) TEMPORARY RESTRICTED AREA ESTABLISHED BOUNDED BY:
395624N1162312E-395812N1162530E-400122N1162215E-
395910N1161845E-395624N1162312E.
VERTICAL LIMITS: GND UP TO FL197.
TYPE OF RESTRICTION: MILITARY EXERCISE.
F) GND G) FL197)`;
};

const notamMain = css({
  height: "100vh",
  display: "flex",
  flexDirection: "column",
  overflow: "hidden",
  boxSizing: "border-box",
  bg: "surface.base",
  transition: "background 0.3s, color 0.3s",
});
const headerStyle = css({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  h: "56px", // [修改] 锁定高度，不再由内容撑开
  flexShrink: 0, // [关键] 防止被压缩
  mb: "4",
  px: "2",
});
const titleGroup = css({
  display: "flex",
  flexDirection: "column", // 垂直排列
  justifyContent: "center", // 垂直居中
  alignItems: "flex-start", // 左对齐
  gap: "0" // [关键] 移除间距，让副标题紧贴
});

const titleStyle = css({ 
  fontSize: "lg", 
  fontWeight: "bold", 
  color: "surface.text",
  letterSpacing: "tight",
  lineHeight: "0" // 紧凑行高
});
const subTitleStyle = css({ 
  color: "surface.textDim", 
  fontSize: "xs",
  fontFamily: "mono",
  opacity: 0.8,
  lineHeight: "0"
});
const controlIsland = css({
  display: "flex",
  alignItems: "center",
  gap: "3",
  bg: "surface.sunken",
  p: "1",
  borderRadius: "lg",
  border: "1px solid token(colors.surface.outline)",
});
const selectWrapper = css({
  position: "relative",
  display: "flex",
  alignItems: "center",
});
const selectStyle = css({
  appearance: "none",
  bg: "surface.sunken", // [修改] 给 Select 一个显式背景
  color: "surface.text",
  pl: "2.5", pr: "6", py: "1",
  borderRadius: "sm",
  fontSize: "xs",
  fontWeight: "500",
  cursor: "pointer",
  outline: "none",
  minWidth: "140px",
  border: "1px solid transparent", // 预留边框位置
  transition: "background 0.2s",
  _hover: { bg: "rgba(0,0,0,0.05)" },
  _focus: { ring: "1px solid token(colors.brand.primary)" },
  
  // [新增] 修复下拉选项在深色模式下的背景
  "& option": {
    bg: "surface.base", // 使用 Token 背景色
    color: "surface.text"
  }
});
const selectArrow = css({
  position: "absolute",
  right: "3",
  top: "50%",
  transform: "translateY(-50%)",
  fontSize: "10px",
  color: "surface.textDim",
  pointerEvents: "none",
});
const divider = css({ w: "1px", h: "16px", bg: "surface.outlineStrong" });
const iconBtn = css({
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  w: "32px",
  h: "32px",
  borderRadius: "md",
  bg: "transparent", // 透明
  border: "none",    // 无边框
  color: "surface.textDim",
  cursor: "pointer",
  transition: "all 0.2s",
  _hover: { 
    bg: "surface.sunken", // Hover 时显示淡背景
    color: "brand.primary", 
    transform: "scale(1.05)"
  },
  _active: { transform: "scale(0.95)" }
});
const langBtn = css({
  fontSize: "xs", fontWeight: "bold", color: "surface.text",
  px: "0", w: "30px", h: "30px", // 正方形/圆形
  display: "flex", alignItems: "center", justifyContent: "center",
  borderRadius: "full", 
  cursor: "pointer", 
  bg: "transparent",
  border: "none",
  transition: "all 0.2s",
  fontFamily: "mono",
  _hover: { 
    bg: "surface.sunken", 
    color: "brand.primary",
    transform: "scale(1.05)"
  },
  _active: { transform: "scale(0.95)" }
});
</script>

<style>
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--colors-surface-outline-strong); /* 使用 Panda Token */
  border-radius: 9999px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--colors-surface-text-dim);
}

/* 兼容 Firefox */
* {
  scrollbar-width: thin;
  scrollbar-color: var(--colors-surface-outline-strong) transparent;
}
</style>