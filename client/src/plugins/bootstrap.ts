import type {App} from "vue";

import {installNormalizeDigits} from "/src/plugins/normalize-digits";
import {installNumberFormat} from "/src/plugins/number-format";

export function installBootstrapPlugins(app: App): void {
  installNormalizeDigits(app);
  installNumberFormat(app);
}
