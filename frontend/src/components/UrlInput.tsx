import { useEffect, useMemo, useState } from "react";
import type { AudioFormat } from "../api";

const YT_RE = /(youtube\.com\/(watch\?.*v=|shorts\/|embed\/)|youtu\.be\/)[\w-]{11}|youtube\.com\/.*[?&]list=[\w-]+/;
const isPlaylist = (u: string) => /[?&]list=/.test(u) && !/(v=|youtu\.be\/|shorts\/)/.test(u);

interface Props {
  defaultFormat?: AudioFormat;
  disabled?: boolean;
  onSubmit: (urls: string[], fmt: AudioFormat) => Promise<unknown>;
}

export default function UrlInput({ defaultFormat = "mp3", disabled, onSubmit }: Props) {
  const [text, setText] = useState("");
  const [fmt, setFmt] = useState<AudioFormat>(defaultFormat);
  const [busy, setBusy] = useState(false);

  useEffect(() => setFmt(defaultFormat), [defaultFormat]);

  const urls = useMemo(() => text.split(/\s+/).filter((u) => YT_RE.test(u)), [text]);

  const submit = async () => {
    setBusy(true);
    try {
      await onSubmit(urls, fmt);
      setText("");
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="card" aria-labelledby="input-title">
      <h2 id="input-title">URLs</h2>
      <textarea
        id="url-input"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={"https://www.youtube.com/watch?v=...\nhttps://www.youtube.com/playlist?list=...\n(uma por linha)"}
        spellCheck={false}
      />
      <div className="row">
        <span className="muted">
          {urls.length} URL{urls.length === 1 ? "" : "s"} válida{urls.length === 1 ? "" : "s"}
          {urls.some(isPlaylist) && ` · ${urls.filter(isPlaylist).length} playlist(s)`}
        </span>
        <div className="right">
          <div className="segmented" role="radiogroup" aria-label="Formato">
            {(["m4a", "mp3"] as const).map((f) => (
              <button key={f} id={`fmt-${f}`} className={fmt === f ? "active" : ""} onClick={() => setFmt(f)} role="radio" aria-checked={fmt === f}>
                {f.toUpperCase()}
              </button>
            ))}
          </div>
          <button id="btn-download" className="btn primary" disabled={!urls.length || busy || disabled} onClick={submit}>
            {busy ? "Enviando…" : "Baixar"}
          </button>
        </div>
      </div>
    </section>
  );
}
