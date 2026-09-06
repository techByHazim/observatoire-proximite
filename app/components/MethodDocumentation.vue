<script setup lang="ts">
import { useI18n } from "#imports"

const { t, n } = useI18n({
  useScope: "local",
  inheritLocale: true,
})

const socialFunctions = [
  "commerce",
  "health",
  "education",
  "services",
  "leisure",
]

const scoreExamples = [
  { value: 0.5, label: "half", tone: "below" },
  { value: 1, label: "average", tone: "average" },
  { value: 2, label: "double", tone: "above" },
]

const calculations = [
  {
    id: "access",
    references: [
      { id: "hansen", label: "Hansen, 1959" },
      { id: "geurs", label: "Geurs & van Wee, 2004" },
    ],
  },
  {
    id: "scale",
    references: [],
  },
  {
    id: "normalization",
    references: [],
  },
  {
    id: "pca",
    references: [
      { id: "pca", label: "Jolliffe & Cadima, 2016" },
    ],
  },
]

const urbanIndicators = [
  "population",
  "income",
  "gap",
]
</script>

<template>
  <div class="method-documentation">
    <header class="method-heading">
      <span class="method-eyebrow">
        {{ t("page.label") }}
      </span>

      <h2>{{ t("page.title") }}</h2>

      <p class="method-intro">
        {{ t("page.intro") }}
      </p>

      <ul class="method-facts">
        <li>{{ t("page.cities") }}</li>
        <li>{{ t("page.functions") }}</li>
        <li>{{ t("page.grid") }}</li>
      </ul>
    </header>

    <aside class="network-note">
      <strong>{{ t("network.title") }}</strong>
      <p>{{ t("network.description") }}</p>
    </aside>

    <!-- Lecture des cartes -->
    <section class="method-section">
      <h3>{{ t("maps.title") }}</h3>

      <p>{{ t("maps.description") }}</p>

      <ul class="function-chips">
        <li
          v-for="socialFunction in socialFunctions"
          :key="socialFunction"
        >
          {{ t(`functions.${socialFunction}`) }}
        </li>
      </ul>

      <p class="method-reference">
        {{ t("referenceLabel") }}
        <a href="#reference-moreno">Moreno et al., 2021</a>
      </p>

      <h4>{{ t("maps.relativeTitle") }}</h4>

      <p>{{ t("maps.relativeDescription") }}</p>

      <dl class="score-examples">
        <div
          v-for="example in scoreExamples"
          :key="example.label"
          :class="example.tone"
        >
          <dt>{{ n(example.value) }}</dt>
          <dd>{{ t(`examples.${example.label}`) }}</dd>
        </div>
      </dl>

      <p>{{ t("maps.colors") }}</p>
      <p>{{ t("maps.pca") }}</p>

      <h4>{{ t("maps.observedTitle") }}</h4>

      <p>{{ t("maps.observedDescription") }}</p>

      <p class="method-secondary">
        {{ t("maps.boundary") }}
      </p>
    </section>

    <!-- Calculs -->
    <section class="method-section">
      <h3>{{ t("calculations.title") }}</h3>
      <p>{{ t("calculations.intro") }}</p>

      <details
        v-for="calculation in calculations"
        :key="calculation.id"
        class="method-details"
      >
        <summary>
          {{ t(`calculations.${calculation.id}.title`) }}
        </summary>

        <div class="detail-content">
          <p>
            {{ t(`calculations.${calculation.id}.description`) }}
          </p>

          <p
            v-if="calculation.id === 'access'"
            class="method-formula"
          >
            A<sub>g,f</sub>(λ) =
            ∑<sub>i ∈ f</sub>
            w<sub>i</sub>
            exp(−d<sub>g,i</sub> / λ),
            d<sub>g,i</sub> ≤ 5λ
          </p>

          <p
            v-if="calculation.id === 'normalization'"
            class="method-formula"
          >
            {{ t("calculations.normalization.formula") }}
          </p>

          <p>
            {{ t(`calculations.${calculation.id}.detail`) }}
          </p>

          <p
            v-if="calculation.id === 'scale'"
            class="method-example"
          >
            {{ t("calculations.scale.example") }}
          </p>

          <p
            v-if="calculation.references.length"
            class="method-reference"
          >
            <span>{{ t("referenceLabel") }}</span>

            <a
              v-for="reference in calculation.references"
              :key="reference.id"
              :href="`#reference-${reference.id}`"
            >
              {{ reference.label }}
            </a>
          </p>
        </div>
      </details>
    </section>

    <!-- Graphiques -->
    <section class="method-section">
      <h3>{{ t("charts.title") }}</h3>
      <p>{{ t("charts.intro") }}</p>

      <details class="method-details">
        <summary>
          {{ t("charts.distribution.title") }}
        </summary>

        <div class="detail-content">
          <p>{{ t("charts.distribution.description") }}</p>
          <p>{{ t("charts.distribution.reading") }}</p>
          <p class="method-secondary">
            {{ t("charts.distribution.range") }}
          </p>
        </div>
      </details>

      <details class="method-details">
        <summary>
          {{ t("charts.structure.title") }}
        </summary>

        <div class="detail-content">
          <p>{{ t("charts.structure.description") }}</p>
          <p>{{ t("charts.structure.threshold") }}</p>

          <p class="method-reference">
            {{ t("referenceLabel") }}
            <a href="#reference-pca">
              Jolliffe &amp; Cadima, 2016
            </a>
          </p>
        </div>
      </details>

      <details class="method-details">
        <summary>
          {{ t("charts.indicators.title") }}
        </summary>

        <div class="detail-content">
          <p>{{ t("charts.indicators.intro") }}</p>

          <dl class="indicator-definitions">
            <div
              v-for="indicator in urbanIndicators"
              :key="indicator"
            >
              <dt>
                {{ t(`indicators.${indicator}.title`) }}
              </dt>

              <dd>
                <p>
                  {{ t(`indicators.${indicator}.description`) }}
                </p>

                <p
                  v-if="indicator === 'gap'"
                  class="method-formula"
                >
                  {{ t("indicators.gap.formula") }}
                </p>

                <p>
                  {{ t(`indicators.${indicator}.reading`) }}
                </p>
              </dd>
            </div>
          </dl>

          <p>{{ t("charts.indicators.ranking") }}</p>

          <p class="method-secondary">
            {{ t("charts.indicators.scope") }}
          </p>
        </div>
      </details>
    </section>
  </div>
