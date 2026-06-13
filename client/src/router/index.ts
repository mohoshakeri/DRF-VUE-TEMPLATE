import {createRouter, createWebHistory} from "vue-router";

import routes from "/src/router/routes";
import {installRouterGuards} from "/src/router/guards";

const router = createRouter({
  history: createWebHistory(),
  routes,
});

installRouterGuards(router);

export default router;
