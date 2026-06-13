import type {Router} from "vue-router";

import {ROUTE_AUTH, ROUTE_DASHBOARD} from "/src/constants/ROUTES";
import {useAuthStore} from "/src/stores/auth";
import {getAuthToken, removeAuthToken} from "/src/utils/storage";

export function installRouterGuards(router: Router): void {
  router.beforeEach(async (to) => {
    const authStore = useAuthStore();
    const token = getAuthToken();

    if (to.meta.guestOnly && token) {
      return {name: ROUTE_DASHBOARD};
    }

    if (!to.meta.requiresAuth) {
      return true;
    }

    if (!token) {
      return {name: ROUTE_AUTH, query: {next: to.fullPath}};
    }

    if (authStore.user) {
      return true;
    }

    const user = await authStore.loadCurrentUser();
    if (user) {
      return true;
    }

    removeAuthToken();
    return {name: ROUTE_AUTH, query: {next: to.fullPath}};
  });
}