</template>

<i18n lang="json">
{
  "fr": {
    "referenceLabel": "Références :",
    "page": {
      "label": "Documentation",
      "title": "Comprendre les cartes et les indicateurs",
      "intro": "Cet observatoire explore l’accessibilité aux équipements du quotidien et ses relations avec la population et les niveaux de vie dans dix villes françaises.",
      "cities": "10 villes",
      "functions": "5 fonctions sociales",
      "grid": "Carreaux de 200 m"
    },
    "network": {
      "title": "Des distances mesurées sur le réseau piéton",
      "description": "Les distances correspondent à la longueur du plus court chemin sur le réseau piéton entre le lieu étudié et les équipements. La distance caractéristique λ et la coupure à 5 × λ se rapportent à ces distances de parcours."
    },
    "functions": {
      "commerce": "Commerce",
      "health": "Santé",
      "education": "Éducation",
      "services": "Services du quotidien",
      "leisure": "Loisirs, culture et sociabilité"
    },
    "maps": {
      "title": "Lire les cartes",
      "description": "Les résultats sont présentés sur le carroyage Insee de 200 mètres. Une seule variable est affichée à la fois. L’accessibilité est étudiée pour cinq fonctions sociales :",
      "relativeTitle": "Les scores d’accessibilité",
      "relativeDescription": "Pour chaque fonction sociale, le score du carreau est rapporté à la moyenne des carreaux étudiés dans la ville, à la distance caractéristique choisie. Les exemples suivants concernent ces scores par fonction :",
      "colors": "Le rouge indique un score inférieur à la moyenne locale ; le vert indique un score supérieur. Les couleurs situent ainsi les carreaux au sein de leur ville.",
      "pca": "L’accessibilité générale utilise un score synthétique, la PC1. Sa représentation est également relative à la moyenne locale, après transformation du score en valeurs positives. Cette transformation est précisée dans la partie consacrée aux calculs.",
      "observedTitle": "Le niveau de vie et la population",
      "observedDescription": "Ces cartes présentent les valeurs dans leurs unités : euros annuels par unité de consommation pour le niveau de vie et personnes par carreau pour la population. Ces deux variables ne dépendent pas de la distance caractéristique λ.",
      "boundary": "Le contour communal sert de repère territorial. L’unité de représentation des résultats reste le carreau de 200 mètres."
    },
    "examples": {
      "half": "Moitié de la moyenne locale",
      "average": "Moyenne locale",
      "double": "Double de la moyenne locale"
    },
    "calculations": {
      "title": "Comprendre les calculs",
      "intro": "Les explications ci-dessous précisent la construction des scores, le rôle des distances et la lecture de la PC1.",
      "access": {
        "title": "Comment les équipements contribuent-ils au score ?",
        "description": "Pour une fonction sociale, l’accessibilité additionne les contributions des équipements. Chaque contribution dépend du poids attribué à l’équipement et diminue de manière exponentielle avec sa distance sur le réseau piéton.",
        "detail": "Dans la formule, g désigne le lieu où le score est calculé, f la fonction sociale, i un équipement, wᵢ son poids et d la distance sur le réseau piéton. Seuls les équipements situés à une distance de parcours inférieure ou égale à 5λ sont retenus. Les scores par fonction sont ensuite agrégés par leur médiane au sein de chaque carreau."
      },
      "scale": {
        "title": "À quoi sert la distance caractéristique λ ?",
        "description": "λ règle la vitesse à laquelle la contribution d’un équipement diminue avec sa distance sur le réseau piéton. Une valeur plus élevée donne davantage de poids aux équipements éloignés.",
        "detail": "La coupure à 5 × λ fixe la distance maximale de parcours prise en compte dans le calcul. Faire varier λ permet d’explorer l’accessibilité à différentes échelles de proximité.",
        "example": "Exemple : pour λ = 400 m, le calcul prend en compte les équipements jusqu’à 2 000 m de parcours sur le réseau piéton."
      },
      "normalization": {
        "title": "Pourquoi la moyenne locale vaut-elle 1 ?",
        "description": "Le score de chaque carreau est divisé par la moyenne arithmétique des valeurs valides des carreaux étudiés. Cette moyenne est calculée séparément pour chaque fonction, chaque ville et chaque valeur de λ.",
        "formula": "Indice relatif = score du carreau / moyenne locale",
        "detail": "Les carreaux ont le même poids dans cette moyenne. Cette lecture permet de comparer leurs positions relatives au sein d’une ville. Une même valeur relative dans deux villes ne signifie pas que les niveaux absolus d’accessibilité sont identiques."
      },
      "pca": {
        "title": "Comment obtient-on l’accessibilité générale, PC1 ?",
        "description": "Les cinq fonctions sont normalisées par leur moyenne puis centrées avant l’analyse en composantes principales. La première composante, PC1, est la combinaison linéaire qui capte la plus grande part de leur variance.",
        "detail": "La carte utilise une version rendue positive de PC1, divisée par sa moyenne locale. Le score affiché exprime une position relative dans la ville à l’échelle choisie. Les rapports calculés sur cette version dépendent de la transformation utilisée pour rendre PC1 positive."
      }
    },
    "charts": {
      "title": "Interpréter les graphiques",
      "intro": "Trois vues permettent d’examiner la répartition des valeurs, leur structure commune et leurs associations avec les caractéristiques sociales.",
      "distribution": {
        "title": "Distributions : comment les valeurs se répartissent-elles ?",
        "description": "Chaque barre regroupe une plage de valeurs. Sa hauteur indique le nombre de carreaux correspondants. Chaque carreau compte une fois, indépendamment de sa population.",
        "reading": "Pour les indices relatifs, la ligne à 1 marque la moyenne locale. Le survol d’une barre donne son intervalle et son effectif.",
        "range": "Dans l’affichage actuel, les bornes sont resserrées autour des 1er et 99e percentiles. Les valeurs extérieures sont regroupées dans les barres d’extrémité."
      },
      "structure": {
        "title": "Structure commune : comment évolue la variance expliquée ?",
        "description": "La courbe présente la part de variance des cinq fonctions captée par PC1 en fonction de la distance caractéristique λ, exprimée en mètres sur le réseau piéton.",
        "threshold": "Le seuil de 85 % est le critère retenu dans cette étude pour repérer une structure commune. La distance indiquée est la première distance testée qui atteint ou dépasse ce seuil. Ce repère dépend des échelles disponibles et constitue un choix méthodologique de l’étude."
      },
      "indicators": {
        "title": "Indicateurs urbains : comment lire les comparaisons ?",
        "intro": "Les villes sont comparées à une même distance caractéristique λ. Chaque indicateur décrit un aspect particulier de la relation entre l’accessibilité et les caractéristiques des carreaux.",
        "ranking": "Les corrélations sont classées par valeur décroissante. Pour l’écart Q5–Q1, le classement place en tête les valeurs les plus proches de zéro, en tenant compte de leur valeur absolue.",
        "scope": "Ces résultats décrivent des relations entre carreaux. Ils n’établissent pas à eux seuls des relations individuelles ou causales, ni une mesure générale de l’équité."
      }
    },
    "indicators": {
      "population": {
        "title": "Accessibilité–population : corrélation de Pearson",
        "description": "Ce coefficient mesure la relation linéaire entre PC1 et la population des carreaux. Il varie de −1 à 1.",
        "reading": "Une valeur positive indique une tendance à des scores plus élevés dans les carreaux plus peuplés ; une valeur négative indique la tendance inverse. Une forte corrélation ne suffit pas à établir une répartition proportionnelle à la population."
      },
      "income": {
        "title": "Accessibilité–niveau de vie : corrélation de Spearman",
        "description": "Ce coefficient compare les rangs de PC1 et du niveau de vie entre les carreaux. Il varie de −1 à 1.",
        "reading": "Une valeur positive indique que les carreaux aux niveaux de vie plus élevés tendent à avoir des scores d’accessibilité plus élevés. Une valeur négative indique la relation inverse. Une valeur proche de zéro correspond à une faible association des rangs."
      },
      "gap": {
        "title": "Écart d’accessibilité entre les groupes locaux Q5 et Q1",
        "description": "Q1 regroupe les carreaux aux niveaux de vie les plus faibles et Q5 ceux aux niveaux de vie les plus élevés dans la ville. Les seuils locaux sont calculés sans pondération par la population ; les valeurs ex æquo peuvent conduire à des groupes de tailles différentes.",
        "formula": "Écart (%) = 100 × [m(Q5) − m(Q1)] / m(Q1)",
        "reading": "m(Q1) et m(Q5) sont les médianes du score PC1 positif dans ces groupes. Un écart positif indique une médiane plus élevée dans Q5 ; un écart négatif indique l’inverse. Zéro correspond à des médianes identiques. Le pourcentage est défini lorsque m(Q1) est non nulle et dépend de la transformation de PC1 utilisée."
      }
    }
  },
  "en": {
    "referenceLabel": "References:",
    "page": {
      "label": "Documentation",
      "title": "Understanding the maps and indicators",
      "intro": "This observatory explores accessibility to everyday facilities and its relationships with population and living standards in ten French cities.",
      "cities": "10 cities",
      "functions": "5 social functions",
      "grid": "200 m grid cells"
    },
    "network": {
      "title": "Distances measured along the pedestrian network",
      "description": "Distances are the lengths of the shortest paths along the pedestrian network between the study location and the facilities. The characteristic distance λ and the cutoff at 5 × λ refer to these network distances."
    },
    "functions": {
      "commerce": "Retail",
      "health": "Healthcare",
      "education": "Education",
      "services": "Everyday services",
      "leisure": "Leisure, culture and social interaction"
    },
    "maps": {
      "title": "Reading the maps",
      "description": "Results are displayed on the Insee 200-metre grid. One variable is shown at a time. Accessibility is examined for five social functions:",
      "relativeTitle": "Accessibility scores",
      "relativeDescription": "For each social function, the cell score is divided by the mean across the cells studied in the city, at the selected characteristic distance. The following examples apply to these function-specific scores:",
      "colors": "Red indicates a score below the local mean; green indicates a score above it. The colours therefore show each cell’s position within its city.",
      "pca": "Overall accessibility uses a composite score, PC1. Its map is also relative to the local mean, after transforming the score into positive values. This transformation is explained in the calculations section.",
      "observedTitle": "Living standards and population",
      "observedDescription": "These maps show values in their units: annual euros per consumption unit for living standards, and people per cell for population. Neither variable depends on the characteristic distance λ.",
      "boundary": "The municipal boundary provides a geographical reference. Results are displayed at the level of 200-metre grid cells."
    },
    "examples": {
      "half": "Half the local mean",
      "average": "Local mean",
      "double": "Twice the local mean"
    },
    "calculations": {
      "title": "Understanding the calculations",
      "intro": "The explanations below describe how the scores are constructed, the role of distance and how to interpret PC1.",
      "access": {
        "title": "How do facilities contribute to the score?",
        "description": "For each social function, accessibility sums the contributions of facilities. Each contribution depends on the weight assigned to the facility and decreases exponentially with its distance along the pedestrian network.",
        "detail": "In the formula, g is the location where the score is calculated, f the social function, i a facility, wᵢ its weight and d the pedestrian network distance. Only facilities within a network distance of 5λ are included. Function-specific scores are then aggregated using their median within each grid cell."
      },
      "scale": {
        "title": "What does the characteristic distance λ control?",
        "description": "λ controls how quickly a facility’s contribution decreases with distance along the pedestrian network. A larger value gives more weight to distant facilities.",
        "detail": "The cutoff at 5 × λ sets the maximum network distance included in the calculation. Varying λ allows accessibility to be explored at different proximity scales.",
        "example": "Example: with λ = 400 m, the calculation includes facilities up to 2,000 m away along the pedestrian network."
      },
      "normalization": {
        "title": "Why is the local mean equal to 1?",
        "description": "Each cell score is divided by the arithmetic mean of the valid values across the cells studied. This mean is calculated separately for each function, city and value of λ.",
        "formula": "Relative index = cell score / local mean",
        "detail": "All cells have equal weight in this mean. This approach compares their relative positions within a city. The same relative value in two cities does not imply identical absolute accessibility levels."
      },
      "pca": {
        "title": "How is overall accessibility, PC1, obtained?",
        "description": "The five functions are normalized by their mean and then centred before principal component analysis. The first component, PC1, is the linear combination that captures the largest share of their variance.",
        "detail": "The map uses a positive version of PC1 divided by its local mean. The displayed score expresses a relative position within the city at the chosen scale. Ratios calculated from this version depend on the transformation used to make PC1 positive."
      }
    },
    "charts": {
      "title": "Interpreting the charts",
      "intro": "Three views describe the distribution of values, their common structure and their associations with social characteristics.",
      "distribution": {
        "title": "Distributions: how are values spread across cells?",
        "description": "Each bar represents a range of values. Its height gives the number of corresponding cells. Every cell is counted once, regardless of its population.",
        "reading": "For relative indices, the line at 1 marks the local mean. Hovering over a bar shows its interval and count.",
        "range": "In the current display, the limits are narrowed around the 1st and 99th percentiles. Values outside these limits are grouped into the bars at the ends."
      },
      "structure": {
        "title": "Common structure: how does explained variance change?",
        "description": "The curve shows the share of variance in the five functions captured by PC1 as the characteristic distance λ increases, expressed in metres along the pedestrian network.",
        "threshold": "The 85% threshold is the criterion adopted in this study to identify a common structure. The reported distance is the first tested distance that reaches or exceeds this threshold. This reference depends on the available scales and is a methodological choice of the study."
      },
      "indicators": {
        "title": "Urban indicators: how should comparisons be read?",
        "intro": "Cities are compared at the same characteristic distance λ. Each indicator describes a particular aspect of the relationship between accessibility and the characteristics of grid cells.",
        "ranking": "Correlations are ranked in descending order. For the Q5–Q1 gap, values closest to zero are placed first, using their absolute values.",
        "scope": "These results describe relationships between grid cells. On their own, they do not establish individual or causal relationships, nor do they provide a general measure of equity."
      }
    },
    "indicators": {
      "population": {
        "title": "Accessibility–population: Pearson correlation",
        "description": "This coefficient measures the linear relationship between PC1 and cell population. It ranges from −1 to 1.",
        "reading": "A positive value indicates a tendency for more populated cells to have higher scores; a negative value indicates the opposite tendency. A strong correlation alone does not establish that accessibility is distributed in proportion to population."
      },
      "income": {
        "title": "Accessibility–living standards: Spearman correlation",
        "description": "This coefficient compares the ranks of PC1 and living standards across cells. It ranges from −1 to 1.",
        "reading": "A positive value indicates that cells with higher living standards tend to have higher accessibility scores. A negative value indicates the reverse relationship. A value close to zero corresponds to a weak association between the ranks."
      },
      "gap": {
        "title": "Accessibility gap between local groups Q5 and Q1",
        "description": "Q1 groups cells with the lowest living standards and Q5 those with the highest living standards within the city. Local thresholds are calculated without population weighting; tied values can produce groups of different sizes.",
        "formula": "Gap (%) = 100 × [m(Q5) − m(Q1)] / m(Q1)",
        "reading": "m(Q1) and m(Q5) are the medians of the positive PC1 score in these groups. A positive gap indicates a higher median in Q5; a negative gap indicates the reverse. Zero means identical medians. The percentage is defined when m(Q1) is non-zero and depends on the PC1 transformation used."
      }
    }
  }
}
</i18n>

