import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export interface AiKey {
  id: string;
  name: string;
  provider: 'deepseek' | 'openai' | 'dmx' | 'qwen';
  sk: string;
  baseUrl?: string;
  isActive: boolean;
  createdAt: string;
}

export const useKeyStore = defineStore('keys', () => {
  // 从 localStorage 初始化，如果没有则为空数组
  const keys = ref<AiKey[]>(JSON.parse(localStorage.getItem('user_ai_keys') || '[]'));
  const selectedKeyId = ref<string>(localStorage.getItem('selected_ai_key_id') || '');

  // Getters
  const activeKeys = computed(() => keys.value.filter(k => k.isActive));
  
  const groupedKeys = computed(() => {
    return {
      deepseek: keys.value.filter(k => k.provider === 'deepseek' && k.isActive),
      openai: keys.value.filter(k => k.provider === 'openai' && k.isActive),
      dmx: keys.value.filter(k => k.provider === 'dmx' && k.isActive),
      qwen: keys.value.filter(k => k.provider === 'qwen' && k.isActive),
    };
  });

  const selectedKey = computed(() => {
    if (!selectedKeyId.value) return null;
    return keys.value.find(k => k.id === selectedKeyId.value && k.isActive) || null;
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
    if (!selectedKeyId.value) {
      selectedKeyId.value = newKey.id;
    }
    save();
  }

  function removeKey(id: string) {
    keys.value = keys.value.filter(k => k.id !== id);
    if (selectedKeyId.value === id) {
      selectedKeyId.value = keys.value.length > 0 ? keys.value[0].id : '';
    }
    save();
  }

  function selectKey(id: string) {
    selectedKeyId.value = id;
    save();
  }

  function save() {
    localStorage.setItem('user_ai_keys', JSON.stringify(keys.value));
    localStorage.setItem('selected_ai_key_id', selectedKeyId.value);
  }

  if (!selectedKeyId.value && keys.value.length > 0) {
    selectedKeyId.value = keys.value[0].id;
    save();
  }

  return { keys, activeKeys, groupedKeys, selectedKeyId, selectedKey, addKey, removeKey, selectKey };
});
