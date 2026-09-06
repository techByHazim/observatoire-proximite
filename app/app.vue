<script setup lang="ts">
import ChartView from "./components/ChartView.client.vue"
import CityIndicatorsChart from "./components/CityIndicatorsChart.client.vue"
import CommonStructureChart from "./components/CommonStructureChart.client.vue"
import MapView from "./components/MapView.client.vue"

interface ScaleAnalysis {
  pc1_evr: number | null
  pc1_population_r: number | null
  population_correlation_n: number
  pc1_income_spearman: number | null
  income_correlation_n: number
}

interface ScaleEntry {
  bw: number
  cutoff: number
  file: string
  analysis?: ScaleAnalysis
}

interface CityEntry {
  name: string
  slug: string
  code: string
  boundary: string | null
  scales: ScaleEntry[]
}

interface CitiesManifest {
  cities: CityEntry[]
  pc1_evr_threshold?: number
}

type ViewName = "map" | "charts" | "method"
type ChartSection = "distribution" | "structure" | "indicators"
type UrbanIndicator = "population" | "income"
type ColorTheme = "light" | "dark"

const activeView = ref<ViewName>("map")
const selectedChartSection = ref<ChartSection>("distribution")
const selectedUrbanIndicator = ref<UrbanIndicator>("population")
const pc1EvrThreshold = ref(0.85)
const selectedIndicator = ref("pc1")
const selectedBw = ref(400)
const selectedCitySlug = ref("marseille")
const manifestError = ref("")
const colorTheme = ref<ColorTheme>("light")

type LocaleCode = "fr" | "en"

const languageMenu = ref<HTMLDetailsElement | null>(null)

const {
  locale,
  setLocale,
  t,
} = useI18n()

async function changeLocale(code: LocaleCode) {
  await setLocale(code)

  if (languageMenu.value) {
    languageMenu.value.open = false
  }
}

useHead(() => ({
  title: t("header.title"),

  htmlAttrs: {
    lang: locale.value,
  },
}))

const darkMode = computed(() => colorTheme.value === "dark")

function applyTheme(theme: ColorTheme) {
  if (!import.meta.client) {
    return
  }

  document.documentElement.dataset.theme = theme
  localStorage.setItem("observatoire-theme", theme)
}

function toggleTheme() {
  colorTheme.value = darkMode.value ? "light" : "dark"
  applyTheme(colorTheme.value)
}

const availableCities = ref<CityEntry[]>([
  {
    name: "Marseille",
    slug: "marseille",
    code: "13055",
    boundary: "/data/marseille/boundary.geojson",
    scales: [
      {
        bw: 400,
        cutoff: 2000,
        file: "/data/marseille/bw400.geojson",
      },
    ],
  },
])

const indicators = [
  { key: "pc1", label: "Accessibilité générale" },
  { key: "commerce", label: "Accessibilité au commerce" },
  { key: "sante", label: "Accessibilité à la santé" },
  { key: "education", label: "Accessibilité à l'éducation" },
  { key: "services", label: "Accessibilité aux services" },
  { key: "loisirs", label: "Accessibilité aux loisirs" },
  { key: "revenu", label: "Niveau de vie" },
  { key: "population", label: "Population" },
]

const currentCity = computed(() => {
  return (
    availableCities.value.find(
      (city) => city.slug === selectedCitySlug.value,
    ) ?? availableCities.value[0]
  )
})

const availableScales = computed(() => {
  return currentCity.value?.scales ?? []
})

const currentScale = computed(() => {
  return (
    availableScales.value.find(
      (scale) => scale.bw === selectedBw.value,
    ) ?? availableScales.value[0]
  )
})

const currentCityName = computed(() => {
  return currentCity.value?.name ?? "Marseille"
})

const currentBoundaryUrl = computed(() => {
  return currentCity.value?.boundary ?? ""
})

const currentDataUrl = computed(() => {
  return currentScale.value?.file ?? ""
})

const currentCutoff = computed(() => {
  return currentScale.value?.cutoff ?? 5 * selectedBw.value
})

const selectedIndicatorUsesScale = computed(() => {
  return !["revenu", "population"].includes(selectedIndicator.value)
})

