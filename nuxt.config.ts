export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",

  devtools: {
    enabled: true,
  },

  modules: [
    "@nuxtjs/i18n",
  ],

  i18n: {
    strategy: "no_prefix",
    defaultLocale: "fr",
    langDir: "locales",

    locales: [
      {
        code: "fr",
        name: "Français",
        language: "fr-FR",
        file: "fr.json",
      },
      {
        code: "en",
        name: "English",
        language: "en-GB",
        file: "en.json",
      },
    ],

    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: "observatoire_locale",
      redirectOn: "root",
    },
  },

  vite: {
    optimizeDeps: {
      exclude: ["maplibre-gl"],
    },
  },
})