<template>
  <n-config-provider :theme-overrides="themeOverrides">
    <n-message-provider>
      <router-view />
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { NConfigProvider, NMessageProvider } from "naive-ui";

const themeOverrides = {
  common: {
    primaryColor: "#1a74ff",
    primaryColorHover: "#3b87ff",
    primaryColorPressed: "#0b5edb",
    infoColor: "#1a74ff",
    borderRadius: "10px",
    fontFamily: "'Space Grotesk', 'IBM Plex Sans', sans-serif",
  },
};
</script>