onMounted(() => {
  const savedTheme = localStorage.getItem("observatoire-theme")
  const systemUsesDarkMode = window.matchMedia(
    "(prefers-color-scheme: dark)",
  ).matches

  const initialTheme: ColorTheme =
    savedTheme === "dark"
    || (savedTheme !== "light" && systemUsesDarkMode)
      ? "dark"
      : "light"

  colorTheme.value = initialTheme
  applyTheme(initialTheme)
})

onMounted(async () => {
  try {

    const response = await fetch("/data/cities.json")

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const manifest = (await response.json()) as CitiesManifest

    if (!Array.isArray(manifest.cities) || manifest.cities.length === 0) {
      throw new Error("Le manifeste ne contient aucune ville.")
    }

    availableCities.value = manifest.cities

    const manifestThreshold = Number(manifest.pc1_evr_threshold)

    if (Number.isFinite(manifestThreshold)) {
      pc1EvrThreshold.value = manifestThreshold
    }

    const marseille = manifest.cities.find(
      (city) => city.slug === "marseille",
    )

    const initialCity = marseille ?? manifest.cities[0]
    selectedCitySlug.value = initialCity.slug

    const bw400 = initialCity.scales.find((scale) => scale.bw === 400)
    selectedBw.value = bw400?.bw ?? initialCity.scales[0].bw
  } catch (error) {
    manifestError.value =
      "Le manifeste multiville est absent. Marseille à 400 m est utilisée."

    console.error("Erreur de chargement du manifeste :", error)
  }
})

watch(
  () => selectedCitySlug.value,
  () => {
    const scales = currentCity.value?.scales ?? []

    if (scales.length === 0) {
      return
    }

    const hasCurrentScale = scales.some(
      (scale) => scale.bw === selectedBw.value,
    )

    if (hasCurrentScale) {
      return
    }

    const bw400 = scales.find((scale) => scale.bw === 400)
    selectedBw.value = bw400?.bw ?? scales[0].bw
  },
)
</script>

