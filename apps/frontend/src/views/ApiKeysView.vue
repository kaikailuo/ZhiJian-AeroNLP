<template>
  <div class="page-shell">
    <SideNav />

    <main class="main-panel fade-in">
      <header class="page-header">
        <div>
          <h2 class="page-title">API 密钥库</h2>
          <p class="page-sub">本地管理您的 AI 模型凭证，密钥仅存储在浏览器本地。</p>
        </div>
        <button :class="primaryBtn" @click="showModal = true">+ 录入新 Key</button>
      </header>

      <section :class="keysGrid">
        <KeyCard
          v-for="key in keyStore.keys"
          :key="key.id"
          :key-item="key"
          @delete="keyStore.removeKey"
        />

        <div v-if="keyStore.keys.length === 0" :class="emptyCard">
          暂无密钥，请点击右上角录入 DeepSeek 或 OpenAI Key 以开启解析功能。
        </div>
      </section>

      <CreateKeyModal
        :is-open="showModal"
        @close="showModal = false"
        @save="handleSave"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useKeyStore } from '@/stores/keyStore';
import KeyCard from '@/components/keys/KeyCard.vue';
import CreateKeyModal from '@/components/keys/CreateKeyModal.vue';
import SideNav from '@/components/layout/SideNav.vue';
import { css } from '@/styled-system/css';

const keyStore = useKeyStore();
const showModal = ref(false);

const handleSave = (payload: any) => {
  keyStore.addKey(payload);
  showModal.value = false;
};

const primaryBtn = css({
  bg: 'brand.primary',
  color: 'white',
  px: '4.5',
  py: '2.5',
  borderRadius: 'xl',
  border: 'none',
  fontWeight: '600',
  cursor: 'pointer',
  transition: 'transform 0.2s ease, box-shadow 0.2s ease',
  boxShadow: '0 12px 24px rgba(26, 116, 255, 0.2)',
  _hover: { transform: 'translateY(-1px)', boxShadow: '0 16px 30px rgba(26, 116, 255, 0.28)' }
});
const keysGrid = css({ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' });
const emptyCard = css({
  gridColumn: '1 / -1',
  textAlign: 'center',
  p: '7',
  borderRadius: '2xl',
  border: '1px dashed token(colors.surface.outline)',
  bg: 'surface.sunken',
  color: 'surface.textDim'
});
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--color-ink);
  margin: 0;
}

.page-sub {
  color: var(--color-slate);
  margin-top: 6px;
  font-size: 14px;
}

@media (max-width: 960px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
