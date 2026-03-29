import axios from "axios";
import { useAuthStore } from "@/stores/auth";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1",
});

type RetriableRequestConfig = {
  _retry?: boolean;
  headers?: Record<string, string>;
  url?: string;
};

api.interceptors.request.use((config) => {
  const auth = useAuthStore();
  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config as RetriableRequestConfig | undefined;
    const status = error?.response?.status;
    const requestUrl = original?.url || "";
    const skipRefresh = requestUrl.includes("/auth/login") || requestUrl.includes("/auth/register") || requestUrl.includes("/auth/refresh");

    if (status === 401 && original && !original._retry && !skipRefresh) {
      original._retry = true;
      const refreshToken = localStorage.getItem("refreshToken");
      if (!refreshToken) {
        const auth = useAuthStore();
        auth.accessToken = null;
        auth.refreshToken = null;
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
        return Promise.reject(error);
      }
      try {
        const { data } = await axios.post(
          `${api.defaults.baseURL}/auth/refresh`,
          { refresh_token: refreshToken }
        );
        const auth = useAuthStore();
        auth.accessToken = data.access_token;
        auth.refreshToken = data.refresh_token;
        localStorage.setItem("accessToken", data.access_token || "");
        localStorage.setItem("refreshToken", data.refresh_token || "");
        if (!original.headers) original.headers = {};
        original.headers.Authorization = `Bearer ${data.access_token}`;
        return api(original as any);
      } catch (refreshError) {
        const auth = useAuthStore();
        auth.accessToken = null;
        auth.refreshToken = null;
        auth.user = null;
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
