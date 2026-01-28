<template>
  <aside class="side-panel">
    <h1>ZhiJian-AeroNLP</h1>
    <p>航行情报作战舱</p>
    <nav :class="navList">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        custom
        v-slot="{ navigate, href, isActive, isExactActive }"
      >
        <a
          :href="href"
          :class="cx(navItem, (isActive || isExactActive) && navItemActive)"
          @click="navigate"
          :aria-current="isActive || isExactActive ? 'page' : undefined"
        >
          {{ item.label }}
        </a>
      </RouterLink>
    </nav>
    <div v-if="showLogout" :class="sideFooter">
      <n-button tertiary block @click="handleLogout">退出登录</n-button>
    </div>
    <div :class="brand">
      <img :class="brandLogo" :src="logoUrl" alt="ZhiJian-AeroNLP logo" />
    </div>
  </aside>
</template>

<script setup lang="ts">
import { RouterLink, useRouter } from "vue-router";
import { NButton } from "naive-ui";
import { useAuthStore } from "@/stores/auth";
import logoUrl from "@/assets/logo.png";
import { css, cx } from "@/styled-system/css";

const props = withDefaults(defineProps<{ showLogout?: boolean }>(), {
  showLogout: true,
});

const router = useRouter();
const auth = useAuthStore();

const navItems = [
  { label: "总览", to: "/" },
  { label: "NOTAM 中心", to: "/notam" },
  { label: "地理情报", to: "/maps" },
  { label: "航路规划", to: "/routes" },
  { label: "训练实验室", to: "/training" },
  { label: "API 密钥库", to: "/api-keys" },
];

const handleLogout = async () => {
  await auth.logout();
  router.push({ name: "login" });
};

const navList = css({ display: "grid", gap: "10px", mt: "6" });
const navItem = css({
  px: "3.5",
  py: "2.5",
  borderRadius: "lg",
  color: "rgba(223, 231, 255, 0.85)",
  fontWeight: "500",
  transition: "background 0.2s ease, color 0.2s ease, box-shadow 0.2s ease",
  _hover: { bg: "rgba(26, 116, 255, 0.12)" },
});
const navItemActive = css({
  bg: "rgba(26, 116, 255, 0.22)",
  color: "white",
  boxShadow: "inset 0 0 0 1px rgba(26, 116, 255, 0.25)",
});
const sideFooter = css({
  mt: "8",
  borderRadius: "lg",
  bg: "surface.elevated",
  border: "1px solid token(colors.surface.outline)",
});
const brand = css({ display: "flex", alignItems: "center", justifyContent: "center", gap: "3" });
const brandLogo = css({
  width: "300px",
  height: "300px",
  objectFit: "contain",
  borderRadius: "18px",
  ml: "-16px",
});
</script>