<template>
  <div class="application">
    <header class="header">
      <div class="header-inner">
        <div>
          <h1>{{ t("header.title") }}</h1>

          <p>
            {{ t("header.subtitle") }}
          </p>
        </div>

        <nav
          class="main-navigation"
          :aria-label="t('navigation.label')"
        >
          <button
            type="button"
            :class="{ active: activeView === 'map' }"
            @click="activeView = 'map'"
          >
            {{ t("navigation.map") }}
          </button>

          <button
            type="button"
            :class="{ active: activeView === 'charts' }"
            @click="activeView = 'charts'"
          >
            {{ t("navigation.charts") }}
          </button>

          <button
            type="button"
            :class="{ active: activeView === 'method' }"
            @click="activeView = 'method'"
          >
            {{ t("navigation.method") }}
          </button>
        </nav>

        <div class="header-actions">
          <!-- Bouton clair/sombre -->
          <button
            type="button"
            class="theme-toggle"
            :aria-pressed="darkMode"
            :aria-label="t('theme.toggle')"
            :data-tooltip="t('theme.toggle')"
            @click="toggleTheme"
          >
            <svg
              v-if="darkMode"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="4" />

              <path
                d="M12 2v2
                   M12 20v2
                   M4.93 4.93l1.42 1.42
                   M17.65 17.65l1.42 1.42
                   M2 12h2
                   M20 12h2
                   M4.93 19.07l1.42-1.42
                   M17.65 6.35l1.42-1.42"
              />
            </svg>

            <svg
              v-else
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                d="M21 12.79A9 9 0 1 1 11.21 3
                   7 7 0 0 0 21 12.79Z"
              />
            </svg>
          </button>

          <!-- Sélecteur de langue -->
          <details
            ref="languageMenu"
            class="language-menu"
          >
            <summary
              class="theme-toggle language-toggle"
              :aria-label="t('language.change')"
              :data-tooltip="t('language.change')"
            >
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <circle cx="12" cy="12" r="9" />
                <path d="M3 12h18" />
                <path d="M12 3a15 15 0 0 1 0 18" />
                <path d="M12 3a15 15 0 0 0 0 18" />
              </svg>

              <span
                class="current-language-flag"
                :class="
                  locale === 'fr'
                    ? 'flag-fr'
                    : 'flag-gb'
                "
                aria-hidden="true"
              ></span>
            </summary>

            <div class="language-options">
              <button
                type="button"
                :class="{ active: locale === 'fr' }"
                @click="changeLocale('fr')"
              >
                <span
                  class="language-flag flag-fr"
                  aria-hidden="true"
                ></span>

                <span>
                  {{ t("language.french") }}
                </span>

                <span
                  v-if="locale === 'fr'"
                  aria-hidden="true"
                >
                  ✓
                </span>
              </button>

              <button
                type="button"
                :class="{ active: locale === 'en' }"
                @click="changeLocale('en')"
              >
                <span
                  class="language-flag flag-gb"
                  aria-hidden="true"
                ></span>

                <span>
                  {{ t("language.english") }}
                </span>

                <span
                  v-if="locale === 'en'"
                  aria-hidden="true"
                >
                  ✓
                </span>
              </button>
            </div>
          </details>
        </div>
      </div>
    </header>
    <main class="page-content">
      <p v-if="manifestError" class="notice">
        {{ manifestError }}
      </p>

      <section v-if="activeView === 'map'" class="workspace-card">
        <aside class="sidebar">
          <section>
            <h2>Territoire</h2>
            <label for="city">Ville</label>
            <select id="city" v-model="selectedCitySlug">
              <option
                v-for="city in availableCities"
                :key="city.slug"
                :value="city.slug"
              >
                {{ city.name }}
              </option>
            </select>
          </section>

          <section v-if="selectedIndicatorUsesScale">
            <h2>Échelle de proximité</h2>

            <label for="scale">Distance caractéristique λ</label>
            <select id="scale" v-model.number="selectedBw">
              <option
                v-for="scale in availableScales"
                :key="scale.bw"
                :value="scale.bw"
              >
                {{ scale.bw }} mètres
              </option>
            </select>

            <p class="scale-note">
              Seuil de calcul : {{ currentCutoff }} m, soit 5 × λ.
            </p>
          </section>

          <section>
            <h2>Indicateur affiché</h2>
            <p class="section-help">
              Une seule variable est représentée à la fois.
            </p>

            <div class="indicator-buttons">
              <button
                v-for="indicator in indicators"
                :key="indicator.key"
                type="button"
                :class="{
                  active: selectedIndicator === indicator.key,
                }"
                @click="selectedIndicator = indicator.key"
              >
                {{ indicator.label }}
              </button>
            </div>
          </section>
        </aside>

        <div class="map-panel">
          <ClientOnly>
            <MapView
              :indicator="selectedIndicator"
              :data-url="currentDataUrl"
              :boundary-url="currentBoundaryUrl"
              :city-name="currentCityName"
              :bw="selectedBw"
              :cutoff="currentCutoff"
              :dark-mode="darkMode"
            />

            <template #fallback>
              <div class="component-loading">
                Chargement de la carte…
              </div>
            </template>
          </ClientOnly>
        </div>
      </section>

      <section v-else-if="activeView === 'charts'" class="content-card">
        <div class="section-heading">
          <div>
            <span class="eyebrow">Analyse</span>
            <h2>Graphiques interactifs</h2>
            <p>
              Explorer les distributions, la structure commune des fonctions
              et les indicateurs urbains.
            </p>
          </div>
        </div>

        <nav class="chart-navigation" aria-label="Types de graphiques">
          <button
            type="button"
            :class="{ active: selectedChartSection === 'distribution' }"
            @click="selectedChartSection = 'distribution'"
          >
            Distributions
          </button>

          <button
            type="button"
            :class="{ active: selectedChartSection === 'structure' }"
            @click="selectedChartSection = 'structure'"
          >
            Structure commune
          </button>

          <button
            type="button"
            :class="{ active: selectedChartSection === 'indicators' }"
            @click="selectedChartSection = 'indicators'"
          >
            Indicateurs urbains
          </button>
        </nav>

        <div class="chart-controls">
          <label>
            Ville
            <select v-model="selectedCitySlug">
              <option
                v-for="city in availableCities"
                :key="city.slug"
                :value="city.slug"
              >
                {{ city.name }}
              </option>
            </select>
          </label>

          <label v-if="selectedChartSection === 'distribution'">
            Indicateur
            <select v-model="selectedIndicator">
              <option
                v-for="indicator in indicators"
                :key="indicator.key"
                :value="indicator.key"
              >
                {{ indicator.label }}
              </option>
            </select>
          </label>

          <label v-if="selectedChartSection === 'indicators'">
            Indicateur urbain
            <select v-model="selectedUrbanIndicator">
              <option value="population">
                Accessibilité–population (Pearson)
              </option>
              <option value="income">
                Accessibilité–revenu (Spearman)
              </option>
            </select>
          </label>

          <label
            v-if="
              selectedChartSection === 'indicators'
              || (
                selectedChartSection === 'distribution'
                && selectedIndicatorUsesScale
              )
            "
          >
            Échelle λ
            <select v-model.number="selectedBw">
              <option
                v-for="scale in availableScales"
                :key="scale.bw"
                :value="scale.bw"
              >
                {{ scale.bw }} m
              </option>
            </select>
          </label>
        </div>

        <ClientOnly>
          <ChartView
            v-if="selectedChartSection === 'distribution'"
            :indicator="selectedIndicator"
            :data-url="currentDataUrl"
            :city-name="currentCityName"
            :bw="selectedBw"
            :cutoff="currentCutoff"
          />

          <CommonStructureChart
            v-else-if="selectedChartSection === 'structure'"
            :city-name="currentCityName"
            :scales="availableScales"
            :threshold="pc1EvrThreshold"
          />

          <CityIndicatorsChart
            v-else
            :cities="availableCities"
            :bw="selectedBw"
            :metric="selectedUrbanIndicator"
            :selected-city-slug="selectedCitySlug"
          />

          <template #fallback>
            <div class="component-loading">
              Chargement du graphique…
            </div>
          </template>
        </ClientOnly>
      </section>

      <section v-else class="content-card method-page">
        <div class="section-heading">
          <div>
            <span class="eyebrow">Documentation</span>
            <h2>Méthode, paramètres et données</h2>
            <p>
              Les informations nécessaires pour interpréter correctement les
              cartes et les graphiques.
            </p>
          </div>
        </div>

        <div class="method-grid">
          <article>
            <h3>Unité spatiale</h3>
            <p>
              Les résultats sont agrégés sur le carroyage Insee de 200 mètres.
              La lecture proposée ici est locale à {{ currentCityName }}.
            </p>
          </article>

          <article>
            <h3>Accessibilité</h3>
            <p>
              Pour une fonction sociale <em>f</em>, l’accessibilité d’un lieu
              <em>g</em> est calculée par une somme pondérée des équipements :
            </p>
            <p class="formula">
              A<sub>g,f</sub>(λ) = Σ w<sub>i</sub> exp(−d<sub>g,i</sub>/λ)
            </p>
            <p>
              Le calcul s’arrête à 5 × λ. Lorsque λ vaut {{ selectedBw }} m,
              le seuil est donc {{ currentCutoff }} m.
            </p>
          </article>

          <article>
            <h3>Fonctions sociales</h3>
            <p>
              Cinq dimensions sont distinguées : commerce, santé, éducation,
              services du quotidien et loisirs, culture et sociabilité.
            </p>
          </article>

          <article>
            <h3>Lecture relative</h3>
            <p>
              Les fonctions sociales sont divisées par leur moyenne communale.
              La valeur 1 représente donc la moyenne de {{ currentCityName }}.
              Le rouge
              correspond aux valeurs inférieures à 1 et le vert aux valeurs
              supérieures à 1.
            </p>
          </article>

          <article>
            <h3>Limite communale</h3>
            <p>
              Le contour affiché provient de l’API officielle du découpage
              administratif. Il sert de repère territorial et ne remplace pas
              les carreaux utilisés pour les calculs.
            </p>
          </article>

          <article>
            <h3>Accessibilité générale</h3>
            <p>
              La PC1 résume la dimension commune aux cinq fonctions. Pour la
              carte locale, PC1 positive est divisée par sa moyenne communale.
              Cet indice relatif sert à comparer les quartiers d’une même ville,
              pas directement les niveaux absolus entre villes.
            </p>
          </article>

          <article>
            <h3>Revenu et population</h3>
            <p>
              Ces variables ne sont pas des indicateurs d’accessibilité. Elles
              sont représentées sur une échelle continue dans leurs unités
              observées : euros annuels par unité de consommation pour le
              niveau de vie et habitants par carreau pour la population. Elles
              ne dépendent pas de la distance caractéristique λ.
            </p>
          </article>
        </div>

        <div class="sources-panel">
          <h3>Principales sources</h3>
          <ul>
            <li>Insee — carroyage Filosofi 2021 et niveau de vie.</li>
            <li>Insee — Base permanente des équipements 2024.</li>
            <li>OpenStreetMap — équipements complémentaires et réseau piéton.</li>
            <li>
              API Découpage administratif — contours communaux officiels.
            </li>
            <li>Calculs et traitements issus des travaux de thèse.</li>
          </ul>
        </div>
      </section>
    </main>
  </div>
