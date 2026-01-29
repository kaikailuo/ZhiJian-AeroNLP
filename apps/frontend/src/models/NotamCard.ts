import { reactive } from 'vue';

// --- 类型定义区 (原 Store 中的定义下沉至此) ---

export const NotamStage = {
  IDLE: "idle",
  CONNECTING: "connecting",
  DISCOVERING: "discovering",
  ANALYZING: "analyzing",
  VALIDATING: "validating",
  FINALIZED: "finalized",
  FAILED: "failed"
} as const;
export type NotamStage = typeof NotamStage[keyof typeof NotamStage];

export const AgentType = {
  DISCOVERY: "DISCOVERY",
  ANALYST: "ANALYST",
  VALIDATOR: "VALIDATOR"
} as const;
export type AgentType = typeof AgentType[keyof typeof AgentType];

export const AlertSeverity = {
  INFO: "info",
  WARNING: "warning",
  CRITICAL: "critical",
  ACTIVE: "active"
} as const;
export type AlertSeverity = typeof AlertSeverity[keyof typeof AlertSeverity];

// 4. 时效状态
export const TimeStatus = {
  ACTIVE: "active",
  PENDING: "pending",
  EXPIRED: "expired",
  PERM: "perm",
  UNKNOWN: "unknown"
} as const;
export type TimeStatus = typeof TimeStatus[keyof typeof TimeStatus];

export interface ThoughtLog {
  id: string;
  agent: AgentType;
  content: string;
  timestamp: number;
  isStreaming: boolean;
}

export interface NotamStructuredData {
  identifier: string;
  summary: string;
  severity: AlertSeverity;
  tags: string[];
  validity: { from: string; to: string; isPerm: boolean };
  confidence: number;
}

/**
 * NotamCardModel
 * 一个自包含的领域模型，负责管理单条 NOTAM 的生命周期、数据解析和 AI 思考流。
 */
export class NotamCardModel {
  // --- 核心状态 ---
  id: string; // 内部 UUID
  rawText: string;
  airportCode: string = "Pending"; // 初始状态
  
  // UI 状态
  stage: NotamStage = NotamStage.IDLE;
  isExpanded: boolean = false; // 控制 UI 折叠/展开
  
  // AI 思考过程 (Log Stream)
  thoughts: ThoughtLog[] = [];
  
  // 最终产出 (Structured Output)
  // 给予默认空值，方便 UI 渲染
  data: NotamStructuredData = {
    identifier: "PENDING",
    summary: "",
    severity: AlertSeverity.INFO, // 默认灰色
    tags: [],
    validity: { from: "", to: "", isPerm: false },
    confidence: 0
  };

  constructor(rawText: string, id?: string) {
    this.id = id || crypto.randomUUID();
    this.rawText = rawText;
    this.extractBasicInfo();
    // [关键] 使用 reactive 包裹实例自身
    // 这样在 Vue 组件中直接使用 card.stage 或 card.data 都是响应式的
    return reactive(this) as NotamCardModel;
  }

