import {
  useEffect,
  useState,
} from "react";


const LOCAL_CALLBACK =
  "http://127.0.0.1:8000/api/tiktok/callback";


export default function TikTokCallback() {
  const [
    error,
    setError,
  ] = useState("");

  useEffect(() => {
    const params =
      new URLSearchParams(
        window.location.search,
      );

    const hasOAuthResult =
      params.has("code")
      || params.has("error");

    if (!hasOAuthResult) {
      setError(
        "TikTok did not return an authorization result.",
      );

      return;
    }

    window.location.replace(
      `${LOCAL_CALLBACK}?${params.toString()}`,
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
          Returning to the local
          Reddit Studio backend.
          Keep Reddit Studio running
          on this computer.
        </p>
      )}
    </section>
  );
}
