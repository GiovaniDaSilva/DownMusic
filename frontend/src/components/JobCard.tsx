import type { Job } from "../api";

const LABEL: Record<Job["status"], string> = {
  pending: "Na fila",
  downloading: "Baixando",
  done: "Concluído",
  skipped: "Já existe",
  error: "Erro",
  expanding: "Lendo lista",
  expanded: "Playlist",
};

const fmtSpeed = (b: number | null) => (b ? `${(b / 1048576).toFixed(2)} MB/s` : "");
const fmtEta = (s: number | null) => (s ? `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")} restantes` : "");

export default function JobCard({ job, onRetry, isActive }: { job: Job; onRetry: (id: string) => void; isActive?: boolean }) {
  const name = job.title || job.url;
  const isRetrying = job.status === "downloading" && Boolean(job.retries && job.retries > 0);

  return (
    <li id={`job-${job.id}`} className={`job ${job.status} ${isActive ? "active-focus" : ""}`}>
      <div className="job-title" title={name}>{name}</div>
      {job.status === "error" && (job.video_id || job.kind === "playlist") ? (
        <button className="btn ghost tiny" onClick={() => onRetry(job.id)}>Tentar de novo</button>
      ) : (
        <span className={`badge ${job.status}`}>
          {isRetrying ? "Tentando de novo" : LABEL[job.status]}
        </span>
      )}
      <div className="bar"><span style={{ width: `${job.progress}%` }} /></div>
      <div className="job-meta">
        {job.status === "error" ? (
          <span className="job-error">{job.error}</span>
        ) : (
          <>
            <span>{job.file || job.url}</span>
            {job.status === "downloading" && (
              <span>
                {job.progress}% · {fmtSpeed(job.speed)} {fmtEta(job.eta)}
                {isRetrying && " · 2ª tentativa"}
              </span>
            )}
          </>
        )}
      </div>
    </li>
  );
}

