import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react-swc";
import { nodePolyfills } from "vite-plugin-node-polyfills";
import path from "path";
import { createThesisDevProxy, resolveThesisDevProxyTargets } from "./src/features/thesis/devProxy";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const proxyTargets = resolveThesisDevProxyTargets({
    apiBaseUrl: env.VITE_API_URL,
    devboxBaseUrl: env.VITE_THESIS_DEVBOX_PROXY_TARGET,
    userServiceBaseUrl: env.VITE_THESIS_USER_SERVICE_PROXY_TARGET,
    localUserId: env.VITE_THESIS_LOCAL_USER_ID,
  });

  return {
    test: {
      environment: "jsdom",
      globals: true,
      setupFiles: "./src/test/setup.ts",
      passWithNoTests: true,
    },
    server: {
      host: "::",
      port: 3000,
      proxy: createThesisDevProxy(proxyTargets),
      headers: {
        "Cache-Control": "no-store",
      },
      hmr: {
        overlay: false,
      },
    },
    optimizeDeps: {
      force: true,
    },
    plugins: [
      react(),
      nodePolyfills({
        globals: {
          Buffer: true,
        },
      }),
    ].filter(Boolean),
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
      dedupe: ["react", "react-dom", "react/jsx-runtime", "react/jsx-dev-runtime"],
    },
  };
});
