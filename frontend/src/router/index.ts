import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("../views/HomeView.vue"),
    },
    {
      path: "/login",
      name: "login",
      component: () => import("../views/LoginView.vue"),
    },
    {
      path: "/dashboard",
      component: () => import("../views/DashboardView.vue"),
    },
    {
      path: '/emprestimos',
      component: () => import("../views/LoanView.vue")
    },
    {
      path: '/equipamentos',
      component: () => import("../views/EquipmentView.vue")
    },
    {
      path: '/registros',
      component: () => import("../views/AccessView.vue")
    },
    {
      path: "/consulta",
      name: "consulta",
      component: () => import("../views/CalendarView.vue"),
    },
    {
      path: "/estatisticas",
      name: "estatisticas",
      component: () => import("../views/StatisticsView.vue"),
    },
  ],
});

export default router;
