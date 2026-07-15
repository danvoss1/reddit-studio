export type JobStatus =
  | "queued"
  | "running"
  | "awaiting_approval"
  | "completed"
  | "failed"
  | "cancelled";

export type VoiceKey = "female" | "male";

export interface Voice {
  key: VoiceKey;
  name: string;
}

export interface VideoJob {
  id: string;
  created_at: string;
  updated_at: string;
  source_mode: "reddit_url" | "manual";
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
}

export interface Asset {
  id: string;
  created_at: string;
  kind: "gameplay" | "music" | "banner";
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
