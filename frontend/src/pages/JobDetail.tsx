import { FormEvent, useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { api } from "../api";
import StatusBadge from "../components/StatusBadge";

export default function JobDetail() {
  const { id = "" } = useParams();
  const client = useQueryClient();
  const jobQuery = useQuery({
  queryKey: ["job", id],
  queryFn: () => api.job(id),

  refetchInterval: query => {
    const status = query.state.data?.status;

    if (
      status === "completed" ||
      status === "failed" ||
      status === "cancelled" ||
      status === "awaiting_approval"
    ) {
      return false;
    }

    return 1500;
  },
});
  const job = jobQuery.data;
  const [script, setScript] = useState("");
  const [uploadStatus, setUploadStatus] = useState("not_uploaded");
  const [platformUrl, setPlatformUrl] = useState("");
  const [views, setViews] = useState(0);

  useEffect(() => {
    if (!job) return;
    setScript(job.approved_script || job.script || "");
    setUploadStatus(job.upload_status);
    setPlatformUrl(job.platform_url || "");
    setViews(job.views);
  }, [job?.id, job?.script, job?.approved_script, job?.upload_status, job?.platform_url, job?.views]);

  const approve = useMutation({
    mutationFn: () => api.approve(id, script),
    onSuccess: () => client.invalidateQueries({ queryKey: ["job", id] }),
  });
  const cancel = useMutation({
    mutationFn: () => api.cancel(id),
    onSuccess: () => client.invalidateQueries({ queryKey: ["job", id] }),
  });
  const publication = useMutation({
    mutationFn: () => api.updatePublication(id, { upload_status: uploadStatus, platform_url: platformUrl || null, views }),
    onSuccess: () => client.invalidateQueries({ queryKey: ["job", id] }),
  });

  if (jobQuery.isLoading) return <div className="panel">Loading job…</div>;
  if (!job) return <div className="error">Job not found.</div>;

  return (
    <>
      <header className="page-header">
        <div><p className="eyebrow">Video job</p><h1>{job.title}</h1><div className="meta"><StatusBadge status={job.status} /><span>{new Date(job.created_at).toLocaleString()}</span></div></div>
        {job.output_video && <a className="button primary" href={`/api/jobs/${id}/video`}>Download MP4</a>}
      </header>

      <section className="panel">
        <div className="progress-header"><strong>{job.stage}</strong><span>{job.progress}%</span></div>
        <div className="progress"><span style={{ width: `${job.progress}%` }} /></div>
        {job.error && <div className="error">{job.error}</div>}
      </section>

      {job.status === "awaiting_approval" && (
        <section className="panel">
          <h2>Review narration script</h2>
          <p>This is the last checkpoint before ElevenLabs credits and rendering are used.</p>
          <textarea className="script-editor" rows={18} value={script} onChange={e => setScript(e.target.value)} />
          {approve.isError && <div className="error">{(approve.error as Error).message}</div>}
          <div className="actions"><button className="button primary" onClick={() => approve.mutate()} disabled={approve.isPending || script.trim().length < 20}>Approve and render</button></div>
        </section>
      )}

      {job.output_video && (
        <section className="panel">
          <h2>Preview</h2>
          <video className="video-preview" controls src={`/api/jobs/${id}/video`} />
        </section>
      )}

      <section className="two-column">
        <article className="panel">
          <h2>Process log</h2>
          <pre className="logs">{job.logs || "No log entries."}</pre>
          {!["completed", "failed", "cancelled"].includes(job.status) && job.status !== "awaiting_approval" &&
            <button className="button danger" onClick={() => cancel.mutate()}>Cancel job</button>}
        </article>

        <article className="panel">
          <h2>Publication tracking</h2>
          <div className="field"><label>Status</label><select value={uploadStatus} onChange={e => setUploadStatus(e.target.value)}><option value="not_uploaded">Not uploaded</option><option value="scheduled">Scheduled</option><option value="uploaded">Uploaded</option></select></div>
          <div className="field"><label>TikTok URL</label><input value={platformUrl} onChange={e => setPlatformUrl(e.target.value)} placeholder="https://www.tiktok.com/..." /></div>
          <div className="field"><label>Views</label><input type="number" min={0} value={views} onChange={e => setViews(Number(e.target.value))} /></div>
          <button className="button" onClick={() => publication.mutate()}>Save publication data</button>
        </article>
      </section>
    </>
  );
}