</template>

<style>
:root {
  color-scheme: light;
  --ink: #17202a;
  --muted: #627181;
  --navy: #17324d;
  --teal: #197278;
  --line: #dce3e9;
  --surface: #ffffff;
  --background: #eef2f5;
}

* {
  box-sizing: border-box;
}

html,
body,
#__nuxt {
  width: 100%;
  min-height: 100%;
  margin: 0;
}

body {
  color: var(--ink);
  background: var(--background);
  font-family: Inter, Arial, sans-serif;
}

button,
select {
  font: inherit;
}

.application {
  min-height: 100vh;
}

body,
.workspace-card,
.content-card,
select,
button {
  transition:
    color 160ms ease,
    background-color 160ms ease,
    border-color 160ms ease;
}

.header {
  color: white;
  background: var(--navy);
}

.header-inner {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 32px;
  width: min(1500px, 100%);
  margin: 0 auto;
  padding: 22px 28px 0;
}

.header h1 {
  margin: 0;
  font-size: clamp(22px, 2.2vw, 30px);
}

.header p {
  margin: 6px 0 22px;
  color: #cbd7e3;
}

.main-navigation {
  display: flex;
  gap: 4px;
}

.main-navigation button {
  padding: 13px 17px;
  color: #d9e4ee;
  background: transparent;
  border: 0;
  border-bottom: 3px solid transparent;
  cursor: pointer;
}

