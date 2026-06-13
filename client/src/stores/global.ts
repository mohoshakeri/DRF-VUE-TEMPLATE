import {defineStore} from "pinia";

import type {MessageStatus} from "/src/constants/ENUMS";
import {MESSAGE_STATUS_PRIMARY} from "/src/constants/ENUMS";
import {getDarkMode, setDarkMode} from "/src/utils/storage";

type MessageState = {
  id: number | null;
  content: string;
  status: MessageStatus;
};

export const useGlobalStore = defineStore("global", {
  state: () => ({
    isLoading: false,
    isDarkMode: false,
    message: {
      id: null,
      content: "",
      status: MESSAGE_STATUS_PRIMARY,
    } as MessageState,
  }),
  actions: {
    showMessage(content: string, status: MessageStatus = MESSAGE_STATUS_PRIMARY) {
      this.message = {
        id: Date.now(),
        content,
        status,
      };
    },
    clearMessage() {
      this.message = {
        id: null,
        content: "",
        status: MESSAGE_STATUS_PRIMARY,
      };
    },
    applyDarkMode() {
      document.documentElement.classList.toggle("dark", this.isDarkMode);
    },
    toggleDarkMode() {
      this.isDarkMode = !this.isDarkMode;
      setDarkMode(this.isDarkMode);
      this.applyDarkMode();
    },
    loadDarkMode() {
      this.isDarkMode = getDarkMode();
      this.applyDarkMode();
    },
  },
});
