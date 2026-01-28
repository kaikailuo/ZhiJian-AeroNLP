// src/constants/events.ts

export const NotamEvents = {
  // 双向绑定标准事件
  UPDATE_MODEL: "update:modelValue",
  
  // 业务动作
  EXECUTE: "execute",
  CLEAR: "clear",
  LOAD_EXAMPLE: "load-example",
  
  // 复杂交互
  BATCH_UPLOAD: "batch-upload",
} as const;

// 提取 Value 类型，供 defineEmits 使用
export type NotamEventType = typeof NotamEvents[keyof typeof NotamEvents];