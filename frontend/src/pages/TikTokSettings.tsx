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


function getErrorMessage(
  error: unknown,
): string {
  if (
    error instanceof Error
  ) {
    return error.message;
  }

  return (
    "An unknown error occurred."
  );
}


export default function TikTokSettings() {
  const queryClient =
    useQueryClient();

  const [
    searchParams,
    setSearchParams,
  ] = useSearchParams();

  const accountQuery =
    useQuery({
      queryKey: [
        "tiktok-account",
      ],

      queryFn:
        api.tiktokAccount,
    });

  const connectMutation =
    useMutation({
      mutationFn:
        api.connectTikTok,

      onSuccess: data => {
        window.location.assign(
          data.authorization_url,
        );
      },
    });

  const disconnectMutation =
    useMutation({
      mutationFn:
        api.disconnectTikTok,

      onSuccess: async () => {
        await queryClient
          .invalidateQueries({
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
      ) !== "1"
    ) {
      return;
    }

    void queryClient
      .invalidateQueries({
        queryKey: [
          "tiktok-account",
        ],
      });

    setSearchParams({});
  }, [
    queryClient,
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

        {accountQuery.isLoading && (
          <p>
            Checking TikTok
            connection…
          </p>
        )}

        {accountQuery.isError && (
          <div className="error">
            {getErrorMessage(
              accountQuery.error,
            )}
          </div>
        )}

        {accountQuery.data
          ?.connected ? (
            <>
              <div className="meta">
                {accountQuery.data
                  .avatar_url && (
                    <img
                      src={
                        accountQuery
                          .data
                          .avatar_url
                      }
                      alt={
                        "Connected TikTok account"
                      }
                      width={64}
                      height={64}
                      style={{
                        borderRadius:
                          "50%",

                        objectFit:
                          "cover",
                      }}
                    />
                  )}

                <div>
                  <strong>
                    {
                      accountQuery
                        .data
                        .display_name
                      ?? "Connected TikTok account"
                    }
                  </strong>

                  <p>
                    TikTok is connected
                    and ready for
                    uploads.
                  </p>

                  {accountQuery.data
                    .scope && (
                      <small>
                        Authorized
                        scopes:{" "}
                        {
                          accountQuery
                            .data
                            .scope
                        }
                      </small>
                    )}
                </div>
              </div>

              <div className="actions">
                <button
                  className={
                    "button danger"
                  }
                  type="button"
                  disabled={
                    disconnectMutation
                      .isPending
                  }
                  onClick={() =>
                    disconnectMutation
                      .mutate()
                  }
                >
                  {
                    disconnectMutation
                      .isPending
                      ? "Disconnecting…"
                      : "Disconnect TikTok"
                  }
                </button>
              </div>
            </>
          ) : (
            <>
              <p>
                Connect the TikTok
                account that should
                receive your rendered
                videos.
              </p>

              <div className="actions">
                <button
                  className={
                    "button primary"
                  }
                  type="button"
                  disabled={
                    connectMutation
                      .isPending
                  }
                  onClick={() =>
                    connectMutation
                      .mutate()
                  }
                >
                  {
                    connectMutation
                      .isPending
                      ? "Opening TikTok…"
                      : "Connect TikTok"
                  }
                </button>
              </div>
            </>
          )}

        {connectMutation.isError && (
          <div className="error">
            {getErrorMessage(
              connectMutation.error,
            )}
          </div>
        )}

        {disconnectMutation
          .isError && (
            <div className="error">
              {getErrorMessage(
                disconnectMutation
                  .error,
              )}
            </div>
          )}
      </section>
    </>
  );
}