<template>
  <div class="map-wrapper">
    <div ref="mapContainer" class="map"></div>

    <div v-if="loading" class="map-message">
      {{ loadingText }}
    </div>

    <div v-else-if="errorMessage" class="map-message error">
      {{ errorMessage }}
    </div>

    <div v-if="!loading && !errorMessage" class="legend">
      <strong>{{ activeIndicator.label }}</strong>
      <span
        v-if="activeIndicator.dependsOnScale"
        class="legend-subtitle"
      >
        λ = {{ bw }} m · seuil = {{ cutoff }} m
      </span>
      <span v-else class="legend-subtitle">
        {{ cityName }} · valeurs observées
      </span>

      <template v-if="activeIndicator.mode === 'relative'">
        <div class="continuous-gradient"></div>

        <div class="gradient-values">
          <span>{{ formatLegendNumber(relativeDomain.lower) }}</span>
          <span class="average-value">1</span>
          <span>{{ formatLegendNumber(relativeDomain.upper) }}</span>
        </div>

        <div class="gradient-meaning">
          <span>Inférieur</span>
          <span>Moyenne</span>
          <span>Supérieur</span>
        </div>

        <p class="legend-note">
          1 = moyenne de {{ cityName }}
        </p>
      </template>

      <template v-else>
        <div 
           class="value-gradient"
           :style="{ background: valueGradient }"
        ></div>

        <div class="gradient-values value-labels">
          <span>{{ formatLegendValue(valueDomain.lower) }}</span>
          <span>{{ formatLegendValue(valueDomain.middle) }}</span>
          <span>{{ formatLegendValue(valueDomain.upper) }}</span>
        </div>

        <p class="legend-note">
          Couleurs bornées aux 5e et 95e percentiles.
        </p>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  Map as MapLibreMap,
  NavigationControl,
  Popup,
  ScaleControl,
  setWorkerUrl,
} from "maplibre-gl"

import maplibreWorkerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url"

import "maplibre-gl/dist/maplibre-gl.css"

setWorkerUrl(maplibreWorkerUrl)

type IndicatorMode = "relative" | "value"

interface IndicatorConfig {
  label: string
  valueProperty: string
  mode: IndicatorMode
  decimals: number
  dependsOnScale: boolean
  unit?: string
  colors?: readonly [string, string, string]
}

interface WebFeature {
  properties: Record<string, unknown> | null
  geometry?: {
    coordinates?: unknown
  } | null
}

interface WebFeatureCollection {
  type: "FeatureCollection"
  features: WebFeature[]
}

interface RelativeDomain {
  lower: number
  upper: number
}

interface ValueDomain {
  lower: number
  middle: number
  upper: number
}

const props = defineProps<{
  indicator: string
  dataUrl: string
  boundaryUrl: string
  cityName: string
  bw: number
  cutoff: number
  darkMode: boolean
}>()

const mapContainer = ref<HTMLDivElement | null>(null)
const loading = ref(true)
const errorMessage = ref("")
const relativeDomain = ref<RelativeDomain>({
  lower: 0,
  upper: 2,
})
const valueDomain = ref<ValueDomain>({
  lower: 0,
  middle: 0.5,
  upper: 1,
})

let map: MapLibreMap | null = null
let hoverPopup: Popup | null = null
let currentData: WebFeatureCollection | null = null
let currentBoundary: WebFeatureCollection | null = null
let requestNumber = 0
let boundaryRequestNumber = 0
let eventsInstalled = false

const defaultIndicator: IndicatorConfig = {
  label: "Accessibilité générale",
  valueProperty: "rel_pc1",
  mode: "relative",
  decimals: 2,
  dependsOnScale: true,
}

const indicatorConfigs: Record<string, IndicatorConfig> = {
  pc1: defaultIndicator,
  commerce: {
    label: "Accessibilité au commerce",
    valueProperty: "rel_commerce",
    mode: "relative",
    decimals: 2,
    dependsOnScale: true,
  },
  sante: {
    label: "Accessibilité à la santé",
    valueProperty: "rel_sante",
    mode: "relative",
    decimals: 2,
    dependsOnScale: true,
  },
  education: {
    label: "Accessibilité à l'éducation",
    valueProperty: "rel_education",
    mode: "relative",
    decimals: 2,
    dependsOnScale: true,
  },
  services: {
    label: "Accessibilité aux services",
    valueProperty: "rel_services",
    mode: "relative",
    decimals: 2,
    dependsOnScale: true,
  },
  loisirs: {
    label: "Accessibilité aux loisirs",
    valueProperty: "rel_loisirs",
    mode: "relative",
    decimals: 2,
    dependsOnScale: true,
  },
  revenu: {
  label: "Niveau de vie",
  valueProperty: "nivvie",
  mode: "value",
  decimals: 0,
  dependsOnScale: false,
  unit: "€",
  colors: [
    "#f2f0f7",
    "#9e9ac8",
    "#54278f",
  ],
},

population: {
  label: "Population",
  valueProperty: "population",
  mode: "value",
  decimals: 0,
  dependsOnScale: false,
  unit: "hab.",
  colors: [
    "#fff7bc",
    "#fec44f",
    "#d7301f",
  ],
},
}

