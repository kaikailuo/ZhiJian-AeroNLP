import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import LoginView from "@/views/LoginView.vue";
import HomeView from "@/views/HomeView.vue";
import PlaceholderView from "@/views/PlaceholderView.vue";
import TrainingLab from "@/views/TrainingLab.vue";

const routes = [
  { path: "/login", name: "login", component: LoginView },
  { path: "/", name: "home", component: HomeView, meta: { requiresAuth: true } },
  {
    path: "/notam",
    name: "notam",
    component: PlaceholderView,
    meta: { requiresAuth: true, title: "NOTAM 中心" },
  },
  {
    path: "/routes",
    name: "routes",
    component: PlaceholderView,
    meta: { requiresAuth: true, title: "航路规划" },
  },
  {
    path: "/training",
    name: "training",
    component: TrainingLab,
    meta: { requiresAuth: true, title: "训练实验室" },
  },
  {
    path: "/api-keys",
    name: "api-keys",
    component: PlaceholderView,
    meta: { requiresAuth: true, title: "API 密钥库" },
  },
  {
    path: "/maps",
    name: "maps",
    component: PlaceholderView,
    meta: { requiresAuth: true, title: "地理情报" },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const auth = useAuthStore();
  if (to.meta.requiresAuth && !auth.accessToken) {
    return { name: "login" };
  }
  if (to.name === "login" && auth.accessToken) {
    return { name: "home" };
  }
  return true;
});

export default router;
