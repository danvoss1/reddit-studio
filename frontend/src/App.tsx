import {
  Navigate,
  NavLink,
  Route,
  Routes,
} from "react-router-dom";

import {
  CalendarClock,
  Clapperboard,
  FileClock,
  Gauge,
  PlusCircle,
  Upload,
  Video,
} from "lucide-react";

import Assets from "./pages/Assets";
import Contact from "./pages/Contact";
import Dashboard from "./pages/Dashboard";
import FAQ from "./pages/FAQ";
import Features from "./pages/Features";
import History from "./pages/History";
import HowItWorks from "./pages/HowItWorks";
import JobDetail from "./pages/JobDetail";
import NewVideo from "./pages/NewVideo";
import Privacy from "./pages/Privacy";
import PublicLanding from "./pages/PublicLanding";
import PublicLayout from "./pages/PublicLayout";
import Terms from "./pages/Terms";
import TikTokCallback from "./pages/TikTokCallback";
import TikTokIntegration from "./pages/TikTokIntegration";
import TikTokSettings from "./pages/TikTokSettings";

import "./public-site.css";


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
  [
    "/schedule",
    "Schedule",
    CalendarClock,
  ],
] as const;


function PublicApp() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route
          path="/"
          element={<PublicLanding />}
        />

        <Route
          path="/features"
          element={<Features />}
        />

        <Route
          path="/how-it-works"
          element={<HowItWorks />}
        />

        <Route
          path="/tiktok-integration"
          element={<TikTokIntegration />}
        />

        <Route
          path="/faq"
          element={<FAQ />}
        />

        <Route
          path="/contact"
          element={<Contact />}
        />

        <Route
          path="/privacy"
          element={<Privacy />}
        />

        <Route
          path="/terms"
          element={<Terms />}
        />
      </Route>

      <Route
        path="/auth/tiktok/callback"
        element={<TikTokCallback />}
      />

      <Route
        path="*"
        element={
          <Navigate
            to="/"
            replace
          />
        }
      />
    </Routes>
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
          Creator workspace
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
            element={
              <Navigate
                to="/"
                replace
              />
            }
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