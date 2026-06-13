import type {App, DirectiveBinding} from "vue";

import {normalizeDigits} from "/src/utils/formatters";

function normalizeInput(event: Event): void {
  const input = event.target as HTMLInputElement;
  const normalized = normalizeDigits(input.value);
  if (input.value === normalized) {
    return;
  }
  input.value = normalized;
  input.dispatchEvent(new Event("input", {bubbles: true}));
}

export function installNormalizeDigits(app: App): void {
  app.directive("normalize-digits", {
    mounted(element: HTMLInputElement, binding: DirectiveBinding<boolean>) {
      if (binding.value === false) {
        return;
      }
      element.addEventListener("input", normalizeInput);
    },
    beforeUnmount(element: HTMLInputElement) {
      element.removeEventListener("input", normalizeInput);
    },
  });
}