<style scoped>
.method-documentation {
  color: var(--ink);
  font-size: 16px;
  line-height: 1.7;
}

.method-documentation h2,
.method-documentation h3,
.method-documentation h4 {
  color: var(--ink);
  line-height: 1.3;
}

.method-documentation h2 {
  margin: 6px 0 12px;
  font-size: clamp(24px, 3vw, 30px);
}

.method-documentation h3 {
  margin: 0 0 14px;
  font-size: 21px;
}

.method-documentation h4 {
  margin: 24px 0 8px;
  font-size: 17px;
}

.method-documentation p {
  max-width: 80ch;
  margin: 10px 0;
  color: var(--ink);
}

.method-eyebrow {
  color: var(--teal);
  font-size: 13px;
  font-weight: 700;
}

.method-documentation .method-intro,
.method-documentation .method-secondary {
  color: var(--muted);
}

.method-facts,
.function-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 18px 0;
  padding: 0;
  list-style: none;
}

.method-facts li,
.function-chips li {
  padding: 5px 12px;
  color: var(--ink);
  background: var(--background);
  border: 1px solid var(--line);
  border-radius: 7px;
  font-size: 14px;
}

.method-facts li {
  font-weight: 600;
}

.network-note {
  margin-top: 26px;
  padding: 18px 20px;
  background: var(--background);
  border: 1px solid var(--line);
  border-left: 4px solid var(--teal);
  border-radius: 9px;
}

