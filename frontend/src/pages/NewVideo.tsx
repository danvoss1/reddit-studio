import { FormEvent, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import type { VoiceKey } from "../types";

type SourceMode = "reddit_url" | "manual";

export default function NewVideo() {
  const navigate = useNavigate();

  const assets = useQuery({
    queryKey: ["assets"],
    queryFn: api.assets,
  });

  const voices = useQuery({
    queryKey: ["voices"],
    queryFn: api.voices,
  });

  const [mode, setMode] = useState<SourceMode>("reddit_url");
  const [url, setUrl] = useState("");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [gameplay, setGameplay] = useState("");
  const [music, setMusic] = useState("");
  const [banner, setBanner] = useState("");
  const [useMusic, setUseMusic] = useState(true);
  const [voiceKey, setVoiceKey] = useState<VoiceKey>("female");
  const [playbackSpeed, setPlaybackSpeed] = useState(1.2);

  const mutation = useMutation({
    mutationFn: api.createJob,
    onSuccess: job => navigate(`/jobs/${job.id}`),
  });

  const gameplayAssets =
    assets.data?.filter(asset => asset.kind === "gameplay") ?? [];
  const musicAssets =
    assets.data?.filter(asset => asset.kind === "music") ?? [];
  const bannerAssets =
    assets.data?.filter(asset => asset.kind === "banner") ?? [];
  const availableVoices = voices.data ?? [];

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    mutation.mutate({
      source_mode: mode,
      reddit_url: mode === "reddit_url" ? url.trim() : null,
      source_title: mode === "manual" ? title.trim() : null,
      source_body: mode === "manual" ? body : null,
      gameplay_asset: gameplay || null,
      music_asset: useMusic && music ? music : null,
      banner_asset: banner || null,
      use_music: useMusic,
      voice_key: voiceKey,
      playback_speed: playbackSpeed,
    });
  }

  const sourceIsValid =
    mode === "reddit_url"
      ? url.trim().length > 0
      : body.trim().length >= 20;

  const canSubmit =
    sourceIsValid &&
    gameplayAssets.length > 0 &&
    availableVoices.length > 0 &&
    !mutation.isPending;

  return (
    <>
      <header className="page-header">
        <div>
          <p className="eyebrow">Pipeline</p>
          <h1>Create a new video</h1>
        </div>
      </header>

      <form className="panel form-grid" onSubmit={submit}>
        <div className="field full">
          <label>Story source</label>
          <div className="segmented">
            <button
              type="button"
              className={mode === "reddit_url" ? "active" : ""}
              onClick={() => setMode("reddit_url")}
            >
              Reddit URL
            </button>
            <button
              type="button"
              className={mode === "manual" ? "active" : ""}
              onClick={() => setMode("manual")}
            >
              Paste story text manually
            </button>
          </div>
        </div>

        {mode === "reddit_url" ? (
          <div className="field full">
            <label htmlFor="url">Reddit story URL</label>
            <input
              id="url"
              type="url"
              required
              value={url}
              onChange={event => setUrl(event.target.value)}
              placeholder="https://www.reddit.com/r/..."
            />
          </div>
        ) : (
          <>
            <div className="field full">
              <label htmlFor="story-title">Story title</label>
              <input
                id="story-title"
                required
                value={title}
                onChange={event => setTitle(event.target.value)}
              />
            </div>
            <div className="field full">
              <label htmlFor="story-body">Story body</label>
              <textarea
                id="story-body"
                required
                minLength={20}
                rows={11}
                value={body}
                onChange={event => setBody(event.target.value)}
              />
              <small>{body.length.toLocaleString()} characters</small>
            </div>
          </>
        )}

        <div className="field">
          <label htmlFor="gameplay">Gameplay</label>
          <select
            id="gameplay"
            value={gameplay}
            onChange={event => setGameplay(event.target.value)}
          >
            <option value="">Choose randomly</option>
            {gameplayAssets.map(asset => (
              <option key={asset.id} value={asset.id}>
                {asset.original_name}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="voice">Narrator voice</label>
          <select
            id="voice"
            value={voiceKey}
            onChange={event =>
              setVoiceKey(event.target.value as VoiceKey)
            }
          >
            {availableVoices.map(voice => (
              <option key={voice.key} value={voice.key}>
                {voice.name}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="speed">Playback speed</label>
          <select
            id="speed"
            value={playbackSpeed}
            onChange={event =>
              setPlaybackSpeed(Number(event.target.value))
            }
          >
            <option value={1}>1.0×</option>
            <option value={1.1}>1.1×</option>
            <option value={1.2}>1.2×</option>
            <option value={1.3}>1.3×</option>
            <option value={1.5}>1.5×</option>
          </select>
        </div>

        <div className="field">
          <label htmlFor="banner">Opening banner</label>
          <select
            id="banner"
            value={banner}
            onChange={event => setBanner(event.target.value)}
          >
            <option value="">No banner</option>
            {bannerAssets.map(asset => (
              <option key={asset.id} value={asset.id}>
                {asset.original_name}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="music">Music</label>
          <select
            id="music"
            disabled={!useMusic}
            value={music}
            onChange={event => setMusic(event.target.value)}
          >
            <option value="">Choose randomly</option>
            {musicAssets.map(asset => (
              <option key={asset.id} value={asset.id}>
                {asset.original_name}
              </option>
            ))}
          </select>

          <label className="checkbox">
            <input
              type="checkbox"
              checked={useMusic}
              onChange={event => {
                setUseMusic(event.target.checked);
                if (!event.target.checked) setMusic("");
              }}
            />
            Add background music
          </label>
        </div>

        {mutation.isError && (
          <div className="error full">
            {(mutation.error as Error).message}
          </div>
        )}

        <div className="actions full">
          <button
            className="button primary"
            type="submit"
            disabled={!canSubmit}
          >
            {mutation.isPending ? "Starting…" : "Start pipeline"}
          </button>
        </div>
      </form>
    </>
  );
}
