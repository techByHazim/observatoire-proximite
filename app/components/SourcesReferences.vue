<script setup lang="ts">
import { useI18n } from "#imports"

const { t } = useI18n({
  useScope: "local",
  inheritLocale: true,
})

const sources = [
  {
    id: "filosofi",
    name: "Insee : Filosofi 2021",
    url: "https://www.insee.fr/fr/statistiques/8735162?sommaire=8735243",
  },
  {
    id: "bpe",
    name: "Insee : Base permanente des équipements 2024",
    url: "https://www.insee.fr/fr/metadonnees/source/operation/s2216/presentation",
  },
  {
    id: "osm",
    name: "OpenStreetMap",
    url: "https://www.openstreetmap.org/copyright",
  },
  {
    id: "boundaries",
    name: "API Découpage administratif",
    url: "https://geo.api.gouv.fr/decoupage-administratif/communes",
  },
]

const references = [
  {
    id: "hansen",
    authors: "Hansen, W. G. (1959)",
    title: "How Accessibility Shapes Land Use",
    journal:
      "Journal of the American Institute of Planners, 25(2), 73–76.",
    url: "https://doi.org/10.1080/01944365908978307",
  },
  {
    id: "geurs",
    authors: "Geurs, K. T., & van Wee, B. (2004)",
    title:
      "Accessibility evaluation of land-use and transport strategies: Review and research directions",
    journal: "Journal of Transport Geography, 12(2), 127–140.",
    url: "https://doi.org/10.1016/j.jtrangeo.2003.10.005",
  },
  {
    id: "moreno",
    authors:
      "Moreno, C., Allam, Z., Chabaud, D., Gall, C., & Pratlong, F. (2021)",
    title:
      "Introducing the “15-Minute City”: Sustainability, Resilience and Place Identity in Future Post-Pandemic Cities",
    journal: "Smart Cities, 4(1), 93–111.",
    url: "https://doi.org/10.3390/smartcities4010006",
  },
  {
    id: "pca",
    authors: "Jolliffe, I. T., & Cadima, J. (2016)",
    title: "Principal component analysis: a review and recent developments",
    journal:
      "Philosophical Transactions of the Royal Society A, 374(2065), 20150202.",
    url: "https://doi.org/10.1098/rsta.2015.0202",
  },
]
</script>

<template>
  <section class="research-documentation">
    <h3>{{ t("title") }}</h3>

    <p class="documentation-intro">
      {{ t("intro") }}
    </p>

    <section class="documentation-block">
      <h4>{{ t("dataTitle") }}</h4>

      <ul class="data-sources">
        <li
          v-for="source in sources"
          :key="source.id"
          class="data-source"
        >
          <a
            :href="source.url"
            target="_blank"
            rel="noopener noreferrer"
          >
            {{ source.name }}
            <span aria-hidden="true">↗</span>
          </a>

          <p>{{ t(`sourceUses.${source.id}`) }}</p>
        </li>
      </ul>
    </section>

    <section class="documentation-block">
      <h4>{{ t("referencesTitle") }}</h4>

      <ol class="reference-list">
        <li
          v-for="reference in references"
          :id="`reference-${reference.id}`"
          :key="reference.id"
          class="reference-entry"
        >
          <p class="reference-authors">
            {{ reference.authors }}
          </p>

          <a
            :href="reference.url"
            target="_blank"
            rel="noopener noreferrer"
          >
            <cite>{{ reference.title }}</cite>
            <span aria-hidden="true"> ↗</span>
          </a>

          <p class="reference-journal">
            {{ reference.journal }}
          </p>

          <p class="reference-purpose">
            {{ t(`referenceUses.${reference.id}`) }}
          </p>
        </li>
      </ol>
    </section>

    <aside class="thesis-note">
      <h4>{{ t("thesisTitle") }}</h4>
      <p>{{ t("thesisDescription") }}</p>
    </aside>
  </section>
</template>

