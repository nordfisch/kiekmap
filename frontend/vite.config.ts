import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Damit in Entwicklung und im Kiosk dieselben relativen Pfade gelten: kein Umschalten von
      // URLs im Code, keine CORS-Sonderfaelle.
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    // Auf dem Pi zaehlt jede Sekunde beim Start. Sourcemaps kosten Uebertragung ohne Nutzen.
    sourcemap: false,
    chunkSizeWarningLimit: 1200, // maplibre-gl ist nun mal gross
  },
});
