import { Link } from "react-router-dom";
import type { VideoJob } from "../types";
import StatusBadge from "./StatusBadge";

export default function JobTable({ jobs }: { jobs: VideoJob[] }) {
  if (!jobs.length) return <div className="empty">No jobs yet.</div>;
  return (
    <div className="table-wrap">
      <table>
        <thead><tr><th>Video</th><th>Status</th><th>Stage</th><th>Progress</th><th>Views</th><th>Created</th></tr></thead>
        <tbody>
          {jobs.map(job => (
            <tr key={job.id}>
              <td><Link className="title-link" to={`/jobs/${job.id}`}>{job.title}</Link></td>
              <td><StatusBadge status={job.status} /></td>
              <td>{job.stage}</td>
              <td>
                <div className="mini-progress"><span style={{ width: `${job.progress}%` }} /></div>
                <small>{job.progress}%</small>
              </td>
              <td>{job.views.toLocaleString()}</td>
              <td>{new Date(job.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
