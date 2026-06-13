import apiCall from "/src/api/call";

export type User = {
  id: number;
  mobile: string;
  name: string | null;
  is_staff: boolean;
};

export type RequestCodePayload = {
  mobile: string;
};

export type VerifyCodePayload = {
  mobile: string;
  code: string;
};

export type RequestCodeResult = {
  mobile: string;
  expire_at: string;
  expire_seconds: number;
};

export type AuthTokenResult = {
  token: string;
  user: User;
};

export async function requestVerificationCode(payload: RequestCodePayload) {
  return await apiCall<RequestCodeResult>(
    "/auth/request-code/",
    "POST",
    {},
    {},
    payload,
  );
}

export async function verifyCode(payload: VerifyCodePayload) {
  return await apiCall<AuthTokenResult>("/auth/verify-code/", "POST", {}, {}, payload);
}

export async function getCurrentUser() {
  return await apiCall<User>("/auth/me/");
}

export async function logoutUser() {
  return await apiCall<void>("/auth/logout/", "POST");
}
