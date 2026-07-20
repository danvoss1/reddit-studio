import {
  Mail,
} from "lucide-react";


const CONTACT_EMAIL =
  "voss.daniel.cgn@gmail.com";


export default function Contact() {
  return (
    <>
      <section className="public-page-hero">
        <div className="public-container">
          <p className="public-eyebrow">
            Contact
          </p>

          <h1>
            Contact Reddit Studio
          </h1>

          <p>
            Questions about the product,
            privacy or platform integration can
            be sent by email.
          </p>
        </div>
      </section>

      <section className="public-section">
        <div className="public-container">
          <div className="public-contact-card">
            <div className="public-icon-box">
              <Mail size={25} />
            </div>

            <div>
              <h2>
                Email support
              </h2>

              <p>
                For product, account, privacy
                or developer-integration
                inquiries:
              </p>

              <a
                href={`mailto:${CONTACT_EMAIL}`}
              >
                {CONTACT_EMAIL}
              </a>
            </div>
          </div>

          <p className="public-contact-note">
            Please do not send passwords,
            access tokens, API keys or other
            sensitive credentials by email.
          </p>
        </div>
      </section>
    </>
  );
}