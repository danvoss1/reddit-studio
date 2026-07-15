import {
  useEffect,
  useState,
} from "react";


const LOCAL_BACKEND_CALLBACK =
  "http://127.0.0.1:8000/api/tiktok/callback";


export default function TikTokCallback() {
  const [
    error,
    setError,
  ] = useState("");

  useEffect(() => {
    const queryString =
      window.location.search;

    const params =
      new URLSearchParams(
        queryString,
      );

    const hasAuthorizationCode =
      params.has("code");

    const hasOAuthError =
      params.has("error");

    if (
      !hasAuthorizationCode
      && !hasOAuthError
    ) {
      setError(
        "No TikTok authorization result was supplied. "
        + "This page is only used after authorizing Reddit Studio on TikTok.",
      );

      return;
    }

    window.location.replace(
      `${LOCAL_BACKEND_CALLBACK}${queryString}`,
    );
  }, []);

  return (
    <section className="panel">
      <p className="eyebrow">
        TikTok authorization
      </p>

      <h1>
        Connecting TikTok…
      </h1>

      {error ? (
        <div className="error">
          {error}
        </div>
      ) : (
        <p>
          TikTok authorization was
          received. Returning to the
          local Reddit Studio backend.
          Keep Reddit Studio and the
          FastAPI backend running on
          this computer.
        </p>
      )}
    </section>
  );
}