.main-navigation button:hover,
.main-navigation button.active {
  color: white;
  border-bottom-color: #59c3c3;
}

.theme-toggle {
  position: relative;
  display: grid;
  width: 40px;
  height: 40px;
  min-width: 40px;
  margin-bottom: 7px;
  padding: 0;
  color: #edf7fa;
  background: rgb(255 255 255 / 9%);
  border: 1px solid rgb(255 255 255 / 18%);
  border-radius: 50%;
  cursor: pointer;
  place-items: center;
  transition:
    background 160ms ease,
    border-color 160ms ease,
    transform 160ms ease;
}

.theme-toggle svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.theme-toggle:hover {
  background: rgb(255 255 255 / 17%);
  border-color: #59c3c3;
  transform: translateY(-1px);
}

.theme-toggle:focus-visible {
  outline: 2px solid #59c3c3;
  outline-offset: 3px;
}

/* Info-bulle */

.theme-toggle::after {
  position: absolute;
  z-index: 30;
  top: calc(100% + 10px);
  right: 0;
  width: max-content;
  max-width: 250px;
  padding: 7px 10px;
  color: #ffffff;
  background: #0b151e;
  border: 1px solid #405363;
  border-radius: 6px;
  box-shadow: 0 4px 14px rgb(0 0 0 / 25%);
  content: attr(data-tooltip);
  font-size: 12px;
  font-weight: 500;
  opacity: 0;
  pointer-events: none;
  transform: translateY(-4px);
  transition:
    opacity 150ms ease,
    transform 150ms ease;
  white-space: nowrap;
}

.theme-toggle:hover::after,
.theme-toggle:focus-visible::after {
  opacity: 1;
  transform: translateY(0);
}

.page-content {
  width: min(1500px, 100%);
  margin: 0 auto;
  padding: 24px 28px 40px;
}

.notice {
  margin: 0 0 14px;
  padding: 10px 14px;
  color: #6f4e00;
  background: #fff4cc;
  border: 1px solid #edd98b;
  border-radius: 8px;
  font-size: 14px;
}

.workspace-card,
.content-card {
  overflow: hidden;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  box-shadow: 0 8px 28px rgb(31 48 64 / 8%);
}

.workspace-card {
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
}

.sidebar {
  height: 690px;
  overflow-y: auto;
  padding: 22px;
  border-right: 1px solid var(--line);
}

.sidebar section + section {
  margin-top: 26px;
}

