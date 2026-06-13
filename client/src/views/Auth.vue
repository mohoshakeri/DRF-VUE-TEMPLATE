<script setup lang="ts">
import {ref} from "vue";
import {useRoute, useRouter} from "vue-router";

import {requestVerificationCode, verifyCode} from "/src/api/services/auth";
import {ROUTE_DASHBOARD} from "/src/constants/ROUTES";
import {useAuthStore} from "/src/stores/auth";
import {sendMessage} from "/src/utils/messages";
import {normalizeDigits} from "/src/utils/formatters";
import {verifyForm} from "/src/validators/form";
import {MOBILE_REGEX} from "/src/validators/regex";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const mobile = ref("");
const code = ref("");
const codeRequested = ref(false);

async function requestCode(): Promise<void> {
  mobile.value = normalizeDigits(mobile.value);
  const isValid = await verifyForm([
    {
      val: mobile.value,
      reg: MOBILE_REGEX,
      msg: "شماره موبایل صحیح نیست.",
    },
  ]);
  if (!isValid) {
    return;
  }

  const result = await requestVerificationCode({mobile: mobile.value});
  if (!result || "isHTML" in result) {
    return;
  }

  codeRequested.value = true;
  await sendMessage("کد تایید ارسال شد.", "success");
}

async function submitCode(): Promise<void> {
  code.value = normalizeDigits(code.value);
  const isValid = await verifyForm([
    {
      val: code.value,
      reg: /^\d{5}$/,
      msg: "کد تایید صحیح نیست.",
    },
  ]);
  if (!isValid) {
    return;
  }

  const result = await verifyCode({mobile: mobile.value, code: code.value});
  if (!result || "isHTML" in result) {
    return;
  }

  authStore.setAuthenticated(result.token, result.user);
  await router.push(String(route.query.next || "") || {name: ROUTE_DASHBOARD});
}
</script>

<template>
  <section>
    <h1>ورود</h1>
    <form v-if="!codeRequested" @submit.prevent="requestCode">
      <label for="mobile">موبایل</label>
      <input id="mobile" v-model="mobile" v-normalize-digits inputmode="numeric" />
      <button type="submit">دریافت کد</button>
    </form>

    <form v-else @submit.prevent="submitCode">
      <label for="code">کد تایید</label>
      <input id="code" v-model="code" v-normalize-digits inputmode="numeric" />
      <button type="submit">ورود</button>
      <button type="button" @click="codeRequested = false">تغییر موبایل</button>
    </form>
  </section>
</template>
