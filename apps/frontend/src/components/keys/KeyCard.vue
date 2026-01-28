<template>
  <div :class="cardStyle">
    <div :class="headerStyle">
      <span :class="badgeStyle(keyItem.provider)">{{ keyItem.provider }}</span>
      <button :class="deleteBtnStyle" @click="$emit('delete', keyItem.id)">移除</button>
    </div>
    <div :class="nameStyle">{{ keyItem.name }}</div>
    <div :class="skStyle">{{ maskedKey }}</div>
    <div :class="dateStyle">创建于 {{ new Date(keyItem.createdAt).toLocaleDateString() }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { css } from '@/styled-system/css';
import type { AiKey } from '@/stores/keyStore';

const props = defineProps<{ keyItem: AiKey }>();
defineEmits(['delete']);

const maskedKey = computed(() => {
  const sk = props.keyItem.sk;
  if (!sk) return '------';
  return sk.length > 8 ? `${sk.slice(0, 4)}...${sk.slice(-4)}` : '******';
});

// Styles
const cardStyle = css({
  border: '1px solid token(colors.surface.outline)', bg: 'surface.base',
  borderRadius: 'lg', p: '5', position: 'relative', overflow: 'hidden',
  transition: 'all 0.2s', _hover: { borderColor: 'brand.primary', transform: 'translateY(-2px)', bg: 'surface.elevated' }
});

const headerStyle = css({ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: '3' });

const badgeStyle = (provider: string) => css({ 
  textTransform: 'uppercase', fontSize: 'xs', fontWeight: 'bold', 
  px: '2', py: '1', borderRadius: 'md',
  color: provider === 'deepseek' ? '#00e5ff' : (provider === 'openai' ? '#10a37f' : 'brand.text.dim'),
  bg: provider === 'deepseek' ? 'rgba(0, 229, 255, 0.1)' : (provider === 'openai' ? 'rgba(16, 163, 127, 0.1)' : 'rgba(255,255,255,0.05)')
});

const deleteBtnStyle = css({ fontSize: 'xs', color: '#ff4d4f', cursor: 'pointer', opacity: 0.6, _hover: { opacity: 1 } });
const nameStyle = css({ fontWeight: 'bold', fontSize: 'md', color: 'brand.text.main', mb: '1' });
const skStyle = css({ fontFamily: 'mono', fontSize: 'xs', color: 'surface.textDim', bg: 'surface.sunken', p: '1', borderRadius: 'sm', width: 'fit-content' });
const dateStyle = css({ fontSize: 'xs', color: 'surface.textDim', mt: '3' });
</script>
