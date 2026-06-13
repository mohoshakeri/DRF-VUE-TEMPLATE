<script setup lang="ts">
import {RouterView} from "vue-router";

import Loading from "/src/components/Loading.vue";
import Message from "/src/components/Message.vue";
</script>

<template>
  <Loading />
  <Message />
  <main>
    <RouterView />
  </main>
</template>
