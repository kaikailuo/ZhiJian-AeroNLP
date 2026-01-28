import { defineStore } from "pinia";
import { ref } from "vue";

export type NotamStage =
  | "idle"
  | "connecting"
  | "discovering"
  | "analyzing"
  | "validating"
  | "debating"
  | "rendering"
  | "finalized"
  | "failed";

export type AlertSeverity = "info" | "warning" | "critical";

export interface NotamThought {
  id: string;
  agent: "DISCOVERY" | "ANALYST" | "VALIDATOR" | "CONSENSUS";
  text: string;
  ts: number;
  level?: "thinking" | "success" | "warning" | "error" | "info";
  isStreaming?: boolean; // [新增] 修复类型报错
}

export interface NotamAlert {
  id: string;
  severity: AlertSeverity;
  code?: string;
  message: string;
  ts: number;
}

export interface NotamEvidence {
  id: string;
  field: string;
  snippet: string;
  source?: string;
  ts: number;
}

// [新增] 运行类型区分
export type RunType = "single" | "batch";

export interface NotamRun {
  id: string;
  type: RunType; // [新增]
  createdAt: number;
  rawText: string;
  engineId?: string;
  stage: NotamStage;
  statusMessage?: string;
  uiHeight?: number;
  fields: Record<string, string | number | boolean | null>;
  alerts: NotamAlert[];
  thoughts: NotamThought[];
  evidence: NotamEvidence[];
  // [新增] 批量任务特有属性
  batchProgress?: {
    current: number;
    total: number;
    filename: string;
  };
}

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
  const runs = ref<NotamRun[]>([]);
  const activeRunId = ref<string | null>(null);
  const currentGrounding = ref<GroundingContext | null>(null);

  // [新增] 订阅列表 (默认给几个假数据撑场面)
  const targets = ref<RadarTarget[]>([
    { code: "ZSPD", name: "Shanghai Pudong", fir: "ZSHA", signalStrength: -42, status: 'scanning', lastPing: Date.now() },
    { code: "VHHH", name: "Hong Kong Intl", fir: "VHHK", signalStrength: -68, status: 'locked', lastPing: Date.now() - 50000 },
    { code: "EGLL", name: "London Heathrow", fir: "EGTT", signalStrength: -95, status: 'warning', lastPing: Date.now() - 120000 },
    { code: "KJFK", name: "New York JFK", fir: "KZNY", signalStrength: -102, status: 'scanning', lastPing: Date.now() - 300000 },
  ]);

  const startRun = (
    rawText: string, 
    engineId?: string, 
    type: RunType = "single", 
    batchMeta?: { filename: string; total: number }
  ) => {
    const id = crypto.randomUUID();
    const run: NotamRun = {
      id,
      type,
      createdAt: Date.now(),
      rawText,
      engineId,
      stage: "connecting",
      uiHeight: undefined, // 让 CSS 自动撑开
      fields: {},
      alerts: [],
      thoughts: [],
      evidence: [],
      batchProgress: type === "batch" && batchMeta ? {
        current: 0,
        total: batchMeta.total,
        filename: batchMeta.filename
      } : undefined
    };
    runs.value.unshift(run);
    activeRunId.value = id;
    return id;
  };

  const setStage = (runId: string, stage: NotamStage, statusMessage?: string) => {
    const run = runs.value.find((item) => item.id === runId);
    if (!run) return;
    run.stage = stage;
    run.statusMessage = statusMessage;
    run.uiHeight = calcRunHeight(run);
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

  const addThought = (runId: string, thought: Omit<NotamThought, "id" | "ts">) => {
    const run = runs.value.find((item) => item.id === runId);
    if (!run) return;
    run.thoughts.push({
      id: crypto.randomUUID(),
      ts: Date.now(),
      ...thought,
    });
    run.uiHeight = calcRunHeight(run);
  };

  // [新增] 逐字追加 Token (打字机核心)
  const appendThoughtToken = (runId: string, token: string) => {
    const run = runs.value.find((item) => item.id === runId);
    if (!run || run.thoughts.length === 0) return;
    
    const lastThought = run.thoughts[run.thoughts.length - 1];
    lastThought.text += token;
    lastThought.isStreaming = true;
  };

  // [新增] 结束当前思考流
  const finishThought = (runId: string) => {
    const run = runs.value.find((item) => item.id === runId);
    if (!run || run.thoughts.length === 0) return;
    run.thoughts[run.thoughts.length - 1].isStreaming = false;
  };

  const addAlert = (runId: string, alert: Omit<NotamAlert, "id" | "ts">) => {
    const run = runs.value.find((item) => item.id === runId);
    if (!run) return;
    run.alerts.push({
      id: crypto.randomUUID(),
      ts: Date.now(),
      ...alert,
    });
    run.uiHeight = calcRunHeight(run);
  };

  const mergeFields = (runId: string, patch: Record<string, string | number | boolean | null>) => {
    const run = runs.value.find((item) => item.id === runId);
    if (!run) return;
    run.fields = { ...run.fields, ...patch };
    run.uiHeight = calcRunHeight(run);
  };

  const addEvidence = (runId: string, evidence: Omit<NotamEvidence, "id" | "ts">) => {
    const run = runs.value.find((item) => item.id === runId);
    if (!run) return;
    run.evidence.push({
      id: crypto.randomUUID(),
      ts: Date.now(),
      ...evidence,
    });
    run.uiHeight = calcRunHeight(run);
  };

  const calcRunHeight = (run: NotamRun) => {
    // 基础高度
    let h = 200;
    
    if (run.type === "batch") {
      h = 180; // Batch 卡片稍微紧凑点
      if (run.thoughts.length > 0) h += 100; // 如果有日志展开
      if (run.alerts.length > 0) h += run.alerts.length * 40;
      if (Object.keys(run.fields).length > 0) h += 60;
      return h;
    }

    const base =
      run.stage === "connecting"
        ? 240
        : run.stage === "discovering" || run.stage === "analyzing" || run.stage === "validating"
        ? 280
        : run.stage === "debating" || run.stage === "rendering"
        ? 320
        : run.stage === "failed"
        ? 300
        : 360;

    const fieldCount = Object.keys(run.fields).length;
    const alertBonus = run.alerts.length > 0 ? 30 : 0;
    const thoughtBonus = run.thoughts.length > 0 ? 40 : 0;
    const fieldBonus = Math.min(fieldCount * 8, 80);

    return base + alertBonus + thoughtBonus + fieldBonus;
  };

  // [修改] 调试版 Grounding 更新逻辑
  const updateGrounding = (text: string) => {
    // 移除空白字符，防止 "Z B A A" 这种情况
    const cleanText = text ? text.replace(/\s+/g, " ").trim().toUpperCase() : "";
    
    // console.log("[Store] updateGrounding input:", cleanText);

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
        console.log("[Store] Found airport:", foundCode);
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

  // [新增] 模拟批量运行
  const simulateBatchRun = async (runId: string) => {
    const run = runs.value.find((r) => r.id === runId);
    if (!run || !run.batchProgress) return;

    const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

    setStage(runId, "analyzing", `Batch processing ${run.batchProgress.filename}...`);
    
    // 模拟逐个处理
    const total = run.batchProgress.total;
    for (let i = 1; i <= total; i++) {
      run.batchProgress.current = i;
      
      // 每处理 5 个产生一条日志
      if (i % 5 === 0 || i === 1 || i === total) {
        addThought(runId, { 
          agent: "ANALYST", 
          text: `Processing item #${i}: Extracting spatial data... OK`, 
          level: "info" 
        });
        run.uiHeight = calcRunHeight(run); // 强制重算高度
      }

      // 模拟偶尔发现 Critical Issue
      if (i === 12) {
        addAlert(runId, { severity: "critical", message: `Item #12: ZBAA Runway Closure Detected` });
      }

      await sleep(Math.random() * 50 + 20); // 快速处理
    }

    setStage(runId, "finalized", "Batch import completed");
    
    // 汇总结果
    mergeFields(runId, {
      "Total Parsed": total,
      "Critical Alerts": 1,
      "Success Rate": "100%"
    });
  };

  // [修改] 模拟流式生成
  const simulateRun = async (runId: string) => {
    const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));
    
    // 辅助：流式文本生成
    const streamText = async (text: string) => {
      const chars = text.split("");
      for (const char of chars) {
        appendThoughtToken(runId, char);
        await sleep(Math.random() * 20 + 5); // 5-25ms 随机延迟
      }
      finishThought(runId);
    };

    // Stage 1: Discovery
    setStage(runId, "discovering", "Agent DISCOVERY active...");
    addThought(runId, { agent: "DISCOVERY", text: "", level: "thinking", isStreaming: true });
    
    await streamText("Scanning input text for aeronautical entities...\nIdentified Aerodrome: ZBAA (Beijing Capital)\nIdentified Runway: 18L/36R\nChecking against AIP database...");
    
    mergeFields(runId, { runway: "18L/36R", status: "CLOSED" });

    // Stage 2: Analyst
    await sleep(300);
    setStage(runId, "analyzing", "Agent ANALYST reasoning...");
    addThought(runId, { agent: "ANALYST", text: "", level: "thinking", isStreaming: true });
    
    await streamText("Analyzing closure impact...\nTimeframe: 0000-0800Z (Peak hours)\nTraffic Impact: High capacity reduction expected.\nCross-referencing historical delay data for ZBAA...");
    
    addAlert(runId, { severity: "critical", message: "Significant capacity reduction detected" });

    // Stage 3: Validator
    await sleep(300);
    setStage(runId, "validating", "Validating output...");
    addThought(runId, { agent: "VALIDATOR", text: "", level: "thinking", isStreaming: true });
    await streamText("Verifying logic consistencies... OK.");

    setStage(runId, "finalized", "Render completed");
  };

  const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

  return {
    runs,
    activeRunId,
    currentGrounding,
    targets, // [导出]
    startRun,
    setStage,
    addThought,
    appendThoughtToken, // 确保导出这个
    finishThought,      // 确保导出这个
    addAlert,
    mergeFields,
    addEvidence,
    updateGrounding,
    simulateRun,
    simulateBatchRun, // [新增]
    addTarget,     // [导出]
    removeTarget,  // [导出]
    activateTarget, // [导出]
  };
});
