<template>
  <div class="chart-shell">
    <div class="chart-meta">
      <div>
        <span class="chart-kicker">{{ activeIndicator.label }}</span>
        <h3>{{ chartTitle }}</h3>
      </div>

      <div class="parameter-chip">
        {{ cityName }}
        <template v-if="activeIndicator.dependsOnScale">
          · λ {{ bw }} m · seuil {{ cutoff }} m
        </template>
      </div>
    </div>

    <div v-if="loading" class="chart-status">
      Chargement des données…
    </div>

    <div v-else-if="errorMessage" class="chart-status error">
      {{ errorMessage }}
    </div>

    <template v-else>
      <div class="histogram">
        <div
          v-if="averagePosition !== null"
          class="average-line"
          :style="{ left: `${averagePosition}%` }"
        >
          <span>Moyenne = 1</span>
        </div>

        <div class="bars">
          <button
            v-for="bar in bars"
            :key="bar.key"
            type="button"
            class="bar-column"
            :aria-label="bar.detail"
            @mouseenter="hoveredBar = bar"
            @mouseleave="hoveredBar = null"
            @focus="hoveredBar = bar"
            @blur="hoveredBar = null"
          >
            <span class="bar-count">{{ bar.count }}</span>
            <span
              class="bar"
              :style="{
                height: `${barHeight(bar.count)}%`,
                backgroundColor: bar.color,
              }"
            ></span>
            <span v-if="bar.label" class="bar-label">
              {{ bar.label }}
            </span>
          </button>
        </div>
      </div>

      <div class="axis-values">
        <span>{{ formatAxisValue(axisMinimum) }}</span>
        <span>{{ axisLabel }}</span>
        <span>{{ formatAxisValue(axisMaximum) }}</span>
      </div>

      <div class="chart-detail">
        <template v-if="hoveredBar">
          <strong>{{ hoveredBar.detail }}</strong>
          <span>{{ hoveredBar.count }} carreau(x)</span>
        </template>

        <template v-else>
          <strong>{{ validCount.toLocaleString("fr-FR") }} carreaux analysés</strong>
          <span>Survole une barre pour afficher son détail.</span>
        </template>
      </div>

      <p class="chart-reading">
        {{ readingText }}
      </p>
    </template>
  </div>
</template>

<script setup lang="ts">
type IndicatorMode = "relative" | "value"

interface IndicatorConfig {
  label: string
  valueProperty: string
  mode: IndicatorMode
  decimals: number
  dependsOnScale: boolean
  unit?: string
}

interface ChartFeature {
  properties: Record<string, unknown> | null
}

interface ChartFeatureCollection {
  features: ChartFeature[]
}

interface ChartBar {
  key: string
  label: string
  count: number
  color: string
  detail: string
}

const props = defineProps<{
  indicator: string
  dataUrl: string
  cityName: string
  bw: number
  cutoff: number
}>()

const loading = ref(true)
const errorMessage = ref("")
const bars = ref<ChartBar[]>([])
const hoveredBar = ref<ChartBar | null>(null)
const validCount = ref(0)
const axisMinimum = ref(0)
const axisMaximum = ref(2)
const averagePosition = ref<number | null>(50)

let currentData: ChartFeatureCollection | null = null
let requestNumber = 0

const defaultIndicator: IndicatorConfig = {
  label: "Accessibilité synthétique (PC1)",
  valueProperty: "rel_pc1",
  mode: "relative",
  decimals: 2,
  dependsOnScale: true,
}

