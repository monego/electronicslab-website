// stores/auth.ts
import { defineStore } from 'pinia';
import { AxiosInstance, AxiosError } from 'axios';
import { axios, api } from 'boot/axios';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    username: '',
    isAuthenticated: false,
  }),
  getters: {
    userName: (state) => state.username,
  },
  actions: {
    setUsername(username: string) {
      this.username = username;
    },
    logout() {
      this.username = '';
      this.isAuthenticated = false;
    },
    async getAuthStatus() {
      try {
        const response = await (api as AxiosInstance).get('/auth/authenticate/');
        if (response.status === 200) {
          if (response.data.authenticated) {
            this.isAuthenticated = true;
          }
        } else {
          throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
        }
      } catch (error: unknown) {
        if (axios.isAxiosError(error)) {
          const axiosError = error as AxiosError;
          if (axiosError.response) {
            const errorData = axiosError.response.data as { detail?: string };
            const errorDetail = errorData.detail ?? 'Erro desconhecido!';
            console.log(errorDetail);
          }
        } else {
          console.log('Erro desconhecido!');
        }
        throw error; // Rethrow the error
      }

      if (!this.isAuthenticated) {
        this.router.push('/login');
      }
    },
  },
});
