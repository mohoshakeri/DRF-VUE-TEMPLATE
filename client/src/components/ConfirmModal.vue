<script setup lang="ts">
defineProps<{
  open: boolean;
  title: string;
}>();

const emit = defineEmits<{
  confirm: [];
  cancel: [];
}>();
</script>

<template>
  <dialog :open="open">
    <p>{{ title }}</p>
    <button type="button" @click="emit('confirm')">تایید</button>
    <button type="button" @click="emit('cancel')">انصراف</button>
  </dialog>
</template>
