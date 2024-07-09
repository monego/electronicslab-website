// stores/auth.ts
import { defineStore } from 'pinia';

export const useAuthStore = defineStore('username', {
  state: () => ({ username: 'null' }),
  getters: {
    userName: (state) => state.username,
  },
  actions: {
    setUsername(username: string) {
      this.username = username;
    },
    logout() {
      this.username = 'null';
    },
  },
});
