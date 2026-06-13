export const AUTH_TOKEN_KEY = "auth-token";
export const DARK_MODE_KEY = "dark-mode";

export const MESSAGE_STATUS_PRIMARY = "primary";
export const MESSAGE_STATUS_SUCCESS = "success";
export const MESSAGE_STATUS_WARNING = "warning";
export const MESSAGE_STATUS_DANGER = "danger";
export const MESSAGE_STATUS_INFO = "info";

export const HTTP_STATUS_BAD_REQUEST = 400;
export const HTTP_STATUS_UNAUTHORIZED = 401;
export const HTTP_STATUS_FORBIDDEN = 403;
export const HTTP_STATUS_TOO_MANY_REQUESTS = 429;
export const HTTP_STATUS_SERVER_ERROR = 500;

export type MessageStatus =
  | typeof MESSAGE_STATUS_PRIMARY
  | typeof MESSAGE_STATUS_SUCCESS
  | typeof MESSAGE_STATUS_WARNING
  | typeof MESSAGE_STATUS_DANGER
  | typeof MESSAGE_STATUS_INFO;
