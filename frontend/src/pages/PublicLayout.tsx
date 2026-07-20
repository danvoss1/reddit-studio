import {
  Menu,
  X,
} from "lucide-react";

import {
  NavLink,
  Outlet,
} from "react-router-dom";

import {
  useState,
} from "react";


const links = [
  {
    to: "/features",
    label: "Features",
  },
  {
    to: "/how-it-works",
    label: "How it works",
  },
  {
    to: "/tiktok-integration",
    label: "TikTok integration",
  },
  {
    to: "/faq",
    label: "FAQ",
  },
  {
    to: "/contact",
    label: "Contact",
  },
];


export default function PublicLayout() {
  const [
    menuOpen,
    setMenuOpen,
  ] = useState(false);

  return (
    <div className="public-root">
      <header className="public-header">
        <div className="public-header-inner">
          <NavLink
            className="public-brand"
            to="/"
            onClick={() =>
              setMenuOpen(false)
            }
          >
            <img
              src="/reddit-studio-logo.png"
              alt="Reddit Studio"
              className="public-brand-logo"
            />

            <span>
              Reddit Studio
            </span>
          </NavLink>

          <button
            className="public-menu-button"
            type="button"
            aria-label={
              menuOpen
                ? "Close navigation"
                : "Open navigation"
            }
            onClick={() =>
              setMenuOpen(
                current => !current,
              )
            }
          >
            {menuOpen ? (
              <X size={24} />
            ) : (
              <Menu size={24} />
            )}
          </button>

          <nav
            className={
              menuOpen
                ? "public-navigation open"
                : "public-navigation"
            }
          >
            {links.map(link => (
              <NavLink
                key={link.to}
                to={link.to}
                onClick={() =>
                  setMenuOpen(false)
                }
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main>
        <Outlet />
      </main>

      <footer className="public-footer">
        <div className="public-footer-grid">
          <div>
            <div className="public-footer-brand">
              Reddit Studio
            </div>

            <p>
              A creator-focused application
              for producing narrated
              short-form videos and
              publishing completed content
              through authorized platform
              integrations.
            </p>
          </div>

          <div>
            <h3>
              Product
            </h3>

            <NavLink to="/features">
              Features
            </NavLink>

            <NavLink to="/how-it-works">
              How it works
            </NavLink>

            <NavLink to="/tiktok-integration">
              TikTok integration
            </NavLink>
          </div>

          <div>
            <h3>
              Support
            </h3>

            <NavLink to="/faq">
              FAQ
            </NavLink>

            <NavLink to="/contact">
              Contact
            </NavLink>
          </div>

          <div>
            <h3>
              Legal
            </h3>

            <NavLink to="/privacy">
              Privacy Policy
            </NavLink>

            <NavLink to="/terms">
              Terms of Service
            </NavLink>
          </div>
        </div>

        <div className="public-footer-bottom">
          <span>
            © 2026 Reddit Studio
          </span>

          <span>
            Independent creator software.
            Not affiliated with Reddit or
            TikTok.
          </span>
        </div>
      </footer>
    </div>
  );
}