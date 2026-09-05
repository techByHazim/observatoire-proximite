<template>
  <section class="indicator-chart">
    <header class="chart-header">
      <div>
        <span class="chart-kicker">Indicateurs urbains</span>
        <h3>{{ metricConfig.title }}</h3>
        <p>{{ metricConfig.subtitle }}</p>
      </div>

      <div class="scale-summary">
        <span>Échelle comparée</span>
        <strong>λ = {{ bw }} m</strong>
      </div>
    </header>

    <div v-if="rows.length === 0" class="empty-state">
      Aucune statistique n’est disponible à cette échelle. Relance l’exporteur
      pour régénérer <code>cities.json</code>.
    </div>

    <template v-else>
      <div class="coefficient-axis" aria-hidden="true">
        <span>−1</span>
        <span>0</span>
        <span>+1</span>
      </div>

      <div class="ranking" role="list" :aria-label="metricConfig.title">
        <button
          v-for="(row, index) in rows"
          :key="row.slug"
          type="button"
          class="ranking-row"
          :class="{
            selected: row.slug === selectedCitySlug,
            active: activeRow?.slug === row.slug,
          }"
          :aria-label="rowDescription(row, index)"
          @mouseenter="hoveredRow = row"
          @mouseleave="hoveredRow = null"
          @focus="hoveredRow = row"
          @blur="hoveredRow = null"
          @click="toggleRow(row)"
        >
          <span class="rank">{{ index + 1 }}</span>
          <span class="city-name">{{ row.name }}</span>

          <span class="bar-area">
            <span class="zero-line"></span>
            <span
              class="coefficient-bar"
              :class="row.value >= 0 ? 'positive' : 'negative'"
              :style="barStyle(row.value)"
            ></span>
          </span>

          <strong class="coefficient">
            {{ formatCoefficient(row.value) }}
          </strong>
        </button>
      </div>

      <div v-if="activeRow" class="chart-detail" aria-live="polite">
        <strong>{{ activeRow.name }}</strong>
        <span>
          {{ metricConfig.symbol }} =
          {{ formatCoefficient(activeRow.value) }} ·
          {{ activeRow.sampleSize.toLocaleString("fr-FR") }} carreaux valides
        </span>
      </div>

      <p class="chart-reading">
        {{ metricConfig.reading }}
      </p>
    </template>
  </section>
</template>

<script setup lang="ts">
type UrbanIndicator = "population" | "income" | "income_gap"

interface ScaleAnalysis {
  pc1_population_r: number | null
  population_correlation_n: number
  pc1_income_spearman: number | null
  income_correlation_n: number
  pc1_income_gap: number | null
  pc1_income_gap_n: number
  pc1_income_q1_median: number | null
  pc1_income_q5_median: number | null
}

interface ScaleEntry {
  bw: number
  analysis?: ScaleAnalysis
}

interface CityEntry {
  name: string
  slug: string
  scales: ScaleEntry[]
}

interface RankingRow {
  name: string
  slug: string
  value: number
  sampleSize: number
}

interface MetricConfig {
  title: string
  subtitle: string
  symbol: string
  reading: string
  valueProperty: keyof ScaleAnalysis
  sampleProperty: keyof ScaleAnalysis
}

const props = defineProps<{
  cities: CityEntry[]
  bw: number
  metric: UrbanIndicator
  selectedCitySlug: string
}>()

const hoveredRow = ref<RankingRow | null>(null)
const pinnedRow = ref<RankingRow | null>(null)

const metricConfigs: Record<UrbanIndicator, MetricConfig> = {
  population: {
    title: "Adéquation entre accessibilité et population",
    subtitle: (
      "Corrélation de Pearson entre PC1 et population, calculée sur les "
      + "carreaux de chaque ville."
    ),
    symbol: "r",
    reading: (
      "Une valeur positive indique que les secteurs les plus peuplés tendent "
      + "à être les plus accessibles. Cet indicateur mesure une association "
      + "spatiale, pas à lui seul l’égalité d’accès."
    ),
    valueProperty: "pc1_population_r",
    sampleProperty: "population_correlation_n",
  },
  income: {
    title: "Gradient socio-spatial d’accessibilité",
    subtitle: (
      "Corrélation de Spearman entre PC1 et niveau de vie, calculée sur les "
      + "carreaux de chaque ville."
    ),
    symbol: "ρ",
    reading: (
      "Une valeur positive indique une accessibilité généralement plus élevée "
      + "dans les secteurs aux revenus élevés ; une valeur négative indique "
      + "la relation inverse. Une valeur proche de zéro ne prouve pas l’égalité."
    ),
    valueProperty: "pc1_income_spearman",
    sampleProperty: "income_correlation_n",
  },
  income_gap: {
  title: "Écart d’accessibilité entre Q5 et Q1",
  subtitle: (
    "Écart entre les médianes de PC1 des quintiles locaux "
    + "Q5 et Q1, rapporté à l’écart interquartile de PC1."
  ),
  symbol: "G",
  reading: (
    "Une valeur proche de zéro indique des médianes similaires. "
    + "Une valeur positive indique un avantage pour Q5 et une "
    + "valeur négative un avantage pour Q1."
 ),
  valueProperty: "pc1_income_gap",
  sampleProperty: "pc1_income_gap_n",
},
}

const metricConfig = computed(() => metricConfigs[props.metric])

