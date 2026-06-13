export function registerPwa(): void {
  if (!("serviceWorker" in navigator)) {
    return;
  }
}
