import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
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
      path: "/cadastrar-aulas",
      name: "cadastrar-aulas",
      component: () => import("../views/NewClassView.vue"),
    },
    {
      path: "/agendamento",
      name: "agendamento",
      component: () => import("../views/ScheduleView.vue"),
    },
  ],
});

export default router;
