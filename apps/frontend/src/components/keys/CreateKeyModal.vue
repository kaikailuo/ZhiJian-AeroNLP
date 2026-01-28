<template>
  <div v-if="isOpen" :class="overlayStyle">
    <div :class="contentStyle">
      <h3 :class="titleStyle">🔗 录入新 API Key</h3>
      
      <div :class="fieldStyle">
        <label>供应商 (Provider)</label>
        <select v-model="form.provider" :class="inputStyle">
          <option value="deepseek">DeepSeek (深度求索)</option>
          <option value="openai">OpenAI (GPT-4)</option>
          <option value="dmx">DMX (聚合API)</option>
        </select>
      </div>

      <div :class="fieldStyle">
        <label>名称备注</label>
        <input v-model="form.name" type="text" placeholder="例如: 个人 DeepSeek Key" :class="inputStyle" />
      </div>

      <div :class="fieldStyle">
        <label>Secret Key (sk-xxxx)</label>
        <input v-model="form.sk" type="password" placeholder="sk-..." :class="inputStyle" />
      </div>

      <div :class="actionsStyle">
        <button :class="btnCancel" @click="$emit('close')">取消</button>
        <button :class="btnConfirm" @click="handleSubmit">保存 Key</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { css } from '@/styled-system/css';

const props = defineProps<{ isOpen: boolean }>();
const emit = defineEmits(['close', 'save']);

const form = ref({
  provider: 'deepseek' as 'deepseek' | 'openai' | 'dmx',
  name: '',
  sk: ''
});

const handleSubmit = () => {
  if (!form.value.sk) return;
  emit('save', { ...form.value });
  // Reset
  form.value = { provider: 'deepseek', name: '', sk: '' };
};

// Styles
const overlayStyle = css({
  position: 'fixed', inset: 0, bg: 'rgba(8, 12, 22, 0.65)', backdropFilter: 'blur(4px)',
  display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100
});
const contentStyle = css({
  bg: 'surface.base', width: '420px', p: '6', borderRadius: 'xl',
  border: '1px solid token(colors.surface.outlineStrong)', boxShadow: '0 24px 48px rgba(0,0,0,0.32)'
});
const titleStyle = css({ fontSize: 'xl', fontWeight: 'bold', color: 'surface.text', mb: '6' });
const fieldStyle = css({ 
  mb: '4', display: 'flex', flexDirection: 'column', gap: '2', fontSize: 'sm', color: 'surface.textDim'
});
const inputStyle = css({
  p: '2.5', borderRadius: 'md', bg: 'surface.sunken', border: '1px solid token(colors.surface.outline)', color: 'surface.text',
  _focus: { borderColor: 'brand.primary', outline: 'none' }
});
const actionsStyle = css({ display: 'flex', justifyContent: 'flex-end', gap: '3', mt: '6' });
const btnCancel = css({ p: '2 4', borderRadius: 'md', color: 'surface.textDim', cursor: 'pointer', _hover: { bg: 'surface.elevated' } });
const btnConfirm = css({ p: '2 6', borderRadius: 'md', bg: 'brand.primary', color: 'white', fontWeight: 'bold', cursor: 'pointer', _hover: { bg: 'brand.hover' } });
</script>
