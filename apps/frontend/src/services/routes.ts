import api from "@/services/api";

export const routesAPI = {
  list() {
    return api.get("/routes");
  },
};
