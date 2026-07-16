export default function PublicLanding() {
  return (
    <section
      className="panel legal-page"
      style={{
        maxWidth: 820,
        margin: "48px auto",
      }}
    >
      <p className="eyebrow">
        Reddit Studio
      </p>

      <h1>
        Narrated short-form story video creator
      </h1>

      <p>
        Reddit Studio helps an authorized creator produce narrated
        short-form story videos and publish completed videos to TikTok.
        The operational creator dashboard runs privately on the
        creator&apos;s own computer.
      </p>

      <p>
        <a href="/privacy">
          Privacy Policy
        </a>
        {" · "}
        <a href="/terms">
          Terms of Service
        </a>
      </p>
    </section>
  );
}
