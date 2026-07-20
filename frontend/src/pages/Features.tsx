import {
  Captions,
  Film,
  Image,
  ListChecks,
  Mic2,
  Music,
  SlidersHorizontal,
  UploadCloud,
} from "lucide-react";


const featureGroups = [
  {
    icon: Film,
    title: "Story preparation",
    description:
      "Creators can provide story text manually or use a supported source URL. The story remains available for review before rendering begins.",
  },
  {
    icon: Mic2,
    title: "Selectable narration",
    description:
      "Choose between configured male and female narrator voices. Narration is generated for the approved story script.",
  },
  {
    icon: Captions,
    title: "Timed subtitles",
    description:
      "Reddit Studio generates synchronized subtitles designed for vertical short-form video and mobile readability.",
  },
  {
    icon: Image,
    title: "Reusable visual assets",
    description:
      "Upload and manage gameplay footage and visual banner assets for repeated use across video projects.",
  },
  {
    icon: Music,
    title: "Optional background audio",
    description:
      "Creators can choose whether to include background music and select an available audio asset.",
  },
  {
    icon: SlidersHorizontal,
    title: "Video customization",
    description:
      "Configure voice, playback speed, gameplay footage, music and title-banner settings before generation.",
  },
  {
    icon: ListChecks,
    title: "Review and approval",
    description:
      "The story script and completed output can be inspected before progressing to publishing.",
  },
  {
    icon: UploadCloud,
    title: "Authorized TikTok publishing",
    description:
      "After connecting TikTok with OAuth, the creator reviews the caption, privacy setting and posting controls before publishing.",
  },
];


export default function Features() {
  return (
    <>
      <section className="public-page-hero">
        <div className="public-container">
          <p className="public-eyebrow">
            Product features
          </p>

          <h1>
            A complete short-form video
            production workflow
          </h1>

          <p>
            Reddit Studio combines the core
            stages of narrated video
            production in one creator-focused
            workspace.
          </p>
        </div>
      </section>

      <section className="public-section">
        <div className="public-container">
          <div className="public-card-grid">
            {featureGroups.map(feature => {
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

                  <h2>
                    {feature.title}
                  </h2>

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
          <div className="public-product-preview">
            <img
              src="/screenshots/new-video.png"
              alt="New video settings in Reddit Studio"
            />
          </div>

          <div>
            <p className="public-eyebrow">
              Configurable production
            </p>

            <h2>
              Prepare each video for its
              intended story
            </h2>

            <p>
              Each job keeps its selected
              narration, playback, gameplay,
              music and visual settings
              together. This makes the result
              reproducible and easier to
              review.
            </p>
          </div>
        </div>
      </section>

      <section className="public-section">
        <div className="public-container public-two-column">
          <div>
            <p className="public-eyebrow">
              Transparent job progress
            </p>

            <h2>
              Follow generation from approval
              to completion
            </h2>

            <p>
              Job pages show progress,
              processing logs and the current
              stage of the video pipeline.
              Completed videos can be previewed
              before publishing.
            </p>
          </div>

          <div className="public-product-preview">
            <img
              src="/screenshots/job-progress.png"
              alt="Video generation progress in Reddit Studio"
            />
          </div>
        </div>
      </section>
    </>
  );
}