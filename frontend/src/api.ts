export type JobStatus = "pending" | "downloading" | "done" | "skipped" | "error" | "expanding" | "expanded";
export type AudioFormat = "m4a" | "mp3";

export interface Job {
  id: string;
  url: string;
  video_id: string | null;
  fmt: AudioFormat;
  kind: "video" | "playlist";
  status: JobStatus;
  progress: number;
  speed: number | null;
  eta: number | null;
  title: string | null;
  file: string | null;
  error: string | null;
  retries?: number;
}

export const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const req = (path: string, init?: RequestInit) =>
  fetch(`${API_BASE}${path}`, init).then((r) => {
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  });

export const api = {
  config: (): Promise<{ format: AudioFormat; download_dir: string }> => req("/api/config"),
  listJobs: (): Promise<Job[]> => req("/api/jobs"),
  addJobs: (urls: string[], format: AudioFormat) =>
    req("/api/jobs", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ urls, format }) }),
  retry: (id: string) => req(`/api/jobs/${id}/retry`, { method: "POST" }),
  clearFinished: () => req("/api/jobs/finished", { method: "DELETE" }),
  openFolder: () => req("/api/open-folder", { method: "POST" }),
  eventsUrl: `${API_BASE}/api/events`,
};
