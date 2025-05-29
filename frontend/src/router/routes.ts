import type { RouteRecordRaw } from 'vue-router';
import { useAuthStore } from 'stores/auth';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('src/layouts/MainLayout.vue'),
    children: [
      { path: '/', component: () => import('pages/IndexPage.vue') },
      { path: '/calendario', component: () => import('pages/CalendarPage.vue') },
      { path: '/materiais', component: () => import('pages/EquipmentPublicPage.vue') },
    ],
  },
  {
    path: '/admin',
    component: () => import('src/layouts/AdminLayout.vue'),
    beforeEnter: (to, from, next) => {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) {
        next({ path: '/login' });
      } else {
        next();
      }
    },
    children: [
      { path: '/acesso', component: () => import('pages/AccessPage.vue') },
      { path: '/emprestimo', component: () => import('pages/LoanPage.vue') },
      { path: '/equipamentos', component: () => import('pages/EquipmentPage.vue') },
      { path: '/ocorrencias', component: () => import('pages/OccurrencePage.vue') },
      { path: '/compras', component: () => import('pages/PurchasePage.vue') },
    ],
  },
  {
    path: '/login',
    component: () => import('src/layouts/LoginLayout.vue'),
    children: [
      { path: '/login', component: () => import('pages/LoginPage.vue') },
    ],
  },
  {
    path: '/telao',
    component: () => import('src/layouts/TelaoLayout.vue'),
    children: [
      { path: '/telaohall', component: () => import('pages/TelaoHall.vue') },
      { path: '/secretaria', name: 'secretaria', component: () => import('pages/TelaoSecretaria.vue') },
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
