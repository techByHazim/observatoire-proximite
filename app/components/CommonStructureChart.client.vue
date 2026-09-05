<template>
  <section class="structure-chart">
    <header class="chart-header">
      <div>
        <span class="chart-kicker">Structure commune</span>
        <h3>Émergence d’une accessibilité unidimensionnelle</h3>
        <p>
          Part de la variance des cinq fonctions expliquée par la PC1 à
          {{ cityName }}.
        </p>
      </div>

      <div class="threshold-summary">
        <span>Seuil retenu</span>
        <strong>{{ formatPercent(threshold) }}</strong>
      </div>
    </header>

    <div v-if="points.length === 0" class="empty-state">
      Les statistiques PCA sont absentes. Relance l’exporteur pour régénérer
      <code>cities.json</code>.
    </div>

    <template v-else>
      <div class="plot-wrapper">
        <svg
          class="plot"
          viewBox="0 0 920 430"
          role="img"
          :aria-label="chartDescription"
          @mouseleave="hoveredPoint = null"
        >
          <title>{{ chartDescription }}</title>

          <g class="grid">
            <g v-for="tick in yTicks" :key="`y-${tick}`">
              <line
                :x1="margins.left"
                :x2="margins.right"
                :y1="yPosition(tick)"
                :y2="yPosition(tick)"
              />
              <text
                :x="margins.left - 12"
                :y="yPosition(tick) + 4"
                text-anchor="end"
              >
                {{ formatPercent(tick) }}
              </text>
            </g>
          </g>

          <line
            class="threshold-line"
            :x1="margins.left"
            :x2="margins.right"
            :y1="yPosition(threshold)"
            :y2="yPosition(threshold)"
          />
          <text
            class="threshold-label"
            :x="margins.right - 4"
            :y="yPosition(threshold) - 9"
            text-anchor="end"
          >
            Seuil {{ formatPercent(threshold) }}
          </text>

          <line
            class="axis"
            :x1="margins.left"
            :x2="margins.left"
            :y1="margins.top"
            :y2="margins.bottom"
          />
          <line
            class="axis"
            :x1="margins.left"
            :x2="margins.right"
            :y1="margins.bottom"
            :y2="margins.bottom"
          />

          <g v-for="tick in xTicks" :key="`x-${tick}`">
            <line
              class="tick-mark"
              :x1="xPosition(tick)"
              :x2="xPosition(tick)"
              :y1="margins.bottom"
              :y2="margins.bottom + 7"
            />
            <text
              :x="xPosition(tick)"
              :y="margins.bottom + 25"
              text-anchor="middle"
            >
              {{ tick }}
            </text>
          </g>

          <text
            class="axis-title"
            x="500"
            y="418"
            text-anchor="middle"
          >
            Distance caractéristique λ (m)
          </text>

          <text
            class="axis-title"
            x="18"
            y="200"
            text-anchor="middle"
            transform="rotate(-90 18 200)"
          >
            Variance expliquée par PC1
          </text>

          <path class="series-line" :d="linePath" />

          <g
            v-for="point in points"
            :key="point.bw"
            class="point-group"
          >
            <circle
              class="point-hit"
              :cx="xPosition(point.bw)"
              :cy="yPosition(point.evr)"
              r="16"
              tabindex="0"
              :aria-label="pointDescription(point)"
              @mouseenter="hoveredPoint = point"
              @focus="hoveredPoint = point"
              @blur="hoveredPoint = null"
              @click="togglePoint(point)"
            />
            <circle
              class="point"
              :class="{
                reached: point.evr >= threshold,
                active: hoveredPoint?.bw === point.bw,
              }"
              :cx="xPosition(point.bw)"
              :cy="yPosition(point.evr)"
              :r="hoveredPoint?.bw === point.bw ? 7 : 5"
            />
          </g>
        </svg>

        <div
          v-if="hoveredPoint"
          class="chart-tooltip"
          :style="tooltipStyle"
          role="status"
        >
          <strong>λ = {{ hoveredPoint.bw }} m</strong>
          <span>PC1 : {{ formatPercent(hoveredPoint.evr) }}</span>
          <span>Cutoff : {{ hoveredPoint.cutoff }} m</span>
        </div>
      </div>

      <p class="chart-reading">
        <template v-if="emergencePoint">
          Le seuil est atteint pour la première fois à
          <strong>λ = {{ emergencePoint.bw }} m</strong>
          ({{ formatPercent(emergencePoint.evr) }} de variance expliquée).
        </template>
        <template v-else>
          Le seuil de {{ formatPercent(threshold) }} n’est atteint à aucune
          distance testée pour {{ cityName }}.
        </template>
      </p>
    </template>
  </section>
