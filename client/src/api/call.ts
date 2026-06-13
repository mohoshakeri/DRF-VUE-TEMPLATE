import type {AxiosRequestHeaders, Method} from "axios";

import apiClient from "/src/api/client";
import {useGlobalStore} from "/src/stores/global";

export type ApiResponse<T> = T | {isHTML: true; contents: string} | undefined;

let activeRequestsCount = 0;

export default async function apiCall<T>(
  path: string,
  method: Method = "GET",
  headers: Record<string, string | undefined> = {},
  params: Record<string, unknown> = {},
  data: unknown = {},
): Promise<ApiResponse<T>> {
  const store = useGlobalStore();

  activeRequestsCount += 1;
  store.isLoading = true;

  const requestHeaders = {...headers};
  if (data instanceof FormData) {
    delete requestHeaders["Content-Type"];
  }

  try {
    const response = await apiClient.request({
      url: path,
      method,
      headers: requestHeaders as AxiosRequestHeaders,
      params,
      data,
    });
    const contentType = String(response.headers["content-type"] || "");
    if (contentType.includes("text/html")) {
      return {isHTML: true, contents: response.data};
    }
    return response.data || ({} as T);
  } catch (error) {
    console.error(error);
    return undefined;
  } finally {
    activeRequestsCount -= 1;
    if (activeRequestsCount === 0) {
      store.isLoading = false;
    }
  }
}
