import api from "@/services/api";

export const dashboardAPI = {
  summary() {
    return api.get("/dashboard/summary");
  },
};