</template>

<script setup lang="ts">
interface ScaleAnalysis {
  pc1_evr: number | null
}

interface ScaleEntry {
  bw: number
  cutoff: number
  analysis?: ScaleAnalysis
}

interface ChartPoint {
  bw: number
  cutoff: number
  evr: number
}

const props = defineProps<{
  cityName: string
  scales: ScaleEntry[]
  threshold: number
}>()

const margins = {
  left: 78,
  right: 890,
  top: 30,
  bottom: 365,
}

const hoveredPoint = ref<ChartPoint | null>(null)

const points = computed<ChartPoint[]>(() => {
  return props.scales
    .map((scale) => {
      const rawEvr = scale.analysis?.pc1_evr

      return {
        bw: Number(scale.bw),
        cutoff: Number(scale.cutoff),
        evr: rawEvr === null || rawEvr === undefined
          ? Number.NaN
          : Number(rawEvr),
      }
    })
    .filter(
      (point) =>
        Number.isFinite(point.bw)
        && Number.isFinite(point.evr)
        && point.evr >= 0
        && point.evr <= 1,
    )
    .sort((first, second) => first.bw - second.bw)
})

const xMinimum = computed(() => points.value[0]?.bw ?? 0)
const xMaximum = computed(() => {
  return points.value[points.value.length - 1]?.bw ?? 1
})

const yMinimum = computed(() => {
  if (points.value.length === 0) {
    return 0
  }

  const minimum = Math.min(
    props.threshold,
    ...points.value.map((point) => point.evr),
  )

  return Math.max(0, Math.floor((minimum - 0.05) * 10) / 10)
})

const yMaximum = computed(() => 1)

const yTicks = computed(() => {
  const count = 5
  const interval = (yMaximum.value - yMinimum.value) / count

  return Array.from(
    { length: count + 1 },
    (_, index) => yMinimum.value + interval * index,
  )
})

const xTicks = computed(() => {
  if (points.value.length <= 5) {
    return points.value.map((point) => point.bw)
  }

  const lastIndex = points.value.length - 1
  const indices = [
    0,
    Math.round(lastIndex * 0.25),
    Math.round(lastIndex * 0.5),
    Math.round(lastIndex * 0.75),
    lastIndex,
  ]

  return [...new Set(indices.map((index) => points.value[index].bw))]
})

const linePath = computed(() => {
  return points.value
    .map((point, index) => {
      const command = index === 0 ? "M" : "L"
      return `${command} ${xPosition(point.bw)} ${yPosition(point.evr)}`
    })
    .join(" ")
})

const emergencePoint = computed(() => {
  return points.value.find((point) => point.evr >= props.threshold) ?? null
})

const chartDescription = computed(() => {
  return (
    `Évolution de la variance expliquée par la première composante `
    + `principale à ${props.cityName}, selon la distance caractéristique.`
  )
})

const tooltipStyle = computed(() => {
  if (!hoveredPoint.value) {
    return {}
  }

  return {
    left: `${(xPosition(hoveredPoint.value.bw) / 920) * 100}%`,
    top: `${(yPosition(hoveredPoint.value.evr) / 430) * 100}%`,
  }
})

