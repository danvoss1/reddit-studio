import {
  useEffect,
} from "react";

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  useSearchParams,
} from "react-router-dom";

import {
  api,
} from "../api";


export default function TikTokSettings() {
  const client =
    useQueryClient();

  const [
    searchParams,
    setSearchParams,
  ] = useSearchParams();

  const account = useQuery({
    queryKey: [
      "tiktok-account",
    ],
    queryFn:
      api.tiktokAccount,
  });

  const connect = useMutation({
    mutationFn:
      api.connectTikTok,

    onSuccess: data => {
      window.location.assign(
        data.authorization_url,
      );
    },
  });

  const disconnect =
    useMutation({
      mutationFn:
        api.disconnectTikTok,

      onSuccess: () => {
        client.invalidateQueries({
          queryKey: [
            "tiktok-account",
          ],
        });
      },
    });

  useEffect(() => {
    if (
      searchParams.get(
        "connected",
      ) === "1"
    ) {
      client.invalidateQueries({
        queryKey: [
          "tiktok-account",
        ],
      });

      setSearchParams({});
    }
  }, [
    client,
    searchParams,
    setSearchParams,
  ]);

  const callbackError =
    searchParams.get(
      "tiktok_error",
    );

  return (
    <>
      <header className="page-header">
        <div>
          <p className="eyebrow">
            Integration
          </p>

          <h1>
            TikTok account
          </h1>
        </div>
      </header>

      <section className="panel">
        {callbackError && (
          <div className="error">
            {callbackError}
          </div>
        )}

        {account.isLoading && (
          <p>
            Checking TikTok
            connection…
          </p>
        )}

        {account.isError && (
          <div className="error">
            {
              (
                account.error
                as Error
              ).message
            }
          </div>
        )}

        {account.data?.connected ? (
          <>
            <div className="meta">
              {account.data
                .avatar_url && (
                <img
                  src={
                    account.data
                      .avatar_url
                  }
                  alt=""
                  width={64}
                  height={64}
                  style={{
                    borderRadius:
                      "50%",
                  }}
                />
              )}

              <div>
                <strong>
                  {
                    account.data
                      .display_name
                    ?? "Connected TikTok account"
                  }
                </strong>

                <p>
                  TikTok is connected
                  and ready for
                  uploads.
                </p>
              </div>
            </div>

            <button
              className="button danger"
              type="button"
              disabled={
                disconnect.isPending
              }
              onClick={() =>
                disconnect.mutate()
              }
            >
              {
                disconnect.isPending
                  ? "Disconnecting…"
                  : "Disconnect TikTok"
              }
            </button>
          </>
        ) : (
          <>
            <p>
              Connect the TikTok account
              that should receive the
              rendered videos.
            </p>

            <button
              className="button primary"
              type="button"
              disabled={
                connect.isPending
              }
              onClick={() =>
                connect.mutate()
              }
            >
              {
                connect.isPending
                  ? "Opening TikTok…"
                  : "Connect TikTok"
              }
            </button>
          </>
        )}

        {connect.isError && (
          <div className="error">
            {
              (
                connect.error
                as Error
              ).message
            }
          </div>
        )}

        {disconnect.isError && (
          <div className="error">
            {
              (
                disconnect.error
                as Error
              ).message
            }
          </div>
        )}
      </section>
    </>
  );
}
