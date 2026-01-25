import api from "@/services/api";

export interface TrainingSubmission {
  exercise_id: string;
  user_answer: any;
}

export interface TrainingResponse {
  status: string;
  message: string;
  data: any;
}

export const trainingAPI = {
  submit(payload: TrainingSubmission) {
    return api.post<TrainingResponse>("/training/submit", payload);
  },
};
