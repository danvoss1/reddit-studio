import type { Asset, Stats, VideoJob, Voice } from "./types";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);

  if (!response.ok) {
    const body = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(body.detail ?? "Request failed");
  }

  if (response.status === 204) return undefined as T;
  return response.json();
}

export const api = {
  jobs: () => request<VideoJob[]>("/api/jobs"),
  job: (id: string) => request<VideoJob>(`/api/jobs/${id}`),
  voices: () => request<Voice[]>("/api/voices"),

  createJob: (payload: unknown) =>
    request<VideoJob>("/api/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  approve: (id: string, script: string) =>
    request<VideoJob>(`/api/jobs/${id}/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ script }),
    }),

  cancel: (id: string) =>
    request<VideoJob>(`/api/jobs/${id}/cancel`, { method: "POST" }),

  updatePublication: (id: string, payload: unknown) =>
    request<VideoJob>(`/api/jobs/${id}/publication`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  assets: () => request<Asset[]>("/api/assets"),

  uploadAsset: (kind: string, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<Asset>(`/api/assets/${kind}`, {
      method: "POST",
      body: form,
    });
  },

  deleteAsset: (id: string) =>
    request<void>(`/api/assets/${id}`, { method: "DELETE" }),

  stats: () => request<Stats>("/api/stats"),
};
