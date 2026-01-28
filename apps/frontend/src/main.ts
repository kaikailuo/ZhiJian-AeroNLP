import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import "./assets/main.css";
import "./styled-system/styles.css"; // Panda 生成的原子类

createApp(App).use(createPinia()).use(router).mount("#app");
