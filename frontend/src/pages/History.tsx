import { useQuery } from "@tanstack/react-query";
import { api } from "../api";
import JobTable from "../components/JobTable";

export default function History() {
  const jobs = useQuery({ queryKey: ["jobs"], queryFn: api.jobs, refetchInterval: 3000 });
  return (
    <>
      <header className="page-header"><div><p className="eyebrow">Archive</p><h1>Video history</h1></div></header>
      <section className="panel">
        {jobs.isError ? <div className="error">{(jobs.error as Error).message}</div> : <JobTable jobs={jobs.data ?? []} />}
      </section>
    </>
  );
}
