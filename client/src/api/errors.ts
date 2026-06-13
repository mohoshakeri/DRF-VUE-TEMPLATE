import {
  HTTP_STATUS_BAD_REQUEST,
  HTTP_STATUS_FORBIDDEN,
  HTTP_STATUS_SERVER_ERROR,
  HTTP_STATUS_TOO_MANY_REQUESTS,
  HTTP_STATUS_UNAUTHORIZED,
} from "/src/constants/ENUMS";
import {
  MESSAGE_ACCESS_DENIED,
  MESSAGE_RATE_LIMIT,
  MESSAGE_SERVER_ERROR,
  MESSAGE_SESSION_EXPIRED,
  MESSAGE_VALIDATION_ERROR,
} from "/src/constants/MESSAGES";
import {ROUTE_AUTH} from "/src/constants/ROUTES";
import {removeAuthToken} from "/src/utils/storage";

type ErrorData = {
  message?: string;
  devMessage?: unknown;
};

export async function buildFriendlyMessage(
  status: number,
  isJson: boolean,
  data: unknown,
): Promise<string | null> {
  const errorData = isJson ? (data as ErrorData) : {};
  const extractedMessage = errorData.message || null;

  if (status === HTTP_STATUS_BAD_REQUEST) {
    return extractedMessage || MESSAGE_VALIDATION_ERROR;
  }
  if (status === HTTP_STATUS_UNAUTHORIZED) {
    removeAuthToken();
    const {default: router} = await import("/src/router");
    await router.push({name: ROUTE_AUTH});
    return extractedMessage || MESSAGE_SESSION_EXPIRED;
  }
  if (status === HTTP_STATUS_FORBIDDEN) {
    return extractedMessage || MESSAGE_ACCESS_DENIED;
  }
  if (status === HTTP_STATUS_TOO_MANY_REQUESTS) {
    return extractedMessage || MESSAGE_RATE_LIMIT;
  }
  if (status >= HTTP_STATUS_SERVER_ERROR) {
    return MESSAGE_SERVER_ERROR;
  }

  return extractedMessage || null;
}
