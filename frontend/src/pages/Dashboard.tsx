import { useQuery } from "@tanstack/react-query";
import { api } from "../api";
import JobTable from "../components/JobTable";

export default function Dashboard() {
  const stats = useQuery({ queryKey: ["stats"], queryFn: api.stats, refetchInterval: 2000 });
  const jobs = useQuery({ queryKey: ["jobs"], queryFn: api.jobs, refetchInterval: 2000 });
  const cards = [
    ["Total videos", stats.data?.total ?? 0],
    ["In progress", (stats.data?.queued ?? 0) + (stats.data?.running ?? 0)],
    ["Need approval", stats.data?.awaiting_approval ?? 0],
    ["Completed", stats.data?.completed ?? 0],
    ["Uploaded", stats.data?.uploaded ?? 0],
    ["Total views", (stats.data?.total_views ?? 0).toLocaleString()],
  ];

  return (
    <>
      <header className="page-header">
        <div><p className="eyebrow">Overview</p><h1>Creator dashboard</h1></div>
        <a className="button primary" href="/new">Create video</a>
      </header>
      <section className="stats-grid">
        {cards.map(([label, value]) => <article className="stat-card" key={label}><span>{label}</span><strong>{value}</strong></article>)}
      </section>
      <section className="panel">
        <div className="panel-heading"><div><h2>Recent jobs</h2><p>Automatically refreshes while jobs are active.</p></div></div>
        {jobs.isError ? <div className="error">{(jobs.error as Error).message}</div> : <JobTable jobs={jobs.data?.slice(0, 8) ?? []} />}
      </section>
    </>
  );
}
