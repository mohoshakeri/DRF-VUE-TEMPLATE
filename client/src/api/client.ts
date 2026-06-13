import axios, {type AxiosError} from "axios";

import {BACKEND_BASE_URL} from "/src/env";
import {buildFriendlyMessage} from "/src/api/errors";
import {sendMessage} from "/src/utils/messages";
import {getAuthToken} from "/src/utils/storage";

const apiClient = axios.create({
  baseURL: BACKEND_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = token.startsWith("Bearer ")
      ? token
      : ["Bearer", token].join(" ");
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (!error.response) {
      await sendMessage(
        error.code === "ECONNABORTED"
          ? "مهلت اتصال به سرور به پایان رسید."
          : "ارتباط با سرور برقرار نشد. اتصال اینترنت را بررسی کنید.",
        "danger",
      );
      return Promise.reject(error);
    }

    const contentType = String(error.response.headers["content-type"] || "");
    const message = await buildFriendlyMessage(
      error.response.status,
      contentType.includes("application/json"),
      error.response.data,
    );
    if (message) {
      await sendMessage(message, "danger");
    }

    return Promise.reject(error);
  },
);

export default apiClient;
