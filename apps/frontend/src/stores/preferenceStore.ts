// src/stores/preferenceStore.ts
import { defineStore } from "pinia";
import { ref, computed, watch } from "vue";
import en from "@/locales/en";
import zh from "@/locales/zh";

// 类型定义，确保写代码时有自动补全提示
type LocaleKey = "zh" | "en";
type MessageSchema = typeof en;

export const usePreferenceStore = defineStore("preference", () => {
  // --- State ---
  // 从 localStorage 读取，如果没有则默认 'zh'
  const locale = ref<LocaleKey>((localStorage.getItem("app_locale") as LocaleKey) || "zh");
  const isDark = ref(localStorage.getItem("app_theme") === "dark");

  // --- Actions ---
  
  // 1. 切换语言
  const toggleLocale = () => {
    locale.value = locale.value === "zh" ? "en" : "zh";
    localStorage.setItem("app_locale", locale.value);
  };

  // 2. 切换主题
  const toggleTheme = () => {
    isDark.value = !isDark.value;
    updateThemeEffect();
  };

  // 应用主题副作用 (操作 DOM)
  const updateThemeEffect = () => {
    const html = document.documentElement;
    if (isDark.value) {
      // PandaCSS 默认监听 [data-panda-theme]
      html.setAttribute("data-panda-theme", "dark");
      
      // 同时也加上 class="dark" 以兼容某些依赖 class 的手写样式或 Tailwind 习惯
      html.classList.add("dark"); 
      localStorage.setItem("app_theme", "dark");
    } else {
      // 切换回 light 主题
      html.setAttribute("data-panda-theme", "light");
      
      html.classList.remove("dark");
      localStorage.setItem("app_theme", "light");
    }
  };

  // 初始化时应用一次
  updateThemeEffect();

  // --- I18n Engine (The "Standard" Way) ---
  const messages = { zh, en };

  // 这是一个极其精简但强大的翻译函数
  // 它支持 obj.path.to.key 的访问方式
  const t = (path: string) => {
    const keys = path.split(".");
    let current: any = messages[locale.value];
    
    for (const k of keys) {
      if (current && current[k]) {
        current = current[k];
      } else {
        return path; // 找不到 key 时直接返回 key 本身
      }
    }
    return current as string;
  };

  return {
    locale,
    isDark,
    toggleLocale,
    toggleTheme,
    t // 暴露出这个函数供组件使用
  };
});