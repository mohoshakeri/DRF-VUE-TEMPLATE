import {createApp} from "vue";
import {createPinia} from "pinia";

import App from "/src/App.vue";
import router from "/src/router";
import {installBootstrapPlugins} from "/src/plugins/bootstrap";
import {registerPwa} from "/src/pwa/register";
import {useGlobalStore} from "/src/stores/global";
import "/src/styles/variables.css";
import "/src/styles/helpers.css";
import "/src/styles/app.css";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
installBootstrapPlugins(app);
registerPwa();
useGlobalStore().loadDarkMode();

app.mount("#app");
