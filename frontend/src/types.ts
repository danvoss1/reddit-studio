export type JobStatus =
  | "queued"
  | "running"
  | "awaiting_approval"
  | "completed"
  | "failed"
  | "cancelled";

export type VoiceKey =
  | "female"
  | "male";

export interface Voice {
  key: VoiceKey;
  name: string;
}

export interface VideoJob {
  id: string;
  created_at: string;
  updated_at: string;

  source_mode:
    | "reddit_url"
    | "manual";

  reddit_url: string | null;
  title: string;
  status: JobStatus;
  stage: string;
  progress: number;
  logs: string;
  error: string | null;

  script: string | null;
  approved_script: string | null;

  gameplay_asset: string | null;
  music_asset: string | null;
  banner_asset: string | null;
  use_music: boolean;
  voice_key: VoiceKey;
  playback_speed: number;

  output_video: string | null;
  narration_file: string | null;
  subtitle_file: string | null;

  upload_status: string;
  platform_url: string | null;
  views: number;

  tiktok_publish_id: string | null;
  tiktok_status: string | null;
  tiktok_caption: string | null;
  tiktok_privacy_level: string | null;
  tiktok_last_error: string | null;
}

export interface Asset {
  id: string;
  created_at: string;

  kind:
    | "gameplay"
    | "music"
    | "banner";

  original_name: string;
  stored_path: string;
  size_bytes: number;
}

export interface Stats {
  total: number;
  queued: number;
  running: number;
  awaiting_approval: number;
  completed: number;
  failed: number;
  uploaded: number;
  total_views: number;
}

export interface TikTokAccount {
  connected: boolean;
  display_name: string | null;
  avatar_url: string | null;
  open_id: string | null;
  scope: string | null;
}

export interface TikTokCreatorInfo {
  creator_username: string | null;
  creator_nickname: string | null;
  creator_avatar_url: string | null;
  privacy_level_options: string[];
  comment_disabled: boolean;
  duet_disabled: boolean;
  stitch_disabled: boolean;
  max_video_post_duration_sec: number;
}

export interface TikTokPublishPayload {
  caption: string;
  privacy_level: string;
  disable_comment: boolean;
  disable_duet: boolean;
  disable_stitch: boolean;
  video_cover_timestamp_ms: number;
  brand_content_toggle: boolean;
  brand_organic_toggle: boolean;
  is_aigc: boolean;
}

export interface TikTokPublishResult {
  publish_id: string;
  status: string;
}

export interface TikTokPostStatus {
  publish_id: string;
  status: string;
  fail_reason: string | null;
  publicly_available_post_ids: string[];
  uploaded_bytes: number | null;
}
