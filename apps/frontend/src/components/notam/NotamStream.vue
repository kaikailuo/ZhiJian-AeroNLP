<template>
  <div :class="streamContainer">
    <div :class="header">
      <h3 :class="title">{{ pref.t('stream.title') }}</h3>
      <div v-if="runningCount > 0" :class="statusBadge">
        {{ pref.t('stream.processing') }} {{ runningCount }} {{ pref.t('stream.tasks') }}
      </div>
    </div>

    <div :class="scrollArea">
      <div v-if="store.cards.length === 0" :class="emptyState">
        <div :class="emptyIcon">📡</div>
        <p>{{ pref.t('stream.standby') }}</p>
      </div>

      <div v-else :class="cardList">
        <NotamSmartCard 
          v-for="card in store.cards" 
          :key="card.id"
          :notam="card"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { css } from '@/styled-system/css';
import { useNotamRunStore } from '@/stores/notamRunStore';
import { usePreferenceStore } from '@/stores/preferenceStore';
import NotamSmartCard from './NotamSmartCard.vue';

const store = useNotamRunStore();
const pref = usePreferenceStore();

const runningCount = computed(() => {
  return store.cards.filter(c => c.stage !== 'finalized' && c.stage !== 'failed').length;
});

// Styles
const streamContainer = css({
  h: '100%', display: 'flex', flexDirection: 'column',
  bg: 'surface.canvas', // 使用 Canvas 背景色
  borderLeft: '1px solid token(colors.surface.outline)'
});

const header = css({
  h: '40px', px: '4', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
  borderBottom: '1px solid token(colors.surface.outline)', bg: 'surface.base'
});

const title = css({ fontSize: 'xs', fontWeight: 'bold', color: 'surface.textDim', letterSpacing: 'wider' });

const statusBadge = (stage: string) => css({
  fontSize: '10px', fontWeight: 'bold', px: '2', py: '0.5', borderRadius: 'sm',
  bg: stage === 'finalized' ? 'status.active' : 'status.info',
  color: 'surface.base' // 文字反白
});

const scrollArea = css({ flex: 1, overflowY: 'auto', p: '4' });

const emptyState = css({
  h: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
  color: 'surface.textDim', opacity: 0.6
});
const emptyIcon = css({ fontSize: '32px', mb: '2' });

const cardList = css({ display: 'flex', flexDirection: 'column', gap: '0' });
</script>

<style scoped>
@keyframes spin { 100% { transform: rotate(360deg); } }
</style>