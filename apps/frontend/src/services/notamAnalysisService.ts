import { 
  NotamStage, 
  AgentType, 
  AlertSeverity, 
  EntityDomain, 
  EntityStatus, 
  GeometryType,
  NotamType,
  type NotamStructuredData,
  type ImpactedEntity,
  type SpatialData
} from "@/models/NotamCard";
import { useKeyStore } from "@/stores/keyStore";
import { notamAPI } from "@/services/notam";

// [新增] 导出正则工具，供 Service 内部和 Store 使用
export const REGEX_SPLIT_ID = /[A-Z]\d{4}\/\d{2}\b/g;

export const AnalysisEventType = {
  STAGE_CHANGE: 'stage_change',     // 阶段流转 (e.g. CONNECTING -> DISCOVERING)
  THOUGHT_START: 'thought_start',   // 智能体开始思考
  THOUGHT_DELTA: 'thought_delta',   // 思考内容打字机输出
  DATA_UPDATE: 'data_update',       // 结构化数据增量更新
  DONE: 'done',                     // 完成
  ERROR: 'error'                    // 错误
} as const;
export type AnalysisEventType = typeof AnalysisEventType[keyof typeof AnalysisEventType];

export type StreamEvent = 
  | { type: typeof AnalysisEventType.STAGE_CHANGE; value: NotamStage }
  | { type: typeof AnalysisEventType.THOUGHT_START; agent: AgentType }
  | { type: typeof AnalysisEventType.THOUGHT_DELTA; content: string }
  | { type: typeof AnalysisEventType.DATA_UPDATE; data: Partial<NotamStructuredData> }
  | { type: typeof AnalysisEventType.DONE }
  | { type: typeof AnalysisEventType.ERROR; message: string };

// 内部工具：模拟网络延迟
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));


const canceledAnalyses = new Set<string>();

export const notamAnalysisService = {
  cancelAnalysis(id: string) {
    canceledAnalyses.add(id);
  },
  // [新增] 预处理：将原始大文本切分为独立的 NOTAM 片段
  // 职责：纯粹的文本处理，不涉及 Store 业务
  preProcessInput(rawInput: string): string[] {
    if (!rawInput) return [];
    
    // 1. 尝试匹配标准的 NOTAM ID (e.g., A1234/24)
    const matches = Array.from(rawInput.matchAll(REGEX_SPLIT_ID));
    
    if (matches.length > 0) {
      const chunks: string[] = [];
      for (let i = 0; i < matches.length; i++) {
        const start = matches[i].index!;
        const end = i < matches.length - 1 ? matches[i + 1].index! : rawInput.length;
        const chunk = rawInput.slice(start, end).trim();
        if (chunk.length > 10) { // 过滤太短的噪点
          chunks.push(chunk);
        }
      }
      return chunks;
    } 
    
    // 2. 如果没找到标准头，视为单条处理
    return rawInput.trim().length > 5 ? [rawInput.trim()] : [];
  },
  async *analyzeStream(rawText: string, airportCode: string, analysisId?: string): AsyncGenerator<StreamEvent> {
    const isCanceled = () => (analysisId ? canceledAnalyses.has(analysisId) : false);
    
    try {
      if (isCanceled()) return;
      yield { type: AnalysisEventType.STAGE_CHANGE, value: NotamStage.CONNECTING };
      await sleep(200);
      if (isCanceled()) return;

      yield { type: AnalysisEventType.STAGE_CHANGE, value: NotamStage.DISCOVERING };
      yield { type: AnalysisEventType.THOUGHT_START, agent: AgentType.DISCOVERY };
      yield* simulateTokenStream(`Target Aerodrome: [${airportCode}]\nPreparing request payload...`);
      await sleep(150);
      if (isCanceled()) return;

      yield { type: AnalysisEventType.STAGE_CHANGE, value: NotamStage.ANALYZING };
      yield { type: AnalysisEventType.THOUGHT_START, agent: AgentType.ANALYST };
      yield* simulateTokenStream("Calling backend /notam/parse ...");
      const keyStore = useKeyStore();
      const selected = keyStore.selectedKey;
      if (!selected) {
        yield { type: AnalysisEventType.ERROR, message: "No active API key selected." };
        return;
      }
      const { data } = await notamAPI.parse(
        { raw_text: rawText },
        { key: selected.sk, provider: selected.provider }
      );
      const normalized = normalizeParseFields(data.parse_fields);
      yield { type: AnalysisEventType.DATA_UPDATE, data: mapToStructured(rawText, airportCode, normalized) };
      if (isCanceled()) return;

      yield { type: AnalysisEventType.STAGE_CHANGE, value: NotamStage.VALIDATING };
      yield { type: AnalysisEventType.THOUGHT_START, agent: AgentType.VALIDATOR };
      yield* simulateTokenStream("Validating output shape and confidence...");
      const now = new Date();
      const nextDay = new Date(now.getTime() + 24 * 60 * 60 * 1000);
      yield { 
        type: AnalysisEventType.DATA_UPDATE, 
        data: {
          validity: {
            from: now.toISOString(),
            to: nextDay.toISOString(),
            isPerm: false,
            duration_text: "24h 00m"
          }
        } 
      };
      yield { type: AnalysisEventType.DONE };
    } catch (e: any) {
      const status = e?.response?.status;
      const detail = e?.response?.data?.detail;
      let message = e instanceof Error ? e.message : "Internal Reasoning Error";
      if (status === 401) {
        message = "认证已过期，请重新登录后再试。";
      } else if (detail) {
        message = String(detail);
      }
      yield { type: AnalysisEventType.ERROR, message };
    } finally {
      if (analysisId) canceledAnalyses.delete(analysisId);
    }
  }
};

