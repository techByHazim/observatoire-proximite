# Observatoire de la proximité urbaine

Application cartographique interactive sur l’étude de l’accessibilité de proximité et des inégalités urbaines dans dix villes françaises.

🔗 **Application en ligne :**  
https://observatoire-proximite.vercel.app/

## Présentation

Cet observatoire valorise des indicateurs développés dans le cadre d’un travail de thèse sur l’accessibilité urbaine.

Il permet d’explorer la distribution spatiale de l’accès à cinq fonctions sociales :

- commerce ;
- santé ;
- éducation ;
- services du quotidien ;
- loisirs, culture et sociabilité.

Les résultats sont représentés sur le carroyage Insee de 200 mètres.

## Fonctionnalités

- exploration de dix villes françaises ;
- analyse à différentes distances caractéristiques ;
- cartographie interactive des fonctions sociales ;
- indicateur synthétique d’accessibilité fondé sur la première composante principale ;
- représentation de la population et du niveau de vie ;
- graphiques interactifs ;
- comparaison d’indicateurs urbains entre les villes ;
- et d'autres fonctionnalités en cours de développement.

## Méthode

L’accessibilité d’un lieu `g` à une fonction sociale `f` est calculée à partir d’une fonction de décroissance exponentielle :

```text
A(g,f,λ) = Σ wᵢ × exp(−d(g,i) / λ)
```

où :

- `wᵢ` représente le poids de l’équipement ;
- `d(g,i)` représente sa distance par le réseau piéton ;
- `λ` représente la distance caractéristique ;

Une analyse en composantes principales est ensuite utilisée pour faire émerger la dimension commune aux cinq fonctions sociales.

## Données mobilisées

- Insee : carroyage Filosofi 2021 ;
- Insee : Base permanente des équipements 2024 ;
- OpenStreetMap : équipements complémentaires et réseau piéton ;
- API Découpage administratif : limites communales ;
- indicateurs et traitements issus du travail de thèse.

## Technologies

- Nuxt 4 ;
- Vue 3 ;
- TypeScript ;
- MapLibre GL JS ;
- GeoPandas pour la préparation des données ;
- Vercel pour le déploiement.

## Installation locale

Installer les dépendances :

```bash
npm install
```

Lancer le serveur de développement :

```bash
npm run dev
```

L’application est ensuite accessible à l’adresse :

```text
http://localhost:3000/
```

Compiler la version de production :

```bash
npm run build
```

## Structure principale

```text
app/
├── app.vue
└── components/
    ├── MapView.client.vue
    ├── ChartView.client.vue
    ├── CommonStructureChart.client.vue
    └── CityIndicatorsChart.client.vue

data_pipeline/
public/data/
i18n/locales/
```

## Statut du projet

L’observatoire est un prototype de recherche en cours de développement. Les indicateurs, interprétations et fonctionnalités sont susceptibles d’évoluer avec l’avancement de la thèse.