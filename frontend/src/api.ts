import type {
  Asset,
  Stats,
  TikTokAccount,
  TikTokCreatorInfo,
  TikTokPostStatus,
  TikTokPublishPayload,
  TikTokPublishResult,
  VideoJob,
  Voice,
} from "./types";


const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "")
  ?? "";

const LOCAL_APP_API_KEY =
  import.meta.env.VITE_LOCAL_APP_API_KEY
  ?? "";


async function request<T>(
  url: string,
  options: RequestInit = {},
): Promise<T> {
  const headers =
    new Headers(options.headers);

  if (LOCAL_APP_API_KEY) {
    headers.set(
      "X-Reddit-Studio-Key",
      LOCAL_APP_API_KEY,
    );
  }

  const response = await fetch(
    `${API_BASE_URL}${url}`,
    {
      ...options,
      headers,
    },
  );

  if (!response.ok) {
    const body = await response
      .json()
      .catch(() => ({
        detail:
          response.statusText,
      }));

    throw new Error(
      body.detail
      ?? "Request failed",
    );
  }

  if (
    response.status === 204
  ) {
    return undefined as T;
  }

  return response.json();
}


export const api = {
  jobs: () =>
    request<VideoJob[]>(
      "/api/jobs",
    ),

  job: (id: string) =>
    request<VideoJob>(
      `/api/jobs/${id}`,
    ),

  voices: () =>
    request<Voice[]>(
      "/api/voices",
    ),

  createJob: (
    payload: unknown,
  ) =>
    request<VideoJob>(
      "/api/jobs",
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify(
          payload,
        ),
      },
    ),

  approve: (
    id: string,
    script: string,
  ) =>
    request<VideoJob>(
      `/api/jobs/${id}/approve`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify({
          script,
        }),
      },
    ),

  cancel: (
    id: string,
  ) =>
    request<VideoJob>(
      `/api/jobs/${id}/cancel`,
      {
        method: "POST",
      },
    ),

  updatePublication: (
    id: string,
    payload: unknown,
  ) =>
    request<VideoJob>(
      `/api/jobs/${id}/publication`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify(
          payload,
        ),
      },
    ),

  assets: () =>
    request<Asset[]>(
      "/api/assets",
    ),

  uploadAsset: (
    kind: string,
    file: File,
  ) => {
    const form =
      new FormData();

    form.append(
      "file",
      file,
    );

    return request<Asset>(
      `/api/assets/${kind}`,
      {
        method: "POST",
        body: form,
      },
    );
  },

  deleteAsset: (
    id: string,
  ) =>
    request<void>(
      `/api/assets/${id}`,
      {
        method: "DELETE",
      },
    ),

  stats: () =>
    request<Stats>(
      "/api/stats",
    ),

  tiktokAccount: () =>
    request<TikTokAccount>(
      "/api/tiktok/account",
    ),

  connectTikTok: () =>
    request<{
      authorization_url: string;
    }>(
      "/api/tiktok/connect",
      {
        method: "POST",
      },
    ),

  disconnectTikTok: () =>
    request<void>(
      "/api/tiktok/account",
      {
        method: "DELETE",
      },
    ),

  tiktokCreatorInfo: () =>
    request<TikTokCreatorInfo>(
      "/api/tiktok/creator-info",
    ),

  publishToTikTok: (
    id: string,
    payload:
      TikTokPublishPayload,
  ) =>
    request<TikTokPublishResult>(
      `/api/jobs/${id}/tiktok/publish`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify(
          payload,
        ),
      },
    ),

  refreshTikTokStatus: (
    id: string,
  ) =>
    request<TikTokPostStatus>(
      `/api/jobs/${id}/tiktok/status`,
      {
        method: "POST",
      },
    ),
};
