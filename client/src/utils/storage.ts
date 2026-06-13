import {AUTH_TOKEN_KEY, DARK_MODE_KEY} from "/src/constants/ENUMS";

export function getAuthToken(): string | null {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

export function setAuthToken(token: string): void {
  localStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function removeAuthToken(): void {
  localStorage.removeItem(AUTH_TOKEN_KEY);
}

export function getDarkMode(): boolean {
  return localStorage.getItem(DARK_MODE_KEY) === "1";
}

export function setDarkMode(isDarkMode: boolean): void {
  localStorage.setItem(DARK_MODE_KEY, isDarkMode ? "1" : "0");
}
