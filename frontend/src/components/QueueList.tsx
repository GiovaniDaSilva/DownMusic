import { useEffect, useMemo } from "react";
import type { Job } from "../api";
import JobCard from "./JobCard";

interface Props {
  jobs: Job[];
  downloadDir?: string;
  onRetry: (id: string) => void;
  onClear: () => void;
  onOpenFolder: () => void;
}

export default function QueueList({ jobs, downloadDir, onRetry, onClear, onOpenFolder }: Props) {
  const videos = jobs.filter((j) => j.kind !== "playlist");
  const count = (s: Job["status"]) => videos.filter((j) => j.status === s).length;

  const sortedJobs = useMemo(() => {
    // 0 = concluídos, 1 = ativos (baixando/lendo), 2 = pendentes
    const group = (s: Job["status"]) => {
      if (s === "downloading" || s === "expanding") return 1;
      if (s === "pending") return 2;
      return 0; // done, skipped, error, expanded
    };
    return [...jobs].sort((a, b) => group(a.status) - group(b.status));
  }, [jobs]);

  const activeJobId = sortedJobs.find(j => j.status === "downloading" || j.status === "expanding")?.id;

  useEffect(() => {
    if (activeJobId) {
      const el = document.getElementById(`job-${activeJobId}`);
      if (el) el.scrollIntoView({ block: "center", behavior: "smooth" });
    }
  }, [activeJobId]);

  return (
    <section className="card queue-card" aria-labelledby="queue-title">
      <div className="row head">
        <h2 id="queue-title">Fila</h2>
        {jobs.length > 0 && (
          <span id="stats" className="muted">
            {count("done") + count("skipped")}/{jobs.length} concluídos · {count("error")} erros
          </span>
        )}
      </div>
      <div className="scroll-box">
        {sortedJobs.length ? (
          <ul id="queue-list" className="queue">
            {sortedJobs.map((j) => (
              <JobCard key={j.id} job={j} onRetry={onRetry} isActive={j.id === activeJobId} />
            ))}
          </ul>
        ) : (
          <p className="empty">Nenhum download ainda.</p>
        )}
      </div>
      <footer className="row foot">
        <span className="muted small">{downloadDir && `Salvando em: ${downloadDir}`}</span>
        <div className="right">
          <button id="btn-clear" className="btn ghost" onClick={onClear}>Limpar concluídos</button>
          <button id="btn-open" className="btn ghost" onClick={onOpenFolder}>Abrir pasta</button>
        </div>
      </footer>
    </section>
  );
}