.network-note strong {
  display: block;
  color: var(--ink);
}

.network-note p {
  margin-bottom: 0;
}

.method-section {
  margin-top: 32px;
}

.method-section + .method-section {
  padding-top: 28px;
  border-top: 1px solid var(--line);
}

.score-examples {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  max-width: 760px;
  margin: 18px 0;
}

.score-examples > div {
  padding: 12px 14px;
  background: var(--background);
  border: 1px solid var(--line);
  border-bottom: 3px solid var(--line);
  border-radius: 8px;
}

.score-examples .below {
  border-bottom-color: #b2182b;
}

.score-examples .average {
  border-bottom-color: #8b949e;
}

.score-examples .above {
  border-bottom-color: #1a9850;
}

.score-examples dt {
  color: var(--ink);
  font-size: 22px;
  font-weight: 700;
}

.score-examples dd {
  margin: 3px 0 0;
  color: var(--muted);
  font-size: 14px;
}

.method-details {
  border-bottom: 1px solid var(--line);
}

.method-details summary {
  padding: 16px 4px;
  color: var(--ink);
  font-weight: 600;
  cursor: pointer;
}

.method-details summary:hover {
  color: var(--teal);
}

.detail-content {
  padding: 0 8px 18px 22px;
}

.method-documentation .method-formula {
  max-width: 100%;
  padding: 12px 16px;
  overflow-x: auto;
  color: var(--ink);
  background: var(--background);
  border-left: 3px solid var(--teal);
  border-radius: 4px;
  font-family: Georgia, serif;
  font-size: 17px;
}

.method-example {
  padding: 12px 16px;
  background: var(--background);
  border: 1px solid var(--line);
  border-radius: 7px;
}

.method-reference {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 6px 12px;
  font-size: 14px;
}

.method-documentation a {
  color: var(--ink);
  text-decoration-color: var(--teal);
  text-underline-offset: 4px;
}

.method-documentation a:hover {
  text-decoration-thickness: 2px;
}

.method-documentation a:focus-visible,
.method-details summary:focus-visible {
  outline: 2px solid var(--teal);
  outline-offset: 4px;
  border-radius: 3px;
}

.indicator-definitions {
  margin: 20px 0;
}

.indicator-definitions > div + div {
  margin-top: 22px;
  padding-top: 18px;
  border-top: 1px solid var(--line);
}

.indicator-definitions dt {
  color: var(--ink);
  font-weight: 700;
}

.indicator-definitions dd {
  margin: 0;
}

@media (max-width: 600px) {
  .score-examples {
    grid-template-columns: 1fr;
  }

  .detail-content {
    padding-left: 8px;
  }

  .network-note {
    padding: 16px;
  }
}
</style>