.sidebar h2 {
  margin: 0 0 11px;
  font-size: 16px;
}

.sidebar label,
.chart-controls label {
  display: grid;
  gap: 7px;
  color: #526170;
  font-size: 14px;
}

.sidebar select,
.chart-controls select {
  width: 100%;
  padding: 10px;
  color: var(--ink);
  background: white;
  border: 1px solid #cbd5df;
  border-radius: 7px;
}

.scale-note,
.section-help {
  margin: 9px 0 0;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.45;
}

.section-help {
  margin: -3px 0 11px;
}

.indicator-buttons {
  display: grid;
  gap: 7px;
}

.indicator-buttons button {
  padding: 9px 11px;
  color: #344454;
  text-align: left;
  background: #f3f6f8;
  border: 1px solid var(--line);
  border-radius: 7px;
  cursor: pointer;
}

.indicator-buttons button:hover {
  background: #e8eef2;
}

.indicator-buttons button.active {
  color: white;
  background: var(--teal);
  border-color: var(--teal);
}

.map-panel {
  height: 690px;
  min-width: 0;
}

.content-card {
  min-height: 620px;
  padding: 28px;
}

.section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 28px;
  margin-bottom: 28px;
  padding-bottom: 22px;
  border-bottom: 1px solid var(--line);
}

.section-heading h2 {
  margin: 4px 0 7px;
  font-size: 25px;
}

.section-heading p {
  max-width: 720px;
  margin: 0;
  color: var(--muted);
  line-height: 1.55;
}

