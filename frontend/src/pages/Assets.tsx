import { FormEvent, useState } from "react";
import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { api } from "../api";

type AssetKind = "gameplay" | "music" | "banner";

function formatBytes(bytes: number) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, index)).toFixed(1)} ${units[index]}`;
}

export default function Assets() {
  const client = useQueryClient();
  const assets = useQuery({
    queryKey: ["assets"],
    queryFn: api.assets,
  });

  const [kind, setKind] = useState<AssetKind>("gameplay");
  const [file, setFile] = useState<File | null>(null);

  const upload = useMutation({
    mutationFn: () => api.uploadAsset(kind, file!),
    onSuccess: () => {
      setFile(null);
      client.invalidateQueries({ queryKey: ["assets"] });
    },
  });

  const remove = useMutation({
    mutationFn: api.deleteAsset,
    onSuccess: () =>
      client.invalidateQueries({ queryKey: ["assets"] }),
  });

  function submit(event: FormEvent) {
    event.preventDefault();
    if (file) upload.mutate();
  }

  const accept =
    kind === "gameplay"
      ? "video/*"
      : kind === "music"
        ? "audio/*"
        : "image/png,image/webp";

  return (
    <>
      <header className="page-header">
        <div>
          <p className="eyebrow">Media library</p>
          <h1>Gameplay, music and banners</h1>
        </div>
      </header>

      <form className="panel upload-form" onSubmit={submit}>
        <div className="field">
          <label>Asset type</label>
          <select
            value={kind}
            onChange={event => {
              setKind(event.target.value as AssetKind);
              setFile(null);
            }}
          >
            <option value="gameplay">Gameplay video</option>
            <option value="music">Background music</option>
            <option value="banner">Opening banner</option>
          </select>
        </div>

        <div className="field">
          <label>File</label>
          <input
            key={kind}
            type="file"
            required
            accept={accept}
            onChange={event =>
              setFile(event.target.files?.[0] ?? null)
            }
          />
        </div>

        <button
          className="button primary"
          disabled={!file || upload.isPending}
        >
          {upload.isPending ? "Uploading…" : "Upload asset"}
        </button>
      </form>

      <section className="panel">
        <h2>Available assets</h2>
        <div className="asset-grid">
          {(assets.data ?? []).map(asset => (
            <article className="asset-card" key={asset.id}>
              <span className="asset-kind">{asset.kind}</span>
              <strong>{asset.original_name}</strong>
              <small>{formatBytes(asset.size_bytes)}</small>
              <button
                className="text-danger"
                onClick={() => remove.mutate(asset.id)}
              >
                Delete
              </button>
            </article>
          ))}
        </div>
      </section>
    </>
  );
}
