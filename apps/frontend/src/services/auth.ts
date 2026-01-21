import api from "@/services/api";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface RegisterPayload {
  email: string;
  password: string;
  role?: string;
}

export interface LogoutPayload {
  refresh_token: string;
}

export const authAPI = {
  login(payload: LoginPayload) {
    return api.post<TokenResponse>("/auth/login", payload);
  },
  register(payload: RegisterPayload) {
    return api.post("/auth/register", payload);
  },
  logout(payload: LogoutPayload) {
    return api.post("/auth/logout", payload);
  },
};
