const steps = [
  {
    number: "01",
    title: "Add the story",
    description:
      "The creator provides story text manually or enters a supported story URL.",
  },
  {
    number: "02",
    title: "Choose production settings",
    description:
      "Select gameplay footage, narrator voice, playback speed, music and optional banner assets.",
  },
  {
    number: "03",
    title: "Review the story script",
    description:
      "The prepared script is shown for approval before narration and rendering continue.",
  },
  {
    number: "04",
    title: "Generate narration and subtitles",
    description:
      "Reddit Studio creates spoken narration and synchronized subtitle timing.",
  },
  {
    number: "05",
    title: "Render the vertical video",
    description:
      "Gameplay, narration, captions and selected visual elements are combined into the final MP4.",
  },
  {
    number: "06",
    title: "Inspect the completed output",
    description:
      "The creator reviews the finished video and can download it before any platform publishing occurs.",
  },
  {
    number: "07",
    title: "Review TikTok settings",
    description:
      "The creator edits the caption, selects an available privacy option and confirms relevant posting settings.",
  },
  {
    number: "08",
    title: "Publish explicitly",
    description:
      "The video is sent to the connected TikTok account only when the creator clicks the publish button.",
  },
];


export default function HowItWorks() {
  return (
    <>
      <section className="public-page-hero">
        <div className="public-container">
          <p className="public-eyebrow">
            Workflow
          </p>

          <h1>
            How Reddit Studio works
          </h1>

          <p>
            Each stage is visible and
            creator-controlled, from the
            initial story selection through
            final publishing.
          </p>
        </div>
      </section>

      <section className="public-section">
        <div className="public-container">
          <div className="public-timeline">
            {steps.map(step => (
              <article
                className="public-timeline-item"
                key={step.number}
              >
                <div className="public-timeline-number">
                  {step.number}
                </div>

                <div>
                  <h2>
                    {step.title}
                  </h2>

                  <p>
                    {step.description}
                  </p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="public-section public-section-muted">
        <div className="public-container public-two-column">
          <div>
            <p className="public-eyebrow">
              No silent publishing
            </p>

            <h2>
              The creator stays in control
            </h2>

            <p>
              Generating a video does not
              automatically publish it. The
              finished MP4, caption, privacy
              level and platform settings are
              presented before a separate
              publishing action is performed.
            </p>
          </div>

          <div className="public-product-preview">
            <img
              src="/screenshots/completed-video.png"
              alt="Completed Reddit Studio video preview"
            />
          </div>
        </div>
      </section>
    </>
  );
}