  // [新增] 基础信息提取逻辑
  extractBasicInfo() {
    // 1. 提取编号 (例如 A0521/24 或 C1234/23)
    // 匹配规则：字母开头 + 4位数字 + / + 2位数字
    const idMatch = this.rawText.match(/[A-Z]\d{4}\/\d{2}/);
    if (idMatch) {
      this.data.identifier = idMatch[0];
    }

    // 2. 提取机场 (A项)
    // 匹配规则：A) 后面跟 4个大写字母
    const airportMatch = this.rawText.match(/A\)\s*([A-Z]{4})/);
    if (airportMatch) {
      this.airportCode = airportMatch[1];
    } else {
        // 如果没有 A) 项，尝试在全文找第一个出现的四字码（兜底）
        const fallbackMatch = this.rawText.match(/\b[A-Z]{4}\b/);
        if (fallbackMatch && !['NOTAM', 'Q)', 'A)', 'B)', 'C)', 'D)', 'E)'].includes(fallbackMatch[0])) {
             this.airportCode = fallbackMatch[0];
        }
    }
  }

  // --- 行为方法 (Actions) ---

  // [新增] 计算属性：获取当前业务时效状态
  // 注意：在 Class 中使用 getter，配合 reactive 可以实现响应式
  get timeStatus(): TimeStatus {
    if (this.stage !== NotamStage.FINALIZED && this.stage !== NotamStage.IDLE) return TimeStatus.UNKNOWN;
    
    if (this.data.validity.isPerm) return TimeStatus.PERM;

    const now = new Date();
    const from = new Date(this.data.validity.from);
    const to = new Date(this.data.validity.to);

    if (isNaN(from.getTime())) return TimeStatus.UNKNOWN;

    if (now < from) return TimeStatus.PENDING;
    if (to && now > to) return TimeStatus.EXPIRED;
    
    return TimeStatus.ACTIVE;
  }

  /**
   * 启动 AI 分析流程 (模拟)
   * 将原本 Store 里的 simulateRun 逻辑完全封装在此
   */
  async startAnalysis() {
    this.stage = NotamStage.CONNECTING;
    this.isExpanded = true; // 开始分析时自动展开

    const sleep = (ms: number) => new Promise(r => setTimeout(r, ms));
    
    // 辅助函数：模拟打字机效果
    const typeWriter = async (agent: AgentType, text: string) => {
      // 1. 创建新日志
      const logId = crypto.randomUUID();
      const logIdx = this.thoughts.push({
        id: logId,
        agent,
        content: "",
        timestamp: Date.now(),
        isStreaming: true
      }) - 1;

      // 2. 逐字输出
      const chars = text.split('');
      for (const char of chars) {
        this.thoughts[logIdx].content += char;
        await sleep(Math.random() * 10 + 5); // 随机打字速度
      }

      // 3. 结束流
      this.thoughts[logIdx].isStreaming = false;
    };

    // Stage 1: Discovery
    await sleep(200);
    this.stage = NotamStage.DISCOVERING;
    
    // 再次确认提取结果
    this.extractBasicInfo();
    
    await typeWriter('DISCOVERY', `Scanning input stream...\nIdentified Aerodrome Entity: [${this.airportCode}]\nValidating temporal format... OK.`);

    // Stage 2: Analyst
    await sleep(300);
    this.stage = NotamStage.ANALYZING;
    
    // 根据关键字生成不同的 Mock 结果
    let mockResult: Partial<NotamStructuredData> = {};
    let reasoningText = "";

    if (this.rawText.includes("CLOSED") || this.rawText.includes("CLSD")) {
      reasoningText = "Detected keyword 'CLSD/CLOSED'.\nMapping operational impact: HIGH.\nGenerating critical alert wrapper.";
      mockResult = {
        severity: AlertSeverity.CRITICAL,
        summary: `跑道/设施关闭警告。${this.airportCode} 运行能力将显著下降。`,
        tags: ['CLOSED', 'OPS IMPACT'],
        confidence: 98
      };
    } else if (this.rawText.includes("U/S") || this.rawText.includes("UNSERVICEABLE")) {
      reasoningText = "Detected equipment failure (U/S).\nImpact: Non-precision approach required.\nSeverity: WARNING.";
      mockResult = {
        severity: AlertSeverity.WARNING,
        summary: `导航设施/灯光不可用。请执行降级运行程序。`,
        tags: ['U/S', 'EQUIPMENT'],
        confidence: 92
      };
    } else {
      reasoningText = "Routine information detected.\nNo significant operational restrictions found.";
      mockResult = {
        severity: AlertSeverity.INFO, // 绿色
        summary: `常规航行信息。无重大运行影响。`,
        tags: ['INFO', 'ROUTINE'],
        confidence: 88
      };
    }

    await typeWriter('ANALYST', reasoningText);
    
    // 更新结构化数据
    Object.assign(this.data, mockResult);
    
    // 模拟时间解析
    this.data.validity = {
      from: new Date().toISOString(),
      to: new Date(Date.now() + 86400000).toISOString(), // +1天
      isPerm: false
    };

    // Stage 3: Validator
    await sleep(200);
    this.stage = NotamStage.VALIDATING;
    await typeWriter('VALIDATOR', `Cross-checking against AIP... Consistency Verified.\nFinalizing output.`);

    this.stage = NotamStage.FINALIZED;
    // 分析完成后，如果有 Critical 警告保持展开，否则收起 (可选优化)
    if (this.data.severity !== AlertSeverity.CRITICAL) {
      this.isExpanded = false; 
    }
  }

  // 手动更新数据的入口 (用于 Human-in-the-loop 修正)
  updateData(patch: Partial<NotamStructuredData>) {
    Object.assign(this.data, patch);
  }
}