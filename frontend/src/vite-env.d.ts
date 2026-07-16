/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_MODE?: "public" | "private";
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_LOCAL_APP_API_KEY?: string;
  readonly VITE_LOCAL_TIKTOK_CALLBACK?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}