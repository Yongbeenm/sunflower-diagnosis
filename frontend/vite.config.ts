import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { VitePWA } from "vite-plugin-pwa";
import { fileURLToPath, URL } from "node:url";

declare module "vite" {
  interface UserConfig {
    test?: Record<string, unknown>;
  }
}

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: [
        "favicon.ico",
        "robots.txt",
        "apple-touch-icon.png",
      ],
      manifest: {
        name: "Sunflower Expert System",
        short_name: "Sunflower AI",
        description: "Bilingual AI Expert System for Sunflower Disease Diagnosis and Care",
        theme_color: "#1A2411",
        background_color: "#1A2411",
        display: "standalone",
        orientation: "portrait",
        scope: "/",
        start_url: "/",
        icons: [
          {
            src: "/icons/pwa-192x192.png",
            sizes: "192x192",
            type: "image/png",
          },
          {
            src: "/icons/pwa-512x512.png",
            sizes: "512x512",
            type: "image/png",
          },
          {
            src: "/icons/pwa-512x512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "any maskable",
          },
        ],
      },
      workbox: {
        globPatterns: ["**/*.{js,css,html,ico,png,svg,webp,json,woff,woff2}"],
        runtimeCaching: [
          // 1. Specifically Cache i18next Translation JSON Dictionaries
          {
            urlPattern: /.*\/locales\/.*\.json$/,
            handler: "CacheFirst",
            options: {
              cacheName: "i18n-locales-cache",
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 60 * 24 * 30, // 30 Days
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
          // 2. Cache Symptom & Disease Definitions (StaleWhileRevalidate for offline diagnosis)
          {
            urlPattern: /\/api\/v1\/(symptoms|diseases).*/,
            handler: "StaleWhileRevalidate",
            options: {
              cacheName: "api-definitions-cache",
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 * 7, // 7 Days
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
          // 3. Cache Botanical & Media Images
          {
            urlPattern: /\/media\/.*\.(?:png|jpg|jpeg|svg|webp)$/,
            handler: "CacheFirst",
            options: {
              cacheName: "media-images-cache",
              expiration: {
                maxEntries: 200,
                maxAgeSeconds: 60 * 60 * 24 * 30, // 30 Days
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) },
  },
  server: {
    host: "0.0.0.0",
    port: 5173,
    watch: {
      usePolling: true,
    },
    // The app talks to the API through /api/v1 in dev, so cookies are same-origin
    // and the refresh-token cookie works without SameSite headaches.
    proxy: {
      "/api": { target: process.env.VITE_PROXY_TARGET || "http://127.0.0.1:8000", changeOrigin: true },
      "/media": { target: process.env.VITE_PROXY_TARGET || "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test-setup.ts"],
  },
});