const activeIndicator = computed(() => {
  return indicatorConfigs[props.indicator] ?? defaultIndicator
})

const defaultValueColors = [
  "#f2f0f7",
  "#9e9ac8",
  "#54278f",
] as const

const valueColors = computed(() => {
  return activeIndicator.value.colors ?? defaultValueColors
})

const valueGradient = computed(() => {
  const [lowColor, middleColor, highColor] = valueColors.value

  return (
    `linear-gradient(90deg, `
    + `${lowColor} 0%, `
    + `${middleColor} 50%, `
    + `${highColor} 100%)`
  )
})

const loadingText = computed(() => {
  return activeIndicator.value.dependsOnScale
    ? `Chargement de l’échelle ${props.bw} m…`
    : `Chargement des données de ${props.cityName}…`
})

function quantile(sortedValues: number[], probability: number) {
  if (sortedValues.length === 0) {
    return Number.NaN
  }

  const position = (sortedValues.length - 1) * probability
  const lowerIndex = Math.floor(position)
  const upperIndex = Math.ceil(position)
  const weight = position - lowerIndex

  if (lowerIndex === upperIndex) {
    return sortedValues[lowerIndex]
  }

  return (
    sortedValues[lowerIndex] * (1 - weight)
    + sortedValues[upperIndex] * weight
  )
}

function valuesForProperty(property: string) {
  if (!currentData) {
    return []
  }

  return currentData.features
    .map((feature) => feature.properties?.[property])
    .filter((value) => value !== null && value !== undefined && value !== "")
    .map((value) => Number(value))
    .filter((value) => Number.isFinite(value))
    .sort((first, second) => first - second)
}

function calculateRelativeDomain(property: string): RelativeDomain {
  const values = valuesForProperty(property)

  if (values.length === 0) {
    return { lower: 0, upper: 2 }
  }

  const percentile05 = quantile(values, 0.05)
  const percentile95 = quantile(values, 0.95)
  const amplitude = Math.max(
    1 - percentile05,
    percentile95 - 1,
    0.1,
  )

  return {
    lower: Math.max(0, 1 - amplitude),
    upper: 1 + amplitude,
  }
}

function calculateValueDomain(property: string): ValueDomain {
  const values = valuesForProperty(property)

  if (values.length === 0) {
    return { lower: 0, middle: 0.5, upper: 1 }
  }

  let lower = quantile(values, 0.05)
  let upper = quantile(values, 0.95)

  if (lower === upper) {
    const padding = Math.max(Math.abs(lower) * 0.05, 1)
    lower -= padding
    upper += padding
  }

  return {
    lower,
    middle: (lower + upper) / 2,
    upper,
  }
}

function relativeColorExpression(
  property: string,
  domain: RelativeDomain,
): any {
  const lowerMiddle = (domain.lower + 1) / 2
  const upperMiddle = (domain.upper + 1) / 2

  return [
    "interpolate",
    ["linear"],
    ["to-number", ["get", property], 1],
    domain.lower,
    "#b2182b",
    lowerMiddle,
    "#ef8a62",
    1,
    "#f7f7f7",
    upperMiddle,
    "#66bd63",
    domain.upper,
    "#1a9850",
  ]
}

function valueColorExpression(
  property: string,
  domain: ValueDomain,
  colors: readonly [string, string, string],
): any {
  const [lowColor, middleColor, highColor] = colors

  return [
    "interpolate",
    ["linear"],
    ["to-number", ["get", property], domain.lower],
    domain.lower,
    lowColor,
    domain.middle,
    middleColor,
    domain.upper,
    highColor,
  ]
}