const indicatorConfigs: Record<string, IndicatorConfig> = {
  pc1: defaultIndicator,
  commerce: {
    label: "Accessibilité — Commerce",
    valueProperty: "rel_commerce",
    mode: "relative",
    decimals: 2,
    dependsOnScale: true,
  },
  sante: {
    label: "Accessibilité — Santé",
    valueProperty: "rel_sante",
    mode: "relative",
    decimals: 2,
    dependsOnScale: true,
  },
  education: {
    label: "Accessibilité — Éducation",
    valueProperty: "rel_education",
    mode: "relative",
    decimals: 2,
    dependsOnScale: true,
  },
  services: {
    label: "Accessibilité — Services",
    valueProperty: "rel_services",
    mode: "relative",
    decimals: 2,
    dependsOnScale: true,
  },
  loisirs: {
    label: "Accessibilité — Loisirs",
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
  },
  population: {
    label: "Population",
    valueProperty: "population",
    mode: "value",
    decimals: 0,
    dependsOnScale: false,
    unit: "hab.",
  },
}

const activeIndicator = computed(() => {
  return indicatorConfigs[props.indicator] ?? defaultIndicator
})

const chartTitle = computed(() => {
  return activeIndicator.value.mode === "relative"
    ? "Distribution de l’indice relatif"
    : "Distribution des valeurs observées"
})

const axisLabel = computed(() => {
  if (activeIndicator.value.mode === "relative") {
    return "Indice relatif à la moyenne communale"
  }

  return props.indicator === "revenu"
    ? "Niveau de vie annuel par unité de consommation"
    : "Population par carreau"
})

const readingText = computed(() => {
  if (activeIndicator.value.mode === "relative") {
    return (
      `La ligne verticale marque la moyenne de ${props.cityName}. `
      + "Les barres situées à gauche correspondent aux valeurs inférieures "
      + "à la moyenne, celles de droite aux valeurs supérieures."
    )
  }

  return (
    "Chaque barre regroupe une plage de valeurs observées. "
    + "L’axe conserve l’unité d’origine ; ses bornes correspondent aux 1er "
    + "et 99e percentiles pour limiter l’effet visuel des valeurs extrêmes."
  )
})