.eyebrow {
  color: var(--teal);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.chart-controls {
  display: grid;
  grid-template-columns: repeat(3, minmax(170px, 240px));
  gap: 12px;
  margin-bottom: 28px;
}

.chart-navigation {
  display: flex;
  gap: 6px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  overflow-x: auto;
  border-bottom: 1px solid var(--line);
}

.chart-navigation button {
  padding: 9px 14px;
  color: #425262;
  white-space: nowrap;
  background: #f3f6f8;
  border: 1px solid var(--line);
  border-radius: 7px;
  cursor: pointer;
}

.chart-navigation button:hover {
  background: #e8eef2;
}

.chart-navigation button.active {
  color: white;
  background: var(--teal);
  border-color: var(--teal);
}

.method-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.method-grid article,
.sources-panel {
  padding: 20px;
  background: #f8fafb;
  border: 1px solid var(--line);
  border-radius: 10px;
}

.method-grid h3,
.sources-panel h3 {
  margin: 0 0 9px;
  font-size: 16px;
}

.method-grid p,
.sources-panel li {
  color: #4f5f6e;
  line-height: 1.6;
}

.formula {
  overflow-x: auto;
  padding: 10px 12px;
  color: var(--ink) !important;
  background: white;
  border-left: 3px solid var(--teal);
  font-family: Georgia, serif;
}

.sources-panel {
  margin-top: 16px;
}

.sources-panel ul {
  margin: 0;
  padding-left: 20px;
}

.component-loading {
  display: grid;
  width: 100%;
  min-height: 420px;
  color: var(--muted);
  place-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.language-menu {
  position: relative;
}

.language-toggle {
  list-style: none;
}

.language-toggle::-webkit-details-marker {
  display: none;
}

.language-menu[open] .language-toggle {
  color: #ffffff;
  background: rgb(89 195 195 / 25%);
  border-color: #59c3c3;
}

.language-menu[open] .language-toggle::after {
  display: none;
}

.language-options {
  position: absolute;
  z-index: 50;
  top: calc(100% + 7px);
  right: 0;
  display: grid;
  gap: 4px;
  width: 150px;
  padding: 6px;
  color: var(--ink);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 9px;
  box-shadow: 0 8px 25px rgb(0 0 0 / 22%);
}

.language-options button:hover {
  background: var(--background);
}

.language-options button.active {
  color: #ffffff;
  background: var(--teal);
}

.language-toggle {
  position: relative;
}

.current-language-flag {
  position: absolute;
  right: -5px;
  bottom: -3px;
  width: 21px;
  height: 14px;
  border: 2px solid var(--navy);
  border-radius: 3px;
  box-shadow: 0 1px 4px rgb(0 0 0 / 28%);
}

.language-options button {
  display: grid;
  grid-template-columns: 23px 1fr 16px;
  align-items: center;
  gap: 8px;
  padding: 9px 10px;
  color: var(--ink);
  text-align: left;
  background: transparent;
  border: 0;
  border-radius: 6px;
  cursor: pointer;
}

.language-flag {
  display: inline-block;
  width: 23px;
  height: 15px;
  border: 1px solid rgb(0 0 0 / 18%);
  border-radius: 2px;
  box-shadow: 0 1px 2px rgb(0 0 0 / 15%);
}

/* Drapeau français */

.flag-fr {
  background: linear-gradient(
    to right,
    #0055a4 0 33.33%,
    #ffffff 33.33% 66.66%,
    #ef4135 66.66% 100%
  );
}

/* Drapeau britannique */

.flag-gb {
  background:
    linear-gradient(
      to right,
      transparent 44%,
      #c8102e 44% 56%,
      transparent 56%
    ),
    linear-gradient(
      to bottom,
      transparent 39%,
      #c8102e 39% 61%,
      transparent 61%
    ),
    linear-gradient(
      28deg,
      transparent 47%,
      #c8102e 47% 53%,
      transparent 53%
    ),
    linear-gradient(
      -28deg,
      transparent 47%,
      #c8102e 47% 53%,
      transparent 53%
    ),
    linear-gradient(
      to right,
      transparent 36%,
      #ffffff 36% 64%,
      transparent 64%
    ),
    linear-gradient(
      to bottom,
      transparent 28%,
      #ffffff 28% 72%,
      transparent 72%
    ),
    linear-gradient(
      28deg,
      transparent 42%,
      #ffffff 42% 58%,
      transparent 58%
    ),
    linear-gradient(
      -28deg,
      transparent 42%,
      #ffffff 42% 58%,
      transparent 58%
    ),
    #012169;
}

html[data-theme="dark"] {
  color-scheme: dark;
  --ink: #edf3f8;
  --muted: #a9b7c5;
  --navy: #0a2033;
  --teal: #2c9ea3;
  --line: #334654;
  --surface: #14232f;
  --background: #0b151e;
}

html[data-theme="dark"] .sidebar select,
html[data-theme="dark"] .chart-controls select {
  color: #edf3f8;
  background: #1c2d39;
  border-color: #405363;
}

html[data-theme="dark"] .indicator-buttons button,
html[data-theme="dark"] .chart-navigation button {
  color: #edf3f8;
  background: #1b2b37;
  border-color: #334654;
}

html[data-theme="dark"] .indicator-buttons button:hover,
html[data-theme="dark"] .chart-navigation button:hover {
  background: #263946;
}

html[data-theme="dark"] .indicator-buttons button.active,
html[data-theme="dark"] .chart-navigation button.active {
  color: white;
  background: var(--teal);
  border-color: var(--teal);
}

html[data-theme="dark"] .sidebar label,
html[data-theme="dark"] .chart-controls label,
html[data-theme="dark"] .method-grid p,
html[data-theme="dark"] .sources-panel li {
  color: #bdc9d3;
}

html[data-theme="dark"] .method-grid article,
html[data-theme="dark"] .sources-panel {
  background: #1b2b37;
  border-color: #334654;
}

html[data-theme="dark"] .formula {
  color: #edf3f8 !important;
  background: #1c2d39;
}

html[data-theme="dark"] .map-message,
html[data-theme="dark"] .legend,
html[data-theme="dark"] .maplibregl-popup-content,
html[data-theme="dark"] .parameter-chip,
html[data-theme="dark"] .scale-summary,
html[data-theme="dark"] .chart-detail,
html[data-theme="dark"] .structure-tooltip {
  color: #edf3f8;
  background: rgb(20 35 47 / 96%);
  border-color: #334654;
}

html[data-theme="dark"] .chart-status,
html[data-theme="dark"] .chart-reading,
html[data-theme="dark"] .chart-header p,
html[data-theme="dark"] .chart-detail span,
html[data-theme="dark"] .axis-values,
html[data-theme="dark"] .legend-subtitle,
html[data-theme="dark"] .legend-note,
html[data-theme="dark"] .empty-state {
  color: #a9b7c5;
}

html[data-theme="dark"] .histogram {
  background:
    repeating-linear-gradient(
      to top,
      #14232f 0,
      #14232f 69px,
      #334654 70px
    );
  border-bottom-color: #536675;
}

html[data-theme="dark"] .ranking-row:hover,
html[data-theme="dark"] .ranking-row.active {
  background: #263946;
  border-color: #334654;
}

html[data-theme="dark"] .grid-line {
  stroke: #334654;
}

html[data-theme="dark"] .tick-label,
html[data-theme="dark"] .axis-title {
  fill: #bdc9d3 !important;
}

@media (max-width: 900px) {
  .header-inner,
  .section-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .header-inner {
    padding-bottom: 0;
  }

  .header p {
    margin-bottom: 4px;
  }

  .main-navigation {
    overflow-x: auto;
  }

  .theme-toggle {
    align-self: flex-start;
    margin-bottom: 10px;
  }

  .workspace-card {
    grid-template-columns: 1fr;
  }

  .sidebar {
    height: auto;
    max-height: 520px;
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }

  .map-panel {
    height: 65vh;
    min-height: 520px;
  }

  .chart-controls {
    grid-template-columns: 1fr;
    min-width: 0;
  }

  .method-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .header-inner,
  .page-content {
    padding-right: 14px;
    padding-left: 14px;
  }

  .content-card {
    padding: 20px;
  }
}

/* Correction de la lisibilité des graphiques en mode sombre */

html[data-theme="dark"] .content-card h2,
html[data-theme="dark"] .content-card h3,
html[data-theme="dark"] .content-card strong {
  color: #edf3f8 !important;
}

/* Graphique des indicateurs urbains */

html[data-theme="dark"] .indicator-chart,
html[data-theme="dark"] .ranking-row,
html[data-theme="dark"] .city-name {
  color: #dce6ed !important;
}

html[data-theme="dark"] .coefficient {
  color: #ffffff !important;
}

html[data-theme="dark"] .rank,
html[data-theme="dark"] .coefficient-axis,
html[data-theme="dark"] .scale-summary span {
  color: #a9b7c5 !important;
}

html[data-theme="dark"] .scale-summary strong,
html[data-theme="dark"] .chart-detail strong {
  color: #edf3f8 !important;
}

html[data-theme="dark"] .ranking-row:hover,
html[data-theme="dark"] .ranking-row.active {
  color: #ffffff !important;
  background: #263946;
  border-color: #405363;
}

html[data-theme="dark"] .ranking-row.selected .city-name {
  color: #62d0d2 !important;
}

/* Histogrammes */

html[data-theme="dark"] .bar-count,
html[data-theme="dark"] .bar-label {
  color: #bdc9d3 !important;
}

/* Textes présents dans les graphiques SVG */

html[data-theme="dark"] .tick-label {
  fill: #bdc9d3 !important;
}

html[data-theme="dark"] .axis-title {
  fill: #edf3f8 !important;
}

html[data-theme="dark"] .point-label {
  fill: #5fd0c8 !important;
}

html[data-theme="dark"] .threshold-label {
  fill: #fbbf24 !important;
}

/* Structure commune — correction du mode sombre */

html[data-theme="dark"] .threshold-summary,
html[data-theme="dark"] .chart-reading {
  color: #dce6ed !important;
  background: #1c2d39 !important;
  border-color: #405363 !important;
}

html[data-theme="dark"] .threshold-summary strong {
  color: #ffffff !important;
}

html[data-theme="dark"] .chart-reading strong {
  color: #62d0d2 !important;
}

/* Graduations et textes du graphique */

html[data-theme="dark"] .structure-chart .grid text,
html[data-theme="dark"] .structure-chart .plot text {
  fill: #a9bdca !important;
}

html[data-theme="dark"] .structure-chart .axis-title {
  fill: #edf3f8 !important;
}

html[data-theme="dark"] .structure-chart .threshold-label {
  fill: #fbbf24 !important;
}

/* Traits et grille */

html[data-theme="dark"] .structure-chart .grid line {
  stroke: #405363;
}

html[data-theme="dark"] .structure-chart .axis,
html[data-theme="dark"] .structure-chart .tick-mark {
  stroke: #718494;
}

/* Petit titre et infobulle */

html[data-theme="dark"] .structure-chart .chart-kicker {
  color: #5fd0c8 !important;
}

html[data-theme="dark"] .structure-chart .chart-tooltip {
  color: #edf3f8;
  background: rgb(20 35 47 / 97%);
  border-color: #405363;
}
</style>
