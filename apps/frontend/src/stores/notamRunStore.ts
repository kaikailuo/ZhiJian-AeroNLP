import { NotamCardModel } from "@/models/NotamCard";
import { defineStore } from "pinia";
import { ref } from "vue";

export interface GroundingContext {
  code: string;
  name: string;
  coordinates: [number, number];
  fir: string;
}

// [新增] 雷达目标接口
export interface RadarTarget {
  code: string;       // ZBAA
  name: string;
  fir: string;
  signalStrength: number; // -30 到 -120 (dB)
  status: 'scanning' | 'locked' | 'warning';
  lastPing: number;
}

// [新增] 简易的机场数据库 Mock
const AIRPORT_DB: Record<string, GroundingContext> = {
  ZBAA: { code: "ZBAA", name: "Beijing Capital Intl", coordinates: [40.0799, 116.6031], fir: "ZBPE" },
  ZSPD: { code: "ZSPD", name: "Shanghai Pudong Intl", coordinates: [31.1443, 121.8083], fir: "ZSHA" },
  ZGGG: { code: "ZGGG", name: "Guangzhou Baiyun Intl", coordinates: [23.3959, 113.2988], fir: "ZGZU" },
  ZUUU: { code: "ZUUU", name: "Chengdu Tianfu Intl", coordinates: [30.5785, 104.1111], fir: "ZPKM" },
  VHHH: { code: "VHHH", name: "Hong Kong Intl", coordinates: [22.3080, 113.9185], fir: "VHHK" },
  RJTT: { code: "RJTT", name: "Tokyo Haneda", coordinates: [35.5494, 139.7798], fir: "RJJJ" },
  WSSS: { code: "WSSS", name: "Singapore Changi", coordinates: [1.3644, 103.9915], fir: "WSJC" },
  KJFK: { code: "KJFK", name: "John F. Kennedy Intl", coordinates: [40.6413, -73.7781], fir: "KZNY" },
  EGLL: { code: "EGLL", name: "London Heathrow", coordinates: [51.4700, -0.4543], fir: "EGTT" },
};

export const useNotamRunStore = defineStore("notam-run", () => {
  // --- State ---
  
  // 1. 卡片流：直接持有 Class 实例的数组
  const cards = ref<NotamCardModel[]>([]);

  // 2. 全局交互状态
  const currentGrounding = ref<GroundingContext | null>(null);

  // 3. 雷达监控列表
  const targets = ref<RadarTarget[]>([
    { code: "ZSPD", name: "Shanghai Pudong", fir: "ZSHA", signalStrength: -42, status: 'scanning', lastPing: Date.now() },
    { code: "VHHH", name: "Hong Kong Intl", fir: "VHHK", signalStrength: -68, status: 'locked', lastPing: Date.now() - 50000 },
    { code: "EGLL", name: "London Heathrow", fir: "EGTT", signalStrength: -95, status: 'warning', lastPing: Date.now() - 120000 },
    { code: "KJFK", name: "New York JFK", fir: "KZNY", signalStrength: -102, status: 'scanning', lastPing: Date.now() - 300000 },
  ]);

  // --- Actions: Card Management ---

  /**
   * 创建一个新任务
   */
  const createRun = (rawText: string) => {
    // 1. 实例化模型
    const card = new NotamCardModel(rawText);
    
    // 2. 加入列表 (最新在最前)
    cards.value.unshift(card);
    
    // 3. 让卡片自己开始干活
    card.startAnalysis();
    
    return card.id;
  };

  // [新增] 模拟批量运行
  const simulateBatch = async () => {
    const demos = [
      "A0521/24 NOTAMN... ZBAA ... RWY 18L/36R CLSD DUE TO MAINT...",
      "C1024/24 NOTAMN... ZSPD ... ILS RWY 17L GP U/S...",
      "A0111/24 NOTAMN... VHHH ... TWY A CLSD PERM...",
      "A0882/24 NOTAMN... ZGGG ... FIREWORKS DISPLAY..."
    ];

    for (const text of demos) {
      createRun(text);
      // 错峰触发，营造流式感
      await new Promise(r => setTimeout(r, 600)); 
    }
  };

  const clearAll = () => {
    cards.value = [];
    currentGrounding.value = null;
  };

  // [修改] 调试版 Grounding 更新逻辑
  const updateGrounding = (text: string) => {
    // console.log("[Store] Updating grounding with text:", text);
    // 移除空白字符，防止 "Z B A A" 这种情况
    const cleanText = text ? text.replace(/\s+/g, " ").trim().toUpperCase() : "";
    if (!cleanText) {
      currentGrounding.value = null;
      return;
    }
    // 正则匹配所有可能的 4 位代码
    const candidates = cleanText.match(/[A-Z]{4}/g);
    if (candidates) {
      // 查找数据库
      const foundCode = candidates.find(code => Object.prototype.hasOwnProperty.call(AIRPORT_DB, code));
      if (foundCode) {
        // 只有当变了才更新，避免闪烁，但如果是从 null 变过来也要更新
        if (currentGrounding.value?.code !== foundCode) {
           currentGrounding.value = AIRPORT_DB[foundCode];
        }
        return;
      }
    }
    // 如果当前有锁定，但新的输入里不再包含该代码，则清除锁定
    // 例如：从 "ZBAA" 删改成 "ZBA"
    if (currentGrounding.value && !cleanText.includes(currentGrounding.value.code)) {
      console.log("[Store] Clearing grounding");
      currentGrounding.value = null;
    }
  };

  // [新增] 添加订阅
  const addTarget = (code: string) => {
    // 查库
    const info = AIRPORT_DB[code];
    if (!info) return;

    // 查重
    if (targets.value.find(t => t.code === code)) return;

    targets.value.unshift({
      code: info.code,
      name: info.name.replace(" Intl", ""), // 简化名字
      fir: info.fir,
      signalStrength: Math.floor(Math.random() * -60) - 30, // 随机信号
      status: 'scanning',
      lastPing: Date.now()
    });
  };

  // [新增] 移除订阅
  const removeTarget = (code: string) => {
    targets.value = targets.value.filter(t => t.code !== code);
  };

  // [新增] 激活某个目标到主雷达
  const activateTarget = (code: string) => {
    // 复用 updateGrounding 的逻辑，直接把文本传进去
    updateGrounding(code);
  };

  return {
    // State
    cards,
    currentGrounding,
    targets,
    
    // Card Actions
    createRun,
    simulateBatch,
    clearAll,
    
    // Global Actions
    updateGrounding,
    addTarget,
    removeTarget,
    activateTarget
  };
});
