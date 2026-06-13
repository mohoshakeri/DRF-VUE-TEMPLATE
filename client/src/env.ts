export const BACKEND_BASE_URL: string =
  import.meta.env.VITE_BACKEND_BASE_URL || "http://localhost:4110/api/v1";

export const APP_TITLE: string =
  import.meta.env.VITE_APP_TITLE || "DRF Vue Template";

export const IS_DEVELOPMENT: boolean = import.meta.env.DEV;
