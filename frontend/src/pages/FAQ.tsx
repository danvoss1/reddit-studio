const questions = [
  {
    question:
      "Does Reddit Studio publish videos automatically?",
    answer:
      "A completed video is not published merely because it has been generated. The creator reviews the video and publishing settings before explicitly initiating the TikTok publishing action.",
  },
  {
    question:
      "Can I review the video before publishing?",
    answer:
      "Yes. Completed jobs include the rendered video and publishing controls so the creator can inspect the output first.",
  },
  {
    question:
      "How is a TikTok account connected?",
    answer:
      "TikTok Login Kit is used to authorize the account through OAuth. Reddit Studio does not ask the creator to enter a TikTok password directly.",
  },
  {
    question:
      "Can the TikTok account be disconnected?",
    answer:
      "Yes. The connected account can be disconnected from the TikTok integration page.",
  },
  {
    question:
      "Are API credentials stored in the public website?",
    answer:
      "No. The public product website does not contain the operational creator workspace or private service credentials.",
  },
  {
    question:
      "Does Reddit Studio support different narrator voices?",
    answer:
      "The creator can select from configured male and female narration voices before generating the video.",
  },
  {
    question:
      "Can background music be disabled?",
    answer:
      "Yes. Background music is optional and can be disabled for an individual video.",
  },
  {
    question:
      "Can I use my own gameplay footage?",
    answer:
      "Gameplay footage can be uploaded to the creator workspace and selected for a video job.",
  },
];


export default function FAQ() {
  return (
    <>
      <section className="public-page-hero">
        <div className="public-container">
          <p className="public-eyebrow">
            Frequently asked questions
          </p>

          <h1>
            Questions about Reddit Studio
          </h1>

          <p>
            Learn how video generation,
            account connection and publishing
            work.
          </p>
        </div>
      </section>

      <section className="public-section">
        <div className="public-container public-faq-list">
          {questions.map(item => (
            <details
              key={item.question}
              className="public-faq-item"
            >
              <summary>
                {item.question}
              </summary>

              <p>
                {item.answer}
              </p>
            </details>
          ))}
        </div>
      </section>
    </>
  );
}