function updateRendering() {
  if (!map || !map.getLayer("carreaux-remplissage")) {
    return
  }

  const config = activeIndicator.value

  if (config.mode === "relative") {
    relativeDomain.value = calculateRelativeDomain(config.valueProperty)

    map.setPaintProperty(
      "carreaux-remplissage",
      "fill-color",
      relativeColorExpression(
        config.valueProperty,
        relativeDomain.value,
      ),
    )
  } else {
    valueDomain.value = calculateValueDomain(config.valueProperty)

    map.setPaintProperty(
      "carreaux-remplissage",
      "fill-color",
      valueColorExpression(
        config.valueProperty,
        valueDomain.value,
         valueColors.value,
     ),
    )
  }

  hoverPopup?.remove()
}

function formatValue(value: unknown, config: IndicatorConfig) {
  if (value === null || value === undefined || value === "") {
    return "Non renseigné"
  }

  const number = Number(value)

  if (!Number.isFinite(number)) {
    return "Non renseigné"
  }

  const formatted = number.toLocaleString("fr-FR", {
    maximumFractionDigits: config.decimals,
  })

  return config.unit ? `${formatted} ${config.unit}` : formatted
}

function formatLegendNumber(value: number) {
  return value.toLocaleString("fr-FR", {
    maximumFractionDigits: 2,
  })
}

function formatLegendValue(value: number) {
  return formatValue(value, activeIndicator.value)
}

function relativeDifferenceText(value: number) {
  const difference = Math.round(Math.abs(value - 1) * 100)

  if (difference === 0) {
    return `Au niveau de la moyenne de ${props.cityName}`
  }

  return value < 1
    ? `${difference} % sous la moyenne de ${props.cityName}`
    : `${difference} % au-dessus de la moyenne de ${props.cityName}`
}

function calculateBounds(
  data: WebFeatureCollection,
): [[number, number], [number, number]] | null {
  let minimumLongitude = Number.POSITIVE_INFINITY
  let minimumLatitude = Number.POSITIVE_INFINITY
  let maximumLongitude = Number.NEGATIVE_INFINITY
  let maximumLatitude = Number.NEGATIVE_INFINITY

  function visitCoordinates(value: unknown) {
    if (!Array.isArray(value)) {
      return
    }

    if (
      value.length >= 2
      && typeof value[0] === "number"
      && typeof value[1] === "number"
    ) {
      minimumLongitude = Math.min(minimumLongitude, value[0])
      minimumLatitude = Math.min(minimumLatitude, value[1])
      maximumLongitude = Math.max(maximumLongitude, value[0])
      maximumLatitude = Math.max(maximumLatitude, value[1])
      return
    }

    for (const child of value) {
      visitCoordinates(child)
    }
  }

  for (const feature of data.features) {
    visitCoordinates(feature.geometry?.coordinates)
  }

  if (
    !Number.isFinite(minimumLongitude)
    || !Number.isFinite(minimumLatitude)
    || !Number.isFinite(maximumLongitude)
    || !Number.isFinite(maximumLatitude)
  ) {
    return null
  }

  return [
    [minimumLongitude, minimumLatitude],
    [maximumLongitude, maximumLatitude],
  ]
}

function fitToData(data: WebFeatureCollection) {
  if (!map) {
    return
  }

  const bounds = calculateBounds(data)

  if (!bounds) {
    return
  }

  map.fitBounds(bounds, {
    padding: 38,
    duration: 650,
    maxZoom: 12,
  })
}

function bringBoundaryToFront() {
  if (!map) {
    return
  }

  if (map.getLayer("limite-communale-halo")) {
    map.moveLayer("limite-communale-halo")
  }

  if (map.getLayer("limite-communale-ligne")) {
    map.moveLayer("limite-communale-ligne")
  }
}

function setEmptyBoundary() {
  if (!map) {
    return
  }

  const source = map.getSource("limite-communale") as any

  if (source) {
    source.setData({
      type: "FeatureCollection",
      features: [],
    })
  }
}

