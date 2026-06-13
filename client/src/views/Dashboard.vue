<script setup lang="ts">
import {storeToRefs} from "pinia";
import {useRouter} from "vue-router";

import {ROUTE_AUTH} from "/src/constants/ROUTES";
import {useAuthStore} from "/src/stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const {user} = storeToRefs(authStore);

async function logout(): Promise<void> {
  await authStore.logout();
  await router.push({name: ROUTE_AUTH});
}
</script>

<template>
  <section>
    <h1>داشبورد</h1>
    <p v-if="user">شماره موبایل: {{ user.mobile }}</p>
    <button type="button" @click="logout">خروج</button>
  </section>
</template>
