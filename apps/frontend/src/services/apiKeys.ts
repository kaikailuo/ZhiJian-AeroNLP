import api from "@/services/api";

export enum KeyType {
  AI_PROVIDER = 'AI_PROVIDER', // 用于驱动后端 LLM
  APP_ACCESS = 'APP_ACCESS'    // 用于外部系统调用本应用
}

export interface ApiKey {
  id: string;
  name: string;       // 备注名称，如 "My DeepSeek Key"
  type: KeyType;
  provider?: string;  // 仅 AI_PROVIDER 有效: 'deepseek' | 'openai' | 'dmx'
  keyPrefix: string;  // 用于展示: "sk-Tc9..."
  createdAt: string;
  lastUsed?: string;
  isActive: boolean;
}

// 用于表单提交
export interface CreateKeyPayload {
  name: string;
  type: KeyType;
  provider?: string;
  secretKey: string; // 完整 Key，仅提交时存在
  baseUrl?: string;  // 可选的代理地址
}

export const apiKeysAPI = {
  list() {
    return api.get("/api-keys");
  },
};
