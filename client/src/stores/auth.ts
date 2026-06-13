import {computed, ref} from "vue";
import {defineStore} from "pinia";

import type {User} from "/src/api/services/auth";
import {getCurrentUser, logoutUser} from "/src/api/services/auth";
import {getAuthToken, removeAuthToken, setAuthToken} from "/src/utils/storage";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<User | null>(null);
  const isAuthenticated = computed(() => Boolean(getAuthToken()));

  async function loadCurrentUser(): Promise<User | null> {
    const result = await getCurrentUser();
    if (!result || "isHTML" in result) {
      user.value = null;
      return null;
    }
    user.value = result;
    return result;
  }

  function setAuthenticated(token: string, nextUser: User): void {
    setAuthToken(token);
    user.value = nextUser;
  }

  async function logout(): Promise<void> {
    await logoutUser();
    removeAuthToken();
    user.value = null;
  }

  return {
    user,
    isAuthenticated,
    loadCurrentUser,
    setAuthenticated,
    logout,
  };
});
