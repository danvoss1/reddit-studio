import {
  Navigate,
  NavLink,
  Route,
  Routes,
} from "react-router-dom";

import {
  Clapperboard,
  FileClock,
  Gauge,
  PlusCircle,
  Upload,
  Video,
} from "lucide-react";

import Assets from "./pages/Assets";
import Dashboard from "./pages/Dashboard";
import History from "./pages/History";
import JobDetail from "./pages/JobDetail";
import NewVideo from "./pages/NewVideo";
import Privacy from "./pages/Privacy";
import PublicLanding from "./pages/PublicLanding";
import Terms from "./pages/Terms";
import TikTokCallback from "./pages/TikTokCallback";
import TikTokSettings from "./pages/TikTokSettings";


const navigation = [
  [
    "/",
    "Dashboard",
    Gauge,
  ],
  [
    "/new",
    "New video",
    PlusCircle,
  ],
  [
    "/history",
    "History",
    FileClock,
  ],
  [
    "/assets",
    "Assets",
    Upload,
  ],
  [
    "/tiktok",
    "TikTok",
    Video,
  ],
] as const;


function PublicApp() {
  return (
    <main className="public-site">
      <Routes>
        <Route
          path="/"
          element={<PublicLanding />}
        />

        <Route
          path="/privacy"
          element={<Privacy />}
        />

        <Route
          path="/terms"
          element={<Terms />}
        />

        <Route
          path="/auth/tiktok/callback"
          element={<TikTokCallback />}
        />

        <Route
          path="*"
          element={<Navigate to="/" replace />}
        />
      </Routes>
    </main>
  );
}


function PrivateApp() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Clapperboard size={25} />
          Reddit Studio
        </div>

        <nav>
          {navigation.map(
            ([
              to,
              label,
              Icon,
            ]) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/"}
              >
                <Icon size={18} />
                {label}
              </NavLink>
            ),
          )}
        </nav>

        <div className="sidebar-note">
          Local creator workspace
        </div>
      </aside>

      <main className="main">
        <Routes>
          <Route
            path="/"
            element={<Dashboard />}
          />

          <Route
            path="/new"
            element={<NewVideo />}
          />

          <Route
            path="/jobs/:id"
            element={<JobDetail />}
          />

          <Route
            path="/history"
            element={<History />}
          />

          <Route
            path="/assets"
            element={<Assets />}
          />

          <Route
            path="/tiktok"
            element={<TikTokSettings />}
          />

          <Route
            path="/privacy"
            element={<Privacy />}
          />

          <Route
            path="/terms"
            element={<Terms />}
          />

          <Route
            path="/auth/tiktok/callback"
            element={<TikTokCallback />}
          />

          <Route
            path="*"
            element={<Navigate to="/" replace />}
          />
        </Routes>
      </main>
    </div>
  );
}


export default function App() {
  const configuredMode =
    import.meta.env.VITE_APP_MODE;

  const isPublicBuild =
    configuredMode === "public"
    || (
      import.meta.env.PROD
      && configuredMode !== "private"
    );

  return isPublicBuild
    ? <PublicApp />
    : <PrivateApp />;
}
