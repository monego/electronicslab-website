import { boot } from 'quasar/wrappers';
import axios from 'axios';
import type { AxiosInstance, AxiosError } from 'axios';

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $axios: AxiosInstance;
    $api: AxiosInstance;
  }
}

// Be careful when using SSR for cross-request state pollution
// due to creating a Singleton instance here;
// If any client changes this (global) instance, it might be a
// good idea to move this instance creation inside of the
// "export default () => {}" function below (which runs individually
// for each client)
const api = axios.create({
  baseURL: process.env.API_URL || 'http://localhost/api',
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFTOKEN',
  withCredentials: true,
  withXSRFToken: true,
});

export default boot(({ app, router }) => {
  api.interceptors.response.use(
    response => response,
    async (error: unknown) => {
      const axiosError = error as AxiosError;
      if (axios.isAxiosError(axiosError) && [401, 403].includes(axiosError.response?.status || 0)) {
        // Clear auth state if possible (optional here, but router push is key)
        await router.push('/login');
      }
      return Promise.reject(axiosError);
    },
  );

  app.config.globalProperties.$axios = axios;
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api;
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API
});

export { axios, api };
