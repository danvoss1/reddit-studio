import {
  CheckCircle2,
  LockKeyhole,
  ShieldCheck,
  UploadCloud,
  UserCheck,
} from "lucide-react";


const integrationPoints = [
  {
    icon: UserCheck,
    title: "Login Kit authorization",
    description:
      "TikTok Login Kit is used to connect the creator's TikTok account through the official OAuth authorization flow.",
  },
  {
    icon: LockKeyhole,
    title: "Secure token handling",
    description:
      "Access and refresh tokens are handled by the private backend and are not placed in the public website.",
  },
  {
    icon: ShieldCheck,
    title: "Account information",
    description:
      "The basic account scope is used to identify and display the connected creator account inside Reddit Studio.",
  },
  {
    icon: UploadCloud,
    title: "Creator-initiated publishing",
    description:
      "The Content Posting API is used only after the creator reviews the completed video and explicitly initiates publishing.",
  },
];


export default function TikTokIntegration() {
  return (
    <>
      <section className="public-page-hero">
        <div className="public-container">
          <p className="public-eyebrow">
            TikTok integration
          </p>

          <h1>
            Authorized and
            creator-controlled publishing
          </h1>

          <p>
            Reddit Studio uses TikTok Login
            Kit and the Content Posting API to
            connect an authorized creator
            account and publish reviewed video
            content.
          </p>
        </div>
      </section>

      <section className="public-section">
        <div className="public-container">
          <div className="public-card-grid">
            {integrationPoints.map(point => {
              const Icon =
                point.icon;

              return (
                <article
                  className="public-feature-card"
                  key={point.title}
                >
                  <div className="public-icon-box">
                    <Icon size={24} />
                  </div>

                  <h2>
                    {point.title}
                  </h2>

                  <p>
                    {point.description}
                  </p>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      <section className="public-section public-section-muted">
        <div className="public-container public-two-column">
          <div className="public-product-preview">
            <img
              src="/screenshots/tiktok-account.png"
              alt="Connected TikTok account in Reddit Studio"
            />
          </div>

          <div>
            <p className="public-eyebrow">
              Clear account identity
            </p>

            <h2>
              See which account is connected
            </h2>

            <p>
              After authorization, Reddit
              Studio displays the connected
              account name, avatar and granted
              permissions. The creator can
              disconnect the account from the
              integration page.
            </p>
          </div>
        </div>
      </section>

      <section className="public-section">
        <div className="public-container public-two-column">
          <div>
            <p className="public-eyebrow">
              Explicit confirmation
            </p>

            <h2>
              Publishing settings remain
              visible before posting
            </h2>

            <ul className="public-check-list">
              <li>
                <CheckCircle2 size={19} />

                Caption and hashtags can be
                reviewed.
              </li>

              <li>
                <CheckCircle2 size={19} />

                Available privacy options are
                selected by the creator.
              </li>

              <li>
                <CheckCircle2 size={19} />

                Platform options are presented
                before publishing.
              </li>

              <li>
                <CheckCircle2 size={19} />

                The MP4 is uploaded only after
                explicit confirmation.
              </li>
            </ul>
          </div>

          <div className="public-product-preview">
            <img
              src="/screenshots/tiktok-publishing.png"
              alt="TikTok publishing controls in Reddit Studio"
            />
          </div>
        </div>
      </section>

      <section className="public-section public-disclaimer">
        <div className="public-container">
          <h2>
            Platform relationship
          </h2>

          <p>
            Reddit Studio is an independent
            creator application. It is not
            owned by, endorsed by or affiliated
            with TikTok. TikTok is a trademark
            of its respective owner.
          </p>
        </div>
      </section>
    </>
  );
}