const rows = computed<RankingRow[]>(() => {
  const config = metricConfig.value

  return props.cities
    .map((city) => {
      const scale = city.scales.find(
        (candidate) =>
          Number(candidate.bw) === Number(props.bw),
      )

      const rawValue =
        scale?.analysis?.[config.valueProperty]

      const rawSampleSize =
        scale?.analysis?.[config.sampleProperty]

      const value =
        rawValue === null || rawValue === undefined
          ? Number.NaN
          : Number(rawValue)

      const sampleSize = Number(rawSampleSize)

      return {
        name: city.name,
        slug: city.slug,
        value,
        sampleSize: Number.isFinite(sampleSize)
          ? sampleSize
          : 0,
      }
    })
    .filter((row) => {
      if (!Number.isFinite(row.value)) {
        return false
      }

      // L’écart Q5–Q1 n’est pas limité entre −1 et 1.
      if (props.metric === "income_gap") {
        return true
      }

      // Pearson et Spearman sont compris entre −1 et 1.
      return row.value >= -1 && row.value <= 1
    })
    .sort((first, second) => {
      if (props.metric === "income_gap") {
        // Pour l’équité, la valeur la plus proche de zéro
        // apparaît en premier.
        return (
          Math.abs(first.value)
          - Math.abs(second.value)
        )
      }

      // Classement décroissant pour Pearson et Spearman.
      return second.value - first.value
    })
})
const selectedRow = computed(() => {
  return (
    rows.value.find((row) => row.slug === props.selectedCitySlug)
    ?? rows.value[0]
    ?? null
  )
})

const activeRow = computed(() => {
  return hoveredRow.value ?? pinnedRow.value ?? selectedRow.value
})

watch(
  () => [props.metric, props.bw],
  () => {
    hoveredRow.value = null
    pinnedRow.value = null
  },
)

function barStyle(value: number) {
  const width = Math.abs(value) * 50
  const left = value >= 0 ? 50 : 50 - width

  return {
    left: `${left}%`,
    width: `${width}%`,
  }
}

function formatCoefficient(value: number) {
  return value.toLocaleString("fr-FR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function rowDescription(row: RankingRow, index: number) {
  return (
    `${index + 1}. ${row.name}, ${metricConfig.value.symbol} `
    + `${formatCoefficient(row.value)}, ${row.sampleSize} carreaux valides.`
  )
}

function toggleRow(row: RankingRow) {
  pinnedRow.value = pinnedRow.value?.slug === row.slug
    ? null
    : row
}
</script>

<style scoped>
.indicator-chart {
  min-width: 0;
}

.chart-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 22px;
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
  max-width: 760px;
  margin: 0;
  color: #627181;
  line-height: 1.5;
}

.scale-summary {
  display: grid;
  min-width: 145px;
  padding: 10px 12px;
  color: #425262;
  text-align: right;
  background: #f1f5f7;
  border: 1px solid #dce3e9;
  border-radius: 8px;
}

.scale-summary span {
  font-size: 12px;
}

.scale-summary strong {
  color: #17202a;
}

.coefficient-axis {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  margin: 0 70px 5px 190px;
  color: #63717e;
  font-size: 12px;
}

.coefficient-axis span:nth-child(2) {
  text-align: center;
}

.coefficient-axis span:last-child {
  text-align: right;
}

.ranking {
  display: grid;
  gap: 5px;
}

.ranking-row {
  display: grid;
  grid-template-columns: 28px 145px minmax(180px, 1fr) 58px;
  align-items: center;
  gap: 9px;
  width: 100%;
  min-height: 38px;
  padding: 5px 8px;
  color: #344454;
  text-align: left;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 6px;
  cursor: pointer;
}

.ranking-row:hover,
.ranking-row.active {
  background: #f3f7f8;
  border-color: #dce3e9;
}

.ranking-row.selected .city-name {
  color: #0f6268;
  font-weight: 700;
}

.rank {
  color: #7a8793;
  font-size: 12px;
  text-align: right;
}

.city-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bar-area {
  position: relative;
  display: block;
  height: 20px;
  background: linear-gradient(
    to right,
    rgb(178 24 43 / 7%) 0%,
    rgb(255 255 255 / 0%) 50%,
    rgb(26 152 80 / 7%) 100%
  );
}

.zero-line {
  position: absolute;
  top: -3px;
  bottom: -3px;
  left: 50%;
  width: 1px;
  background: #7e8b96;
}

.coefficient-bar {
  position: absolute;
  top: 3px;
  height: 14px;
  min-width: 2px;
  border-radius: 2px;
}

.coefficient-bar.positive {
  background: #26945d;
}

.coefficient-bar.negative {
  background: #b83248;
}

.coefficient {
  color: #17202a;
  text-align: right;
}

.chart-detail {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  margin-top: 18px;
  padding: 13px 15px;
  color: #425262;
  background: #f6f9fa;
  border: 1px solid #dce3e9;
  border-radius: 8px;
}

.chart-detail span {
  color: #627181;
}

.chart-reading {
  margin: 14px 0 0;
  color: #526170;
  font-size: 14px;
  line-height: 1.6;
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
  .chart-header,
  .chart-detail {
    align-items: flex-start;
    flex-direction: column;
  }

  .scale-summary {
    text-align: left;
  }

  .coefficient-axis {
    margin-right: 56px;
    margin-left: 108px;
  }

  .ranking-row {
    grid-template-columns: 22px 76px minmax(100px, 1fr) 48px;
    gap: 6px;
    padding-right: 2px;
    padding-left: 2px;
  }
}
</style>
