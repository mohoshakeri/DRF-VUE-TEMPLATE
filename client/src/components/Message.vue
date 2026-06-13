<script setup lang="ts">
import {storeToRefs} from "pinia";

import {useGlobalStore} from "/src/stores/global";

const store = useGlobalStore();
const {message} = storeToRefs(store);
</script>

<template>
  <div v-if="message.id" role="alert" :data-status="message.status">
    {{ message.content }}
    <button type="button" @click="store.clearMessage">×</button>
  </div>
</template>
