// stores/auth.ts
import { defineStore } from 'pinia';
import type { AxiosError } from 'axios';
import { axios, api } from 'boot/axios';
import { useQuasar } from 'quasar';

const notifTimeout = 30;

export const useAuthStore = defineStore('auth', {
  state: () => ({
    username: '',
    isAuthenticated: false,
  }),
  getters: {
    userName: (state) => state.username,
  },
  actions: {
    login(username: string) {
      this.username = username;
      this.isAuthenticated = true;
    },
    logout() {
      this.username = '';
      this.isAuthenticated = false;
    },
    async getAuthStatus() {
      const $q = useQuasar();
      try {
        const response = await api.get('/auth/authenticate/');
        if (response.status === 200) {
          if (response.data.authenticated) {
            this.isAuthenticated = true;
          }
        }
      } catch (error: unknown) {
        this.isAuthenticated = false;
        if (axios.isAxiosError(error)) {
          const axiosError = error as AxiosError;
          // 401/403 are handled by interceptor, so we only notify for other errors
          if (axiosError.response && ![401, 403].includes(axiosError.response.status)) {
            $q.notify({
              type: 'negative',
              message: 'Erro de conexão ou servidor.',
              timeout: notifTimeout,
            });
          }
        }
        throw error;
      }

      if (!this.isAuthenticated) {
        await this.router.push('/login');
      }
    },
  },
});
