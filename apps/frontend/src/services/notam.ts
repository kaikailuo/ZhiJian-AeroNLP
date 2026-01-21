import api from "@/services/api";

export interface NotamParseRequest {
  raw_text: string;
}

export interface NotamParseResponse {
  record_id: number;
  parse_fields: Record<string, unknown>;
}

export const notamAPI = {
  parse(payload: NotamParseRequest) {
    return api.post<NotamParseResponse>("/notam/parse", payload);
  },
  history() {
    return api.get("/notam/history");
  },
};
