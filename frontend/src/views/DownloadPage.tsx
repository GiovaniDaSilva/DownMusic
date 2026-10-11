import QueueList from "../components/QueueList";
import UrlInput from "../components/UrlInput";
import { useDownloadQueue } from "../hooks/useDownloadQueue";

export default function DownloadPage() {
  const q = useDownloadQueue();
  return (
    <>
      <div className="bg-orb orb-1" />
      <div className="bg-orb orb-2" />
      <main className="container">
        <header className="header">
          <div className="logo">♪</div>
          <div>
            <h1>DownMusic</h1>
            <p className="muted">Cole links de vídeos, músicas ou playlists (YouTube e YouTube Music) e deixe o resto comigo.</p>
          </div>
          <span className={`status-dot ${q.online ? "on" : "off"}`} title={q.online ? "API conectada" : "API offline"}>
            {q.online ? "API online" : "API offline"}
          </span>
        </header>
        <div className="layout">
          <div className="layout-col">
            <UrlInput defaultFormat={q.config?.format} disabled={!q.online} onSubmit={q.add} />
          </div>
          <div className="layout-col">
            <QueueList
              jobs={q.jobs}
              downloadDir={q.config?.download_dir}
              onRetry={q.retry}
              onClear={q.clearFinished}
              onOpenFolder={q.openFolder}
            />
          </div>
        </div>
      </main>
    </>
  );
}
