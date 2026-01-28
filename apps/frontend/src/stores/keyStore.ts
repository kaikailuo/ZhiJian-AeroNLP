import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export interface AiKey {
  id: string;
  name: string;
  provider: 'deepseek' | 'openai' | 'dmx';
  sk: string;
  baseUrl?: string;
  isActive: boolean;
  createdAt: string;
}

export const useKeyStore = defineStore('keys', () => {
  // 从 localStorage 初始化，如果没有则为空数组
  const keys = ref<AiKey[]>(JSON.parse(localStorage.getItem('user_ai_keys') || '[]'));

  // Getters
  const activeKeys = computed(() => keys.value.filter(k => k.isActive));
  
  const groupedKeys = computed(() => {
    return {
      deepseek: keys.value.filter(k => k.provider === 'deepseek' && k.isActive),
      openai: keys.value.filter(k => k.provider === 'openai' && k.isActive),
      dmx: keys.value.filter(k => k.provider === 'dmx' && k.isActive),
    };
  });

  // Actions
  function addKey(payload: Omit<AiKey, 'id' | 'isActive' | 'createdAt'>) {
    const newKey: AiKey = {
      ...payload,
      id: crypto.randomUUID(),
      isActive: true,
      createdAt: new Date().toISOString()
    };
    keys.value.push(newKey);
    save();
  }

  function removeKey(id: string) {
    keys.value = keys.value.filter(k => k.id !== id);
    save();
  }

  function save() {
    localStorage.setItem('user_ai_keys', JSON.stringify(keys.value));
  }

  return { keys, activeKeys, groupedKeys, addKey, removeKey };
});