<i18n lang="json">
{
  "fr": {
    "title": "Sources et références scientifiques",
    "intro": "Les données mobilisées, les fondements scientifiques et les choix méthodologiques de l’observatoire.",
    "dataTitle": "Données utilisées",
    "referencesTitle": "Références scientifiques",
    "sourceUses": {
      "filosofi": "Données carroyées à 200 mètres : population couverte par Filosofi, ménages et niveaux de vie.",
      "bpe": "Localisation et classification des équipements, regroupés selon les fonctions sociales étudiées.",
      "osm": "Équipements complémentaires et réseau utilisé pour calculer les distances piétonnes. Données produites par les contributeurs d’OpenStreetMap.",
      "boundaries": "Contours des communes utilisés pour délimiter les territoires sur les cartes."
    },
    "referenceUses": {
      "hansen": "Cadre fondateur de l’accessibilité potentielle : les possibilités accessibles sont pondérées en fonction de leur éloignement.",
      "geurs": "Synthèse des différentes approches de mesure de l’accessibilité, de leurs composantes et de leurs limites.",
      "moreno": "Cadre conceptuel de la proximité et des fonctions urbaines du quotidien. Les auteurs distinguent six fonctions ; le regroupement en cinq fonctions de cet observatoire constitue une adaptation au périmètre de l’étude.",
      "pca": "Référence méthodologique pour l’analyse en composantes principales et l’interprétation de la variance expliquée. Son application aux cinq fonctions d’accessibilité est mise en œuvre dans cette étude."
    },
    "thesisTitle": "Calculs et choix méthodologiques de la thèse",
    "thesisDescription": "La préparation des données, le regroupement des équipements, le calcul des accessibilités à différentes distances caractéristiques et les analyses présentées sont réalisés dans le cadre des travaux de thèse. Les paramètres et les transformations appliquées aux indicateurs sont précisés dans la méthode.",
    "thresholdNote": "Le seuil de 85 % de variance expliquée sert ici de critère pour repérer une structure commune aux fonctions étudiées. Il s’agit d’un choix de l’étude, et non d’une règle générale de l’ACP."
  },
  "en": {
    "title": "Data sources and scientific references",
    "intro": "The datasets, scientific foundations and methodological choices behind the observatory.",
    "dataTitle": "Data sources",
    "referencesTitle": "Scientific references",
    "sourceUses": {
      "filosofi": "Data on a 200-metre grid: population covered by Filosofi, households and living standards.",
      "bpe": "Facility locations and classifications, grouped according to the social functions examined in this study.",
      "osm": "Additional facilities and the network used to calculate walking distances. Data produced by OpenStreetMap contributors.",
      "boundaries": "Municipal boundaries used to delineate the study areas on the maps."
    },
    "referenceUses": {
      "hansen": "A foundational framework for potential accessibility: accessible opportunities are weighted according to their distance.",
      "geurs": "A review of accessibility measurement approaches, their components and their limitations.",
      "moreno": "A conceptual framework for proximity and everyday urban functions. The authors distinguish six functions; the five-function grouping used in this observatory is an adaptation to the scope of this study.",
      "pca": "A methodological reference for principal component analysis and the interpretation of explained variance. Its application to the five accessibility functions is implemented in this study."
    },
    "thesisTitle": "Calculations and methodological choices",
    "thesisDescription": "Data preparation, facility grouping, accessibility calculations at different characteristic distances and the analyses presented here are carried out as part of the doctoral research. Parameters and indicator transformations are described in the methodology.",
    "thresholdNote": "The threshold of 85% explained variance is used here to identify a structure shared by the functions studied. It is a study-specific choice rather than a general rule of PCA."
  }
}
</i18n>

<style scoped>
.research-documentation {
  margin-top: 28px;
  padding-top: 24px;
  border-top: 1px solid var(--line);
  color: var(--ink);
  line-height: 1.65;
}

.research-documentation h3 {
  margin: 0;
  font-size: 20px;
}

.research-documentation h4 {
  margin: 0 0 14px;
  color: var(--ink);
  font-size: 16px;
}

.documentation-intro {
  margin: 8px 0 0;
  color: var(--muted);
}

.documentation-block {
  margin-top: 26px;
}

.data-sources {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.data-source {
  padding: 18px;
  background: var(--background);
  border: 1px solid var(--line);
  border-radius: 10px;
}

.data-source a {
  font-weight: 700;
}

.data-source p {
  margin: 8px 0 0;
  color: var(--muted);
  font-size: 14px;
}

.research-documentation a {
  color: var(--ink);
  text-decoration: underline;
  text-decoration-color: var(--teal);
  text-underline-offset: 4px;
  overflow-wrap: anywhere;
}

.research-documentation a:hover {
  text-decoration-thickness: 2px;
}

.research-documentation a:focus-visible {
  outline: 2px solid var(--teal);
  outline-offset: 4px;
  border-radius: 2px;
}

.reference-list {
  margin: 0;
  padding-left: 24px;
}

.reference-entry {
  padding: 0 0 18px 6px;
  scroll-margin-top: 24px;
}

.reference-entry + .reference-entry {
  padding-top: 18px;
  border-top: 1px solid var(--line);
}

.reference-authors {
  margin: 0 0 4px;
  color: var(--ink);
  font-weight: 700;
}

.reference-journal {
  margin: 4px 0 0;
  color: var(--muted);
  font-size: 14px;
}

.reference-purpose {
  margin: 10px 0 0;
  color: var(--ink);
  font-size: 14px;
}

.thesis-note {
  margin-top: 20px;
  padding: 18px 20px;
  background: var(--background);
  border: 1px solid var(--line);
  border-left: 4px solid var(--teal);
  border-radius: 8px;
}

.thesis-note p {
  margin: 8px 0 0;
  color: var(--ink);
  font-size: 14px;
}

@media (max-width: 700px) {
  .data-sources {
    grid-template-columns: 1fr;
  }
}
</style>