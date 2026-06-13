<script setup lang="ts">
import {storeToRefs} from "pinia";

import {useGlobalStore} from "/src/stores/global";

const store = useGlobalStore();
const {isLoading} = storeToRefs(store);
</script>

<template>
  <div v-if="isLoading" role="status" aria-live="polite">
    در حال بارگذاری...
  </div>
</template>
