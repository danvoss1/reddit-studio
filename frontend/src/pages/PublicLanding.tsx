import {
  ArrowRight,
  Captions,
  CheckCircle2,
  Film,
  LockKeyhole,
  Mic2,
  SlidersHorizontal,
  UploadCloud,
} from "lucide-react";

import {
  Link,
} from "react-router-dom";


const features = [
  {
    icon: Film,
    title: "Story-based video creation",
    description:
      "Prepare user-selected stories for vertical short-form video production.",
  },
  {
    icon: Mic2,
    title: "Natural narration",
    description:
      "Generate spoken narration with selectable male and female voices.",
  },
  {
    icon: Captions,
    title: "Synchronized captions",
    description:
      "Create timed, word-focused subtitles designed for mobile viewing.",
  },
  {
    icon: SlidersHorizontal,
    title: "Creator-controlled settings",
    description:
      "Select gameplay, music, narration voice, banners and playback speed.",
  },
  {
    icon: UploadCloud,
    title: "TikTok publishing",
    description:
      "Review the finished video and publishing details before sending it to TikTok.",
  },
  {
    icon: LockKeyhole,
    title: "Secure architecture",
    description:
      "Operational credentials and creator tools remain outside the public website.",
  },
];


const workflow = [
  "Add or import a story",
  "Choose narration and video settings",
  "Generate and review the finished video",
  "Connect an authorized TikTok account",
  "Review caption and privacy settings",
  "Publish only after explicit confirmation",
];


export default function PublicLanding() {
  return (
    <>
      <section className="public-hero">
        <div className="public-container public-hero-grid">
          <div>
            <p className="public-eyebrow">
              Creator video production
            </p>

            <h1>
              Turn stories into narrated
              short-form videos
            </h1>

            <p className="public-hero-copy">
              Reddit Studio brings story
              preparation, narration,
              synchronized captions, vertical
              video composition and TikTok
              publishing into one structured
              creator workflow.
            </p>

            <div className="public-actions">
              <Link
                className="public-button primary"
                to="/features"
              >
                Explore features

                <ArrowRight size={18} />
              </Link>

              <Link
                className="public-button secondary"
                to="/how-it-works"
              >
                See how it works
              </Link>
            </div>

            <div className="public-trust-row">
              <span>
                <CheckCircle2 size={17} />

                Creator review before publishing
              </span>

              <span>
                <CheckCircle2 size={17} />

                OAuth account connection
              </span>

              <span>
                <CheckCircle2 size={17} />

                Explicit publish confirmation
              </span>
            </div>
          </div>

          <div className="public-product-preview">
            <img
              src="/screenshots/dashboard.png"
              alt="Reddit Studio creator dashboard"
            />
          </div>
        </div>
      </section>

      <section className="public-section">
        <div className="public-container">
          <div className="public-section-heading">
            <p className="public-eyebrow">
              One connected workflow
            </p>

            <h2>
              Tools for every stage of
              short-form production
            </h2>

            <p>
              Reddit Studio helps creators
              move from source text to a
              reviewed and publishable vertical
              video without switching between
              several disconnected tools.
            </p>
          </div>

          <div className="public-card-grid">
            {features.map(feature => {
              const Icon =
                feature.icon;

              return (
                <article
                  className="public-feature-card"
                  key={feature.title}
                >
                  <div className="public-icon-box">
                    <Icon size={24} />
                  </div>

                  <h3>
                    {feature.title}
                  </h3>

                  <p>
                    {feature.description}
                  </p>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      <section className="public-section public-section-muted">
        <div className="public-container public-two-column">
          <div>
            <p className="public-eyebrow">
              Creator-controlled publishing
            </p>

            <h2>
              Review every video before it
              leaves the application
            </h2>

            <p>
              The creator can inspect the
              generated video, edit its caption,
              choose an available privacy
              setting and confirm platform
              options before publishing.
            </p>

            <Link
              className="public-text-link"
              to="/tiktok-integration"
            >
              Learn about the TikTok
              integration

              <ArrowRight size={17} />
            </Link>
          </div>

          <div className="public-product-preview">
            <img
              src="/screenshots/tiktok-publishing.png"
              alt="TikTok publishing settings in Reddit Studio"
            />
          </div>
        </div>
      </section>

      <section className="public-section">
        <div className="public-container">
          <div className="public-section-heading">
            <p className="public-eyebrow">
              How it works
            </p>

            <h2>
              From selected story to completed
              video
            </h2>
          </div>

          <div className="public-workflow">
            {workflow.map(
              (
                item,
                index,
              ) => (
                <article
                  key={item}
                  className="public-workflow-step"
                >
                  <span>
                    {index + 1}
                  </span>

                  <p>
                    {item}
                  </p>
                </article>
              ),
            )}
          </div>

          <div className="public-centered-action">
            <Link
              className="public-button secondary"
              to="/how-it-works"
            >
              View the complete workflow
            </Link>
          </div>
        </div>
      </section>

      <section className="public-section public-final-cta">
        <div className="public-container">
          <div>
            <p className="public-eyebrow">
              Reddit Studio
            </p>

            <h2>
              A structured production
              workspace for short-form
              creators
            </h2>

            <p>
              Explore the product, its workflow
              and the way authorized TikTok
              publishing is handled.
            </p>
          </div>

          <div className="public-actions">
            <Link
              className="public-button primary"
              to="/features"
            >
              View features
            </Link>

            <Link
              className="public-button secondary"
              to="/contact"
            >
              Contact
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}