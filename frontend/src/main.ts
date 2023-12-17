import { createApp } from 'vue'
import './style.css'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router' // If the folder contains an index file, it is imported automatically

createApp(App).use(router).use(ElementPlus).mount('#app')
