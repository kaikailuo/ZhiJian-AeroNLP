import api from "@/services/api";

export const apiKeysAPI = {
  list() {
    return api.get("/api-keys");
  },
};
