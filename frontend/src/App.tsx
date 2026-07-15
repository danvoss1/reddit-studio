import { NavLink, Route, Routes } from "react-router-dom";
import { Clapperboard, FileClock, Gauge, PlusCircle, Upload } from "lucide-react";
import Dashboard from "./pages/Dashboard";
import NewVideo from "./pages/NewVideo";
import JobDetail from "./pages/JobDetail";
import History from "./pages/History";
import Assets from "./pages/Assets";

const navigation = [
  ["/", "Dashboard", Gauge],
  ["/new", "New video", PlusCircle],
  ["/history", "History", FileClock],
  ["/assets", "Assets", Upload],
] as const;

export default function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><Clapperboard size={25} /> Reddit Studio</div>
        <nav>
          {navigation.map(([to, label, Icon]) => (
            <NavLink key={to} to={to} end={to === "/"}>
              <Icon size={18} /> {label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-note">Local creator workspace</div>
      </aside>
      <main className="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/new" element={<NewVideo />} />
          <Route path="/jobs/:id" element={<JobDetail />} />
          <Route path="/history" element={<History />} />
          <Route path="/assets" element={<Assets />} />
        </Routes>
      </main>
    </div>
  );
}
