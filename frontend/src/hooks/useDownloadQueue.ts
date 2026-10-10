import { useCallback, useEffect, useState } from "react";
import { api, type AudioFormat, type Job } from "../api";

/** Estado da fila sincronizado com o backend via SSE. */
export function useDownloadQueue() {
  const [jobs, setJobs] = useState<Record<string, Job>>({});
  const [order, setOrder] = useState<string[]>([]);
  const [config, setConfig] = useState<{ format: AudioFormat; download_dir: string } | null>(null);
  const [online, setOnline] = useState(false);

  const upsert = useCallback((job: Job) => {
    setJobs((prev) => ({ ...prev, [job.id]: job }));
    setOrder((prev) => (prev.includes(job.id) ? prev : [job.id, ...prev]));
  }, []);

  useEffect(() => {
    api.config().then(setConfig).catch(() => setOnline(false));
    api.listJobs().then((list) => list.reverse().forEach(upsert)).catch(() => {});
    const es = new EventSource(api.eventsUrl);
    es.onopen = () => setOnline(true);
    es.onerror = () => setOnline(false);
    es.onmessage = (e) => upsert(JSON.parse(e.data));
    return () => es.close();
  }, [upsert]);

  const clearFinished = async () => {
    await api.clearFinished();
    const keep = (j: Job) => !["done", "skipped", "expanded"].includes(j.status);
    setJobs((prev) => Object.fromEntries(Object.entries(prev).filter(([, j]) => keep(j))));
    setOrder((prev) => prev.filter((id) => jobs[id] && keep(jobs[id])));
  };

  return {
    jobs: order.map((id) => jobs[id]).filter(Boolean),
    config,
    online,
    add: (urls: string[], fmt: AudioFormat) => api.addJobs(urls, fmt),
    retry: (id: string) => api.retry(id),
    clearFinished,
    openFolder: () => api.openFolder(),
  };
}