const maximumCount = computed(() => {
  return Math.max(...bars.value.map((bar) => bar.count), 1)
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

function formatNumber(value: number) {
  return value.toLocaleString("fr-FR", {
    maximumFractionDigits: 2,
  })
}

function formatIndicatorValue(value: number, config: IndicatorConfig) {
  const formatted = value.toLocaleString("fr-FR", {
    maximumFractionDigits: config.decimals,
  })

  return config.unit ? `${formatted} ${config.unit}` : formatted
}

function formatAxisValue(value: number) {
  return formatIndicatorValue(value, activeIndicator.value)
}

function barHeight(count: number) {
  return Math.max((count / maximumCount.value) * 88, 1)
}

function mixColor(first: number[], second: number[], ratio: number) {
  const clampedRatio = Math.min(Math.max(ratio, 0), 1)
  const channels = first.map((value, index) => {
    return Math.round(
      value + (second[index] - value) * clampedRatio,
    )
  })

  return `rgb(${channels.join(", ")})`
}

function valueBarColor(
  ratio: number,
  colors: [number[], number[], number[]],
) {
  if (ratio <= 0.5) {
    return mixColor(
      colors[0],
      colors[1],
      ratio * 2,
    )
  }

  return mixColor(
    colors[1],
    colors[2],
    (ratio - 0.5) * 2,
  )
}

function relativeBarColor(value: number, minimum: number, maximum: number) {
  if (value < 1) {
    const denominator = Math.max(1 - minimum, 0.001)
    const intensity = (1 - value) / denominator
    return mixColor([253, 219, 199], [178, 24, 43], intensity)
  }

  const denominator = Math.max(maximum - 1, 0.001)
  const intensity = (value - 1) / denominator
  return mixColor([217, 240, 211], [26, 152, 80], intensity)
}

function buildRelativeBars(config: IndicatorConfig) {
  if (!currentData) {
    return
  }

  const values = currentData.features
    .map((feature) => feature.properties?.[config.valueProperty])
    .filter((value) => value !== null && value !== undefined && value !== "")
    .map((value) => Number(value))
    .filter((value) => Number.isFinite(value))
    .sort((first, second) => first - second)

  validCount.value = values.length

  if (values.length === 0) {
    bars.value = []
    return
  }

  let minimum = Math.min(quantile(values, 0.01), 1)
  let maximum = Math.max(quantile(values, 0.99), 1)

  if (minimum === maximum) {
    minimum -= 0.1
    maximum += 0.1
  }

  axisMinimum.value = minimum
  axisMaximum.value = maximum
  averagePosition.value = ((1 - minimum) / (maximum - minimum)) * 100

  const numberOfBins = 18
  const width = (maximum - minimum) / numberOfBins
  const counts = Array.from({ length: numberOfBins }, () => 0)

  for (const value of values) {
    const clamped = Math.min(Math.max(value, minimum), maximum)
    const rawIndex = Math.floor((clamped - minimum) / width)
    const index = Math.min(rawIndex, numberOfBins - 1)
    counts[index] += 1
  }

  bars.value = counts.map((count, index) => {
    const start = minimum + index * width
    const end = start + width
    const middle = (start + end) / 2

    return {
      key: `bin-${index}`,
      label: "",
      count,
      color: relativeBarColor(middle, minimum, maximum),
      detail: `${formatNumber(start)} à ${formatNumber(end)}`,
    }
  })
}

function buildValueBars(config: IndicatorConfig) {
  if (!currentData) {
    return
  }

  const values = currentData.features
    .map((feature) => feature.properties?.[config.valueProperty])
    .filter((value) => value !== null && value !== undefined && value !== "")
    .map((value) => Number(value))
    .filter((value) => Number.isFinite(value))
    .sort((first, second) => first - second)

  validCount.value = values.length
  averagePosition.value = null

  if (values.length === 0) {
    bars.value = []
    return
  }

  let minimum = quantile(values, 0.01)
  let maximum = quantile(values, 0.99)

  if (minimum === maximum) {
    const padding = Math.max(Math.abs(minimum) * 0.05, 1)
    minimum -= padding
    maximum += padding
  }

  axisMinimum.value = minimum
  axisMaximum.value = maximum

  const numberOfBins = 18
  const width = (maximum - minimum) / numberOfBins
  const counts = Array.from({ length: numberOfBins }, () => 0)

  for (const value of values) {
    const clamped = Math.min(Math.max(value, minimum), maximum)
    const rawIndex = Math.floor((clamped - minimum) / width)
    const index = Math.min(rawIndex, numberOfBins - 1)
    counts[index] += 1
  }

  const colors: [number[], number[], number[]] =
  props.indicator === "population"
    ? [
        [255, 247, 188],
        [254, 196, 79],
        [215, 48, 31],
      ]
    : [
        [242, 240, 247],
        [158, 154, 200],
        [84, 39, 143],
      ]

  bars.value = counts.map((count, index) => ({
    key: `value-bin-${index}`,
    label: "",
    count,
    color: valueBarColor(
      index / (numberOfBins - 1),
      colors,
    ),
    detail: `${formatIndicatorValue(
      minimum + index * width,
      config,
    )} à ${formatIndicatorValue(
      minimum + (index + 1) * width,
      config,
    )}`,
  }))
}

function rebuildChart() {
  hoveredBar.value = null
  const config = activeIndicator.value

  if (config.mode === "relative") {
    buildRelativeBars(config)
  } else {
    buildValueBars(config)
  }
}

async function loadData() {
  if (!props.dataUrl) {
    return
  }

  const activeRequest = ++requestNumber
  loading.value = true
  errorMessage.value = ""

  try {
    const separator = props.dataUrl.includes("?") ? "&" : "?"
    const response = await fetch(
      `${props.dataUrl}${separator}v=${Date.now()}`,
    )

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const data = (await response.json()) as ChartFeatureCollection

    if (activeRequest !== requestNumber) {
      return
    }

    if (!Array.isArray(data.features) || data.features.length === 0) {
      throw new Error("Le GeoJSON ne contient aucun carreau.")
    }

    currentData = data
    rebuildChart()
  } catch (error) {
    if (activeRequest !== requestNumber) {
      return
    }

    console.error("Erreur de chargement du graphique :", error)
    errorMessage.value = activeIndicator.value.dependsOnScale
      ? `Impossible de charger ${props.cityName} pour λ = ${props.bw} m.`
      : `Impossible de charger les données de ${props.cityName}.`
  } finally {
    if (activeRequest === requestNumber) {
      loading.value = false
    }
  }
}

onMounted(() => {
  loadData()
})

watch(
  () => props.dataUrl,
  () => {
    loadData()
  },
)

watch(
  () => props.indicator,
  () => {
    rebuildChart()
  },
)

onBeforeUnmount(() => {
  requestNumber += 1
  currentData = null
})
</script>

<style scoped>
.chart-shell {
  padding: 2px 0 0;
}

.chart-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 26px;
}

.chart-kicker {
  color: #197278;
  font-size: 13px;
  font-weight: 700;
}

.chart-meta h3 {
  margin: 5px 0 0;
  font-size: 20px;
}

.parameter-chip {
  padding: 8px 11px;
  color: #425262;
  background: #f1f5f7;
  border: 1px solid #dce3e9;
  border-radius: 999px;
  font-size: 13px;
}

.chart-status {
  display: grid;
  min-height: 370px;
  color: #627181;
  place-items: center;
}

.chart-status.error {
  color: #8c2430;
}

.histogram {
  position: relative;
  height: 350px;
  padding: 34px 14px 0;
  background:
    repeating-linear-gradient(
      to top,
      #ffffff 0,
      #ffffff 69px,
      #e8edf1 70px
    );
  border-bottom: 1px solid #aeb9c3;
}

.bars {
  display: flex;
  align-items: flex-end;
  gap: 5px;
  height: 100%;
}

.bar-column {
  position: relative;
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
  min-width: 0;
  padding: 0;
  background: transparent;
  border: 0;
  cursor: pointer;
  flex-direction: column;
}

.bar-column:hover .bar,
.bar-column:focus-visible .bar {
  filter: brightness(0.88);
  outline: 2px solid #17324d;
  outline-offset: 1px;
}

.bar {
  display: block;
  width: 100%;
  min-height: 2px;
  border-radius: 3px 3px 0 0;
  transition: filter 120ms ease;
}

.bar-count {
  margin-bottom: 4px;
  color: #566675;
  font-size: 10px;
  opacity: 0;
}

.bar-column:hover .bar-count,
.bar-column:focus-visible .bar-count {
  opacity: 1;
}

.bar-label {
  position: absolute;
  bottom: -25px;
  color: #526170;
  font-size: 12px;
  font-weight: 700;
}

.average-line {
  position: absolute;
  top: 18px;
  bottom: 0;
  z-index: 2;
  width: 2px;
  background: #17202a;
  pointer-events: none;
}

.average-line span {
  position: absolute;
  top: -16px;
  left: 6px;
  width: max-content;
  padding: 2px 5px;
  color: white;
  background: #17202a;
  border-radius: 3px;
  font-size: 10px;
}

.axis-values {
  display: grid;
  grid-template-columns: 80px 1fr 80px;
  gap: 12px;
  margin-top: 8px;
  color: #63717e;
  font-size: 12px;
  text-align: center;
}

.axis-values span:first-child {
  text-align: left;
}

.axis-values span:last-child {
  text-align: right;
}

.chart-detail {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  margin-top: 34px;
  padding: 13px 15px;
  background: #f6f9fa;
  border: 1px solid #dce3e9;
  border-radius: 8px;
}

.chart-detail span {
  color: #627181;
}

.chart-reading {
  max-width: 900px;
  margin: 18px 0 0;
  color: #526170;
  font-size: 14px;
  line-height: 1.6;
}

@media (max-width: 700px) {
  .chart-meta,
  .chart-detail {
    align-items: flex-start;
    flex-direction: column;
  }

  .histogram {
    height: 300px;
    padding-right: 6px;
    padding-left: 6px;
  }

  .bars {
    gap: 2px;
  }
}
</style>
