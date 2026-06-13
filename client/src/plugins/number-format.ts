import type {App} from "vue";

import {formatNumber} from "/src/utils/formatters";

export function installNumberFormat(app: App): void {
  app.directive("num-format", {
    mounted(element: HTMLElement, binding) {
      element.textContent = formatNumber(binding.value);
    },
    updated(element: HTMLElement, binding) {
      element.textContent = formatNumber(binding.value);
    },
  });
}
