import api from "@/services/api";

export interface NotamParseRequest {
  raw_text: string;
}

export interface NotamParseResponse {
  record_id: number;
  parse_fields: Record<string, unknown>;
}

export const notamAPI = {
  // parse(payload: NotamParseRequest) {
  //   return api.post<NotamParseResponse>("/notam/parse", payload);
  // },
  parse(payload: NotamParseRequest, config?: { key: string; provider: string }) {
    // 将 Key 放入 Header 传给后端
    // 后端 api_manager 需要对应修改逻辑读取 X-Override-Key
    const headers = config ? {
        'X-AI-Proxy-Key': config.key,
        'X-AI-Proxy-Provider': config.provider
    } : {};

    return api.post<NotamParseResponse>("/notam/parse", payload, { headers });
  },
  history() {
    return api.get("/notam/history");
  },
};