async function loadBoundary() {
  if (!map) {
    return
  }

  const activeRequest = ++boundaryRequestNumber
  currentBoundary = null
  setEmptyBoundary()

  if (!props.boundaryUrl) {
    if (currentData) {
      fitToData(currentData)
    }
    return
  }

  try {
    const response = await fetch(props.boundaryUrl)

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const boundary = (await response.json()) as WebFeatureCollection

    if (activeRequest !== boundaryRequestNumber) {
      return
    }

    if (!Array.isArray(boundary.features) || boundary.features.length === 0) {
      throw new Error("La limite communale est vide.")
    }

    currentBoundary = boundary

    const existingSource = map.getSource("limite-communale") as any

    if (existingSource) {
      existingSource.setData(boundary as any)
    } else {
      map.addSource("limite-communale", {
        type: "geojson",
        data: boundary as any,
      })

      map.addLayer({
        id: "limite-communale-halo",
        type: "line",
        source: "limite-communale",
        paint: {
          "line-color": "#ffffff",
          "line-width": 5,
          "line-opacity": 0.9,
        },
      })

      map.addLayer({
        id: "limite-communale-ligne",
        type: "line",
        source: "limite-communale",
        paint: {
          "line-color": "#17202a",
          "line-width": 2.2,
          "line-opacity": 0.95,
        },
      })
    }

    bringBoundaryToFront()
    fitToData(boundary)
  } catch (error) {
    if (activeRequest !== boundaryRequestNumber) {
      return
    }

    console.error(
      `Erreur de chargement de la limite de ${props.cityName} :`,
      error,
    )

    if (currentData) {
      fitToData(currentData)
    }
  }
}

function installMapEvents(carte: MapLibreMap) {
  if (eventsInstalled) {
    return
  }

  eventsInstalled = true

  hoverPopup = new Popup({
    closeButton: false,
    closeOnClick: false,
    offset: 12,
  })

  carte.on("mousemove", "carreaux-remplissage", (event) => {
    const properties = event.features?.[0]?.properties

    if (!properties || !hoverPopup) {
      return
    }

    const config = activeIndicator.value
    const rawValue = properties[config.valueProperty]
    const numericValue =
      rawValue === null || rawValue === undefined || rawValue === ""
        ? Number.NaN
        : Number(rawValue)

    let detail = ""

    if (config.mode === "relative") {
      detail = Number.isFinite(numericValue)
        ? `<div>${relativeDifferenceText(numericValue)}</div>`
        : ""
    }

    carte.getCanvas().style.cursor = "pointer"

    hoverPopup
      .setLngLat(event.lngLat)
      .setHTML(`
        <div class="indicator-popup">
          <strong>${config.label}</strong>
          <div>Valeur : ${formatValue(rawValue, config)}</div>
          ${detail}
        </div>
      `)
      .addTo(carte)
  })

  carte.on("mouseleave", "carreaux-remplissage", () => {
    carte.getCanvas().style.cursor = ""
    hoverPopup?.remove()
  })
}

async function loadData() {
  if (!map || !props.dataUrl) {
    return
  }

  const activeRequest = ++requestNumber
  loading.value = true
  errorMessage.value = ""
  hoverPopup?.remove()

  try {
    const response = await fetch(props.dataUrl)

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const data = (await response.json()) as WebFeatureCollection

    if (activeRequest !== requestNumber) {
      return
    }

    if (!Array.isArray(data.features) || data.features.length === 0) {
      throw new Error("Le GeoJSON ne contient aucun carreau.")
    }

    currentData = data

    const existingSource = map.getSource("carreaux") as any

    if (existingSource) {
      existingSource.setData(data as any)
    } else {
      map.addSource("carreaux", {
        type: "geojson",
        data: data as any,
        generateId: true,
      })

      map.addLayer({
        id: "carreaux-remplissage",
        type: "fill",
        source: "carreaux",
        paint: {
          "fill-color": "#f7f7f7",
          "fill-opacity": 0.78,
        },
      })

      map.addLayer({
        id: "carreaux-contours",
        type: "line",
        source: "carreaux",
        paint: {
          "line-color": "#ffffff",
          "line-width": 0.25,
          "line-opacity": 0.35,
        },
      })

      installMapEvents(map)
    }

    updateRendering()
    bringBoundaryToFront()

    if (!currentBoundary) {
      fitToData(data)
    }
  } catch (error) {
    if (activeRequest !== requestNumber) {
      return
    }

    console.error("Erreur de chargement des carreaux :", error)
    errorMessage.value = activeIndicator.value.dependsOnScale
      ? `Impossible de charger ${props.cityName} pour λ = ${props.bw} m.`
      : `Impossible de charger les données de ${props.cityName}.`
  } finally {
    if (activeRequest === requestNumber) {
      loading.value = false
    }
  }
}

const BASEMAP_LIGHT =
  "https://tiles.openfreemap.org/styles/liberty"

const BASEMAP_DARK =
  "https://tiles.openfreemap.org/styles/dark"

function getBasemapStyle() {
  return props.darkMode
    ? BASEMAP_DARK
    : BASEMAP_LIGHT
}

