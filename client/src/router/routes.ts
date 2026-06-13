import type {RouteRecordRaw} from "vue-router";

import {PATH_AUTH, PATH_DASHBOARD, ROUTE_AUTH, ROUTE_DASHBOARD, ROUTE_NOT_FOUND} from "/src/constants/ROUTES";
import AuthLayout from "/src/layouts/AuthLayout.vue";
import MainLayout from "/src/layouts/MainLayout.vue";
import Auth from "/src/views/Auth.vue";
import Dashboard from "/src/views/Dashboard.vue";
import NotFound from "/src/views/NotFound.vue";

const routes: RouteRecordRaw[] = [
  {
    path: PATH_AUTH,
    component: AuthLayout,
    children: [
      {
        path: "",
        name: ROUTE_AUTH,
        component: Auth,
        meta: {requiresAuth: false, guestOnly: true},
      },
    ],
  },
  {
    path: PATH_DASHBOARD,
    component: MainLayout,
    children: [
      {
        path: "",
        name: ROUTE_DASHBOARD,
        component: Dashboard,
        meta: {requiresAuth: true},
      },
    ],
  },
  {
    path: "/:pathMatch(.*)*",
    name: ROUTE_NOT_FOUND,
    component: NotFound,
    meta: {requiresAuth: false},
  },
];

export default routes;
