import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('src/layouts/MainLayout.vue'),
  },
  {
    path: '/admin',
    component: () => import('src/layouts/AdminLayout.vue'),
    children: [{ path: '', component: () => import('pages/AccessPage.vue') }],
  },
  {
    path: '/telao',
    component: () => import('layouts/TelaoLayout.vue'),
    children: [
      { path: 'secretaria', name: 'secretaria', component: () => import('src/pages/TelaoSecretaria.vue') },
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
