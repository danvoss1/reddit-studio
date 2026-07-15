import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  Link,
  useParams,
} from "react-router-dom";

import {
  api,
} from "../api";

import StatusBadge from "../components/StatusBadge";

function getErrorMessage(
  error: unknown,
): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "An unknown error occurred.";
}


function defaultCaption(
  title: string,
) {
  const base =
    `${title}\n\n`
    + "#redditstories "
    + "#storytime "
    + "#reddit";

  return base.slice(
    0,
    2200,
  );
}


export default function JobDetail() {
  const {
    id = "",
  } = useParams();

  const client =
    useQueryClient();

  const jobQuery = useQuery({
    queryKey: [
      "job",
      id,
    ],

    queryFn: () =>
      api.job(id),

    refetchInterval: query => {
      const status =
        query.state.data
          ?.status;

      if (
        status === "completed"
        || status === "failed"
        || status
        === "cancelled"
        || status
        === "awaiting_approval"
      ) {
        return false;
      }

      return 1500;
    },
  });

  const account = useQuery({
    queryKey: [
      "tiktok-account",
    ],
    queryFn:
      api.tiktokAccount,
  });

  const creatorInfo =
    useQuery({
      queryKey: [
        "tiktok-creator-info",
      ],
      queryFn:
        api.tiktokCreatorInfo,
      enabled:
        account.data
          ?.connected
        === true,
      retry: false,
    });

  const job =
    jobQuery.data;

  const [
    script,
    setScript,
  ] = useState("");

  const [
    uploadStatus,
    setUploadStatus,
  ] = useState(
    "not_uploaded",
  );

  const [
    platformUrl,
    setPlatformUrl,
  ] = useState("");

  const [
    views,
    setViews,
  ] = useState(0);

  const [
    caption,
    setCaption,
  ] = useState("");

  const [
    privacyLevel,
    setPrivacyLevel,
  ] = useState("");

  const [
    disableComment,
    setDisableComment,
  ] = useState(false);

  const [
    disableDuet,
    setDisableDuet,
  ] = useState(false);

  const [
    disableStitch,
    setDisableStitch,
  ] = useState(false);

  const [
    coverTimestamp,
    setCoverTimestamp,
  ] = useState(1000);

  const [
    isAigc,
    setIsAigc,
  ] = useState(true);

  const [
    ownBusiness,
    setOwnBusiness,
  ] = useState(false);

  const [
    paidPartnership,
    setPaidPartnership,
  ] = useState(false);

  useEffect(() => {
    if (!job) {
      return;
    }

    setScript(
      job.approved_script
      || job.script
      || "",
    );

    setUploadStatus(
      job.upload_status,
    );

    setPlatformUrl(
      job.platform_url
      || "",
    );

    setViews(
      job.views,
    );

    setCaption(
      job.tiktok_caption
      || defaultCaption(
        job.title,
      ),
    );

    setPrivacyLevel(
      job.tiktok_privacy_level
      || "",
    );
  }, [
    job?.id,
    job?.script,
    job?.approved_script,
    job?.upload_status,
    job?.platform_url,
    job?.views,
    job?.tiktok_caption,
    job?.tiktok_privacy_level,
    job?.title,
  ]);

  useEffect(() => {
    const options =
      creatorInfo.data
        ?.privacy_level_options
      ?? [];

    if (
      options.length > 0
      && !options.includes(
        privacyLevel,
      )
    ) {
      const preferred =
        options.includes(
          "SELF_ONLY",
        )
          ? "SELF_ONLY"
          : options[0];

      setPrivacyLevel(
        preferred,
      );
    }
  }, [
    creatorInfo.data
      ?.privacy_level_options,
    privacyLevel,
  ]);

  useEffect(() => {
    if (!creatorInfo.data) {
      return;
    }

    setDisableComment(
      creatorInfo.data
        .comment_disabled,
    );

    setDisableDuet(
      creatorInfo.data
        .duet_disabled,
    );

    setDisableStitch(
      creatorInfo.data
        .stitch_disabled,
    );
  }, [
    creatorInfo.data,
  ]);

  const approve =
    useMutation({
      mutationFn: () =>
        api.approve(
          id,
          script,
        ),

      onSuccess: () =>
        client.invalidateQueries({
          queryKey: [
            "job",
            id,
          ],
        }),
    });

  const cancel =
    useMutation({
      mutationFn: () =>
        api.cancel(id),

      onSuccess: () =>
        client.invalidateQueries({
          queryKey: [
            "job",
            id,
          ],
        }),
    });

  const publication =
    useMutation({
      mutationFn: () =>
        api.updatePublication(
          id,
          {
            upload_status:
              uploadStatus,
            platform_url:
              platformUrl
              || null,
            views,
          },
        ),

      onSuccess: () =>
        client.invalidateQueries({
          queryKey: [
            "job",
            id,
          ],
        }),
    });

  const publish =
    useMutation({
      mutationFn: () =>
        api.publishToTikTok(
          id,
          {
            caption,
            privacy_level:
              privacyLevel,
            disable_comment:
              disableComment,
            disable_duet:
              disableDuet,
            disable_stitch:
              disableStitch,
            video_cover_timestamp_ms:
              coverTimestamp,
            brand_content_toggle:
              paidPartnership,
            brand_organic_toggle:
              ownBusiness,
            is_aigc:
              isAigc,
          },
        ),

      onSuccess: () => {
        client.invalidateQueries({
          queryKey: [
            "job",
            id,
          ],
        });
      },
    });

  const refreshStatus =
    useMutation({
      mutationFn: () =>
        api.refreshTikTokStatus(
          id,
        ),

      onSuccess: () =>
        client.invalidateQueries({
          queryKey: [
            "job",
            id,
          ],
        }),
    });

  const privacyOptions =
    useMemo(
      () =>
        creatorInfo.data
          ?.privacy_level_options
        ?? [],
      [
        creatorInfo.data
          ?.privacy_level_options,
      ],
    );

  if (
    jobQuery.isLoading
  ) {
    return (
      <div className="panel">
        Loading job…
      </div>
    );
  }

  if (!job) {
    return (
      <div className="error">
        Job not found.
      </div>
    );
  }

  return (
    <>
      <header className="page-header">
        <div>
          <p className="eyebrow">
            Video job
          </p>

          <h1>
            {job.title}
          </h1>

          <div className="meta">
            <StatusBadge
              status={job.status}
            />

            <span>
              {
                new Date(
                  job.created_at,
                )
                  .toLocaleString()
              }
            </span>
          </div>
        </div>

        {job.output_video && (
          <a
            className="button primary"
            href={
              `/api/jobs/${id}/video`
            }
          >
            Download MP4
          </a>
        )}
      </header>

      <section className="panel">
        <div className="progress-header">
          <strong>
            {job.stage}
          </strong>

          <span>
            {job.progress}%
          </span>
        </div>

        <div className="progress">
          <span
            style={{
              width:
                `${job.progress}%`,
            }}
          />
        </div>

        {job.error && (
          <div className="error">
            {job.error}
          </div>
        )}
      </section>

      {job.status
        === "awaiting_approval"
        && (
          <section className="panel">
            <h2>
              Review narration
              script
            </h2>

            <p>
              This is the last
              checkpoint before
              ElevenLabs credits and
              rendering are used.
            </p>

            <textarea
              className="script-editor"
              rows={18}
              value={script}
              onChange={event =>
                setScript(
                  event.target.value,
                )
              }
            />

            {approve.isError && (
              <div className="error">
                {getErrorMessage(
                  approve.error,
                )}
              </div>
            )}

            <div className="actions">
              <button
                className="button primary"
                onClick={() =>
                  approve.mutate()
                }
                disabled={
                  approve.isPending
                  || script
                    .trim()
                    .length < 20
                }
              >
                Approve and render
              </button>
            </div>
          </section>
        )}

      {job.output_video && (
        <section className="panel">
          <h2>
            Preview
          </h2>

          <video
            className="video-preview"
            controls
            src={
              `/api/jobs/${id}/video`
            }
          />
        </section>
      )}

      {job.status
        === "completed"
        && (
          <section className="panel">
            <h2>
              Publish to TikTok
            </h2>

            {!account.data
              ?.connected ? (
              <p>
                Connect TikTok before
                publishing.{" "}

                <Link to="/tiktok">
                  Open TikTok settings
                </Link>
              </p>
            ) : (
              <>
                {creatorInfo.isError && (

                  <div className="error">
                    {getErrorMessage(
                      creatorInfo.error,
                    )}
                  </div>
                )}

                <div className="field">
                  <label htmlFor="tiktok-caption">
                    Caption and hashtags
                  </label>

                  <textarea
                    id="tiktok-caption"
                    rows={6}
                    maxLength={2200}
                    value={caption}
                    onChange={event =>
                      setCaption(
                        event.target.value,
                      )
                    }
                  />

                  <small>
                    {caption.length}
                    /2200
                  </small>
                </div>

                <div className="field">
                  <label htmlFor="privacy-level">
                    Privacy
                  </label>

                  <select
                    id="privacy-level"
                    value={privacyLevel}
                    onChange={event =>
                      setPrivacyLevel(
                        event.target.value,
                      )
                    }
                  >
                    {privacyOptions.map(
                      option => (
                        <option
                          key={option}
                          value={option}
                        >
                          {option}
                        </option>
                      ),
                    )}
                  </select>
                </div>

                <div className="field">
                  <label htmlFor="cover-time">
                    Cover frame time
                    in milliseconds
                  </label>

                  <input
                    id="cover-time"
                    type="number"
                    min={0}
                    value={coverTimestamp}
                    onChange={event =>
                      setCoverTimestamp(
                        Number(
                          event.target.value,
                        ),
                      )
                    }
                  />
                </div>

                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={
                      disableComment
                    }
                    onChange={event =>
                      setDisableComment(
                        event.target.checked,
                      )
                    }
                    disabled={
                      creatorInfo.data
                        ?.comment_disabled
                    }
                  />

                  Disable comments
                </label>

                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={
                      disableDuet
                    }
                    onChange={event =>
                      setDisableDuet(
                        event.target.checked,
                      )
                    }
                    disabled={
                      creatorInfo.data
                        ?.duet_disabled
                    }
                  />

                  Disable Duet
                </label>

                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={
                      disableStitch
                    }
                    onChange={event =>
                      setDisableStitch(
                        event.target.checked,
                      )
                    }
                    disabled={
                      creatorInfo.data
                        ?.stitch_disabled
                    }
                  />

                  Disable Stitch
                </label>

                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={isAigc}
                    onChange={event =>
                      setIsAigc(
                        event.target.checked,
                      )
                    }
                  />

                  Label as AI-generated
                  content
                </label>

                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={ownBusiness}
                    onChange={event =>
                      setOwnBusiness(
                        event.target.checked,
                      )
                    }
                  />

                  Promotes my own
                  business
                </label>

                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={
                      paidPartnership
                    }
                    onChange={event =>
                      setPaidPartnership(
                        event.target.checked,
                      )
                    }
                  />

                  Paid partnership
                </label>

                <p>
                  By clicking publish,
                  you explicitly
                  authorize Reddit
                  Studio to upload this
                  MP4 and selected
                  metadata to TikTok.
                </p>

                {job.tiktok_status && (
                  <p>
                    TikTok status:{" "}
                    <strong>
                      {
                        job.tiktok_status
                      }
                    </strong>
                  </p>
                )}

                {job.tiktok_last_error && (
                  <div className="error">
                    {
                      job.tiktok_last_error
                    }
                  </div>
                )}

                {publish.isError && (
                  <div className="error">
                    {getErrorMessage(
                      publish.error,
                    )}
                  </div>
                )}

                {refreshStatus.isError && (
                  <div className="error">
                    {getErrorMessage(
                      refreshStatus.error,
                    )}
                  </div>
                )}

                <div className="actions">
                  <button
                    className="button primary"
                    type="button"
                    disabled={
                      publish.isPending
                      || !caption.trim()
                      || !privacyLevel
                    }
                    onClick={() =>
                      publish.mutate()
                    }
                  >
                    {
                      publish.isPending
                        ? "Uploading to TikTok…"
                        : "Publish to TikTok"
                    }
                  </button>

                  {job.tiktok_publish_id && (
                    <button
                      className="button"
                      type="button"
                      disabled={
                        refreshStatus.isPending
                      }
                      onClick={() =>
                        refreshStatus.mutate()
                      }
                    >
                      {
                        refreshStatus.isPending
                          ? "Checking…"
                          : "Refresh TikTok status"
                      }
                    </button>
                  )}
                </div>
              </>
            )}
          </section>
        )}

      <section className="two-column">
        <article className="panel">
          <h2>
            Process log
          </h2>

          <pre className="logs">
            {
              job.logs
              || "No log entries."
            }
          </pre>

          {![
            "completed",
            "failed",
            "cancelled",
          ].includes(
            job.status,
          )
            && job.status
            !== "awaiting_approval"
            && (
              <button
                className="button danger"
                onClick={() =>
                  cancel.mutate()
                }
              >
                Cancel job
              </button>
            )}
        </article>

        <article className="panel">
          <h2>
            Publication tracking
          </h2>

          <div className="field">
            <label>
              Status
            </label>

            <select
              value={uploadStatus}
              onChange={event =>
                setUploadStatus(
                  event.target.value,
                )
              }
            >
              <option value="not_uploaded">
                Not uploaded
              </option>

              <option value="scheduled">
                Scheduled
              </option>

              <option value="uploading">
                Uploading
              </option>

              <option value="processing">
                Processing
              </option>

              <option value="uploaded">
                Uploaded
              </option>

              <option value="failed">
                Failed
              </option>
            </select>
          </div>

          <div className="field">
            <label>
              TikTok URL
            </label>

            <input
              value={platformUrl}
              onChange={event =>
                setPlatformUrl(
                  event.target.value,
                )
              }
              placeholder=
              "https://www.tiktok.com/..."
            />
          </div>

          <div className="field">
            <label>
              Views
            </label>

            <input
              type="number"
              min={0}
              value={views}
              onChange={event =>
                setViews(
                  Number(
                    event.target.value,
                  ),
                )
              }
            />
          </div>

          <button
            className="button"
            onClick={() =>
              publication.mutate()
            }
          >
            Save publication data
          </button>
        </article>
      </section>
    </>
  );
}
