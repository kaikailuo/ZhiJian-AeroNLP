<template>
  <div :class="container">
    <button @click="isOpen = !isOpen" :class="toggleBtn">
      <span>{{ pref.t('reasoningDrawer.showRawText') }}</span>
      <n-icon :size="12" :class="iconStyle(isOpen)">
        <ChevronDown16Regular />
      </n-icon>
    </button>
    
    <n-collapse-transition :show="isOpen">
      <div :class="contentBox">
        <pre :class="preText">{{ text }}</pre>
      </div>
    </n-collapse-transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { NIcon, NCollapseTransition } from 'naive-ui';
import { ChevronDown16Regular } from '@vicons/fluent';
import { css } from '@/styled-system/css';
import { usePreferenceStore } from '@/stores/preferenceStore';

defineProps<{ text: string }>();
const isOpen = ref(false);
const pref = usePreferenceStore();

const container = css({ mt: '2' });

const toggleBtn = css({
  display: 'flex', alignItems: 'center', gap: '1',
  fontSize: '12px', fontWeight: 'bold', color: 'surface.textDim',
  bg: 'transparent', border: 'none', cursor: 'pointer',
  p: '0', mb: '1',
  _hover: { color: 'brand.primary' }
});

const iconStyle = (open: boolean) => css({
  transition: 'transform 0.2s',
  transform: open ? 'rotate(180deg)' : 'rotate(0deg)'
});

const contentBox = css({
  bg: 'surface.base', 
  border: '1px dashed token(colors.surface.outline)',
  borderRadius: 'md',
  p: '2'
});

const preText = css({
  fontFamily: 'mono', fontSize: '10px', color: 'surface.textDim',
  whiteSpace: 'pre-wrap', wordBreak: 'break-all', m: 0
});
</script>