async function* simulateTokenStream(text: string): AsyncGenerator<StreamEvent> {
  const chars = text.split('');
  let buffer = "";
  
  for (let i = 0; i < chars.length; i++) {
    buffer += chars[i];
    
    if (Math.random() > 0.7 || i === chars.length - 1) {
      yield { type: AnalysisEventType.THOUGHT_DELTA, content: buffer };
      buffer = "";
      await sleep(Math.random() * 20 + 10); 
    }
  }
}

function normalizeParseFields(payload: unknown): Record<string, any> {
  if (Array.isArray(payload)) {
    return (payload[0] && typeof payload[0] === "object") ? payload[0] : {};
  }
  if (payload && typeof payload === "object") {
    return payload as Record<string, any>;
  }
  return {};
}

function inferNotamType(rawText: string): NotamType {
  if (rawText.includes("NOTAMC")) return NotamType.CANCEL;
  if (rawText.includes("NOTAMR")) return NotamType.REPLACE;
  return NotamType.NEW;
}

function mapToStructured(rawText: string, airportCode: string, parsed: Record<string, any>): Partial<NotamStructuredData> {
  const statusText = String(parsed.status || parsed.restriction_Type || "unknown").toLowerCase();
  const runway = parsed.runway ? String(parsed.runway) : "";
  const airport = parsed.airport ? String(parsed.airport) : airportCode;

  const impactedEntities: ImpactedEntity[] = runway
    ? [{
        id: crypto.randomUUID(),
        domain: EntityDomain.RUNWAY,
        designator: `RWY ${runway}`,
        status: mapEntityStatus(statusText),
        reason: parsed.reason ? String(parsed.reason) : undefined,
      }]
    : [];

  return {
    type: inferNotamType(rawText),
    severity: mapSeverity(statusText),
    summary: String(parsed.summary || rawText.slice(0, 160)),
    impacted_entities: impactedEntities,
    spatial_data: buildSpatialData(),
    tags: buildTags(statusText, runway, airport),
    confidence: Number(parsed.confidence ?? 85),
  };
}

function mapSeverity(statusText: string): AlertSeverity {
  if (statusText.includes("closed")) return AlertSeverity.CRITICAL;
  if (statusText.includes("restricted") || statusText.includes("ltd") || statusText.includes("tips")) return AlertSeverity.WARNING;
  if (statusText.includes("open")) return AlertSeverity.ACTIVE;
  return AlertSeverity.INFO;
}

function mapEntityStatus(statusText: string): EntityStatus {
  if (statusText.includes("closed")) return EntityStatus.CLOSED;
  if (statusText.includes("open")) return EntityStatus.ACTIVE;
  if (statusText.includes("unserviceable") || statusText.includes("u/s")) return EntityStatus.UNSERVICEABLE;
  if (statusText.includes("restricted") || statusText.includes("ltd")) return EntityStatus.RESTRICTED;
  return EntityStatus.CHANGED;
}

function buildSpatialData(): SpatialData {
  return {
    center: { lat: 39.50, lon: 116.41 },
    radius_nm: 5,
    geometry_type: GeometryType.CIRCLE,
    vertical: { lower: "GND", upper: "UNL" },
  };
}

function buildTags(statusText: string, runway: string, airport: string): string[] {
  const tags = new Set<string>();
  if (airport) tags.add(airport);
  if (runway) tags.add("RWY");
  if (statusText) tags.add(statusText.toUpperCase());
  return Array.from(tags);
}
