import api from "@/services/api";

export const trainingAPI = {
  list() {
    return api.get("/training");
  },
};