function xPosition(value: number) {
  const range = Math.max(xMaximum.value - xMinimum.value, 1)
  return (
    margins.left
    + ((value - xMinimum.value) / range)
      * (margins.right - margins.left)
  )
}

function yPosition(value: number) {
  const range = Math.max(yMaximum.value - yMinimum.value, 0.001)
  return (
    margins.bottom
    - ((value - yMinimum.value) / range)
      * (margins.bottom - margins.top)
  )
}

function formatPercent(value: number) {
  return value.toLocaleString("fr-FR", {
    style: "percent",
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  })
}

function pointDescription(point: ChartPoint) {
  return (
    `Distance ${point.bw} mètres, variance expliquée `
    + `${formatPercent(point.evr)}, cutoff ${point.cutoff} mètres.`
  )
}

function togglePoint(point: ChartPoint) {
  hoveredPoint.value = hoveredPoint.value?.bw === point.bw
    ? null
    : point
}
</script>

<style scoped>
.structure-chart {
  min-width: 0;
}

.chart-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 18px;
}

.chart-kicker {
  color: #197278;
  font-size: 13px;
  font-weight: 700;
}

.chart-header h3 {
  margin: 5px 0 6px;
  font-size: 20px;
}

.chart-header p {
  margin: 0;
  color: #627181;
}

.threshold-summary {
  display: grid;
  min-width: 125px;
  padding: 10px 12px;
  color: #425262;
  text-align: right;
  background: #f1f5f7;
  border: 1px solid #dce3e9;
  border-radius: 8px;
}

.threshold-summary span {
  font-size: 12px;
}

.threshold-summary strong {
  color: #17202a;
  font-size: 20px;
}

.plot-wrapper {
  position: relative;
  width: 100%;
}

.plot {
  display: block;
  width: 100%;
  min-height: 330px;
  overflow: visible;
}

.grid line {
  stroke: #e3e9ee;
  stroke-width: 1;
}

.grid text,
.plot text {
  fill: #526170;
  font-family: Inter, Arial, sans-serif;
  font-size: 12px;
}

.axis,
.tick-mark {
  stroke: #8795a2;
  stroke-width: 1;
}

.axis-title {
  fill: #344454 !important;
  font-weight: 700;
}

.threshold-line {
  stroke: #b45309;
  stroke-width: 2;
  stroke-dasharray: 8 6;
}

.threshold-label {
  fill: #92400e !important;
  font-weight: 700;
}

.series-line {
  fill: none;
  stroke: #197278;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 3;
}

.point-hit {
  fill: transparent;
  cursor: pointer;
}

.point-hit:focus-visible {
  outline: none;
}

.point {
  fill: white;
  stroke: #197278;
  stroke-width: 3;
  pointer-events: none;
}

.point.reached {
  fill: #197278;
}

.point.active {
  fill: #f59e0b;
  stroke: #92400e;
}

.chart-tooltip {
  position: absolute;
  z-index: 3;
  display: grid;
  gap: 2px;
  min-width: 145px;
  padding: 9px 11px;
  color: #17202a;
  background: rgb(255 255 255 / 96%);
  border: 1px solid #cbd5df;
  border-radius: 7px;
  box-shadow: 0 3px 12px rgb(0 0 0 / 16%);
  font-size: 12px;
  pointer-events: none;
  transform: translate(-50%, calc(-100% - 12px));
}

.chart-reading {
  margin: 10px 0 0;
  padding: 13px 15px;
  color: #425262;
  background: #f6f9fa;
  border: 1px solid #dce3e9;
  border-radius: 8px;
  line-height: 1.55;
}

.empty-state {
  display: grid;
  min-height: 330px;
  padding: 20px;
  color: #627181;
  text-align: center;
  place-items: center;
}

@media (max-width: 700px) {
  .chart-header {
    flex-direction: column;
  }

  .threshold-summary {
    text-align: left;
  }

  .plot {
    min-height: 260px;
  }
}
</style>
