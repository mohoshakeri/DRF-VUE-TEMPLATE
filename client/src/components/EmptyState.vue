<script setup lang="ts">
defineProps<{
  title?: string;
}>();
</script>

<template>
  <p>{{ title || "موردی برای نمایش وجود ندارد." }}</p>
</template>
