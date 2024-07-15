// stores/auth.ts
import { defineStore } from 'pinia';
import { AxiosInstance } from 'axios';
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
        console.log(response);
        if (response.status === 200) {
          if (response.data.authenticated) {
            this.isAuthenticated = true;
          }
        } else {
          throw new Error(`Request failed with status ${response.status}: ${response.statusText}`);
        }
      } catch (error: any) {
        if (axios.isAxiosError(error)) {
          console.error(`Axios Error: ${error.message}`);
          if (error.response) {
            console.error(`Status: ${error.response.status}`);
            console.error(`Data: ${JSON.stringify(error.response.data, null, 2)}`); // Formatted JSON
          }
        } else {
          console.error(`Error: ${error.message}`);
        }
        throw error; // Rethrow the error
      }

      if (!this.isAuthenticated) {
        this.router.push('/login');
      }
    },
  },
});