function updateBasemapTheme() {
  if (!map) {
    return
  }

  map.setStyle(getBasemapStyle())
}

onMounted(() => {
  if (!mapContainer.value) {
    return
  }

  const carte = new MapLibreMap({
    container: mapContainer.value,
    style: getBasemapStyle(),
    center: [5.3698, 43.2965],
    zoom: 10.5,
  })

  map = carte

  carte.addControl(
    new NavigationControl(),
    "top-right",
  )

  carte.addControl(
    new ScaleControl({
      unit: "metric",
    }),
    "bottom-left",
  )

  carte.on("error", (event) => {
    console.error(
      "Erreur MapLibre :",
      event.error,
    )
  })

  const initializeThematicLayers = () => {
    void loadData()
    void loadBoundary()
  }

  /*
   * L’événement reste actif afin de recharger les carreaux
   * et la limite lorsque le thème cartographique change.
   */
  carte.on(
    "style.load",
    initializeThematicLayers,
  )

  /*
   * Cas où le style serait déjà chargé au moment
   * de l’installation de l’événement.
   */
  if (carte.isStyleLoaded()) {
    initializeThematicLayers()
  }
})

watch(
  () => props.dataUrl,
  () => {
    if (map?.isStyleLoaded()) {
      loadData()
    }
  },
)

watch(
  () => props.boundaryUrl,
  () => {
    if (map?.isStyleLoaded()) {
      loadBoundary()
    }
  },
)

watch(
  () => props.indicator,
  () => {
    updateRendering()
  },
)

watch(
  () => props.darkMode,
  () => {
    updateBasemapTheme()
  },
)

onBeforeUnmount(() => {
  requestNumber += 1
  boundaryRequestNumber += 1
  hoverPopup?.remove()
  map?.remove()

  hoverPopup = null
  currentData = null
  currentBoundary = null
  map = null
})
</script>

<style scoped>
.map-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 500px;
}

.map {
  width: 100%;
  height: 100%;
}

.map-message {
  position: absolute;
  top: 14px;
  left: 50%;
  z-index: 3;
  padding: 9px 13px;
  color: #344454;
  background: rgb(255 255 255 / 95%);
  border: 1px solid #d8e0e7;
  border-radius: 7px;
  box-shadow: 0 2px 8px rgb(0 0 0 / 14%);
  transform: translateX(-50%);
}

.map-message.error {
  color: #8c2430;
  border-color: #e5b4ba;
}

.legend {
  position: absolute;
  right: 14px;
  bottom: 36px;
  z-index: 2;
  width: 230px;
  padding: 13px;
  color: #17202a;
  background: rgb(255 255 255 / 94%);
  border: 1px solid #d8e0e7;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgb(0 0 0 / 16%);
  font-size: 13px;
}

.legend strong,
.legend-subtitle {
  display: block;
}

.legend-subtitle {
  margin: 3px 0 11px;
  color: #63717e;
  font-size: 12px;
}

.continuous-gradient {
  height: 14px;
  background: linear-gradient(
    90deg,
    #b2182b 0%,
    #ef8a62 25%,
    #f7f7f7 50%,
    #66bd63 75%,
    #1a9850 100%
  );
  border: 1px solid rgb(0 0 0 / 12%);
  border-radius: 3px;
}

.value-gradient {
  height: 14px;
  background: linear-gradient(
    90deg,
    #fff7fb 0%,
    #67a9cf 50%,
    #045a8d 100%
  );
  border: 1px solid rgb(0 0 0 / 12%);
  border-radius: 3px;
}

.gradient-values,
.gradient-meaning {
  display: flex;
  justify-content: space-between;
  gap: 6px;
}

.gradient-values {
  margin-top: 4px;
  font-variant-numeric: tabular-nums;
}

.gradient-meaning {
  margin-top: 2px;
  color: #6b7784;
  font-size: 10px;
}

.average-value {
  font-weight: 700;
}

.value-labels {
  align-items: flex-start;
  font-size: 11px;
}

.value-labels span:nth-child(2) {
  text-align: center;
}

.value-labels span:last-child {
  text-align: right;
}

.legend-note {
  margin: 8px 0 0;
  color: #526170;
  font-size: 11px;
}

:deep(.maplibregl-popup-content) {
  min-width: 190px;
  padding: 10px 12px;
  line-height: 1.55;
}

:deep(.indicator-popup strong) {
  display: block;
  margin-bottom: 4px;
}
</style>
