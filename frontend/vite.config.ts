import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // So that development and the kiosk use the same relative paths: no switching URLs in the
      // code, no CORS special cases.
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    // On the Pi every second of startup counts. Sourcemaps cost transfer for no benefit.
    sourcemap: false,
    chunkSizeWarningLimit: 1200, // maplibre-gl simply is large
  },
});
