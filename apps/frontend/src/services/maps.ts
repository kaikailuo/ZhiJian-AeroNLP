import api from "@/services/api";

export const mapsAPI = {
  summary() {
    return api.get("/maps/summary");
  },
};
