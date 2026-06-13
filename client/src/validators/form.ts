import type {ValidationRule} from "/src/validators/rules";
import {sendMessage} from "/src/utils/messages";

export async function verifyForm(rules: ValidationRule[]): Promise<boolean> {
  for (const rule of rules) {
    const isValid =
      rule.reg instanceof RegExp
        ? rule.reg.test(String(rule.val || ""))
        : await rule.reg(rule.val);

    if (!isValid) {
      await sendMessage(rule.msg, "warning");
      return false;
    }
  }

  return true;
}
