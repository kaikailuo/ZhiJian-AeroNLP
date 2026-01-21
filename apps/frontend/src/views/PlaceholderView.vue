<template>
  <div class="page-shell">
    <aside class="side-panel">
      <h1>ZhiJian-AeroNLP</h1>
      <p>模块占位区</p>
      <nav class="nav-list">
        <router-link class="nav-item" to="/">总览</router-link>
        <router-link class="nav-item" to="/notam">NOTAM 中心</router-link>
        <router-link class="nav-item" to="/maps">地理情报</router-link>
        <router-link class="nav-item" to="/routes">航路规划</router-link>
        <router-link class="nav-item" to="/training">训练实验室</router-link>
        <router-link class="nav-item" to="/api-keys">API 密钥库</router-link>
      </nav>
    </aside>
    <main class="main-panel fade-in">
      <div class="card">
        <h2>{{ title }}</h2>
        <p>
          该模块已完成 MVP 骨架，API 接口契约已预留，后续将补齐完整功能。
        </p>
        <router-link to="/" class="badge">返回总览</router-link>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const title = computed(() => (route.meta.title as string) || "Module Placeholder");
</script>

<style scoped>
.nav-list {
  display: grid;
  gap: 10px;
  margin-top: 24px;
}

.nav-item {
  padding: 10px 14px;
  border-radius: 10px;
  color: rgba(223, 231, 255, 0.85);
  font-weight: 500;
}

.nav-item.router-link-active {
  background: rgba(26, 116, 255, 0.2);
  color: #ffffff;
}
</style>
