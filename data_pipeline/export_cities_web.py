from argparse import ArgumentParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json
import re
import unicodedata

import geopandas as gpd
import numpy as np
import pandas as pd


VILLES = {
    "Paris": "75056",
    "Marseille": "13055",
    "Lyon": "69123",
    "Toulouse": "31555",
    "Nice": "06088",
    "Nantes": "44109",
    "Montpellier": "34172",
    "Strasbourg": "67482",
    "Bordeaux": "33063",
    "Lille": "59350",
}

FONCTIONS = {
    "education": "median_education",
    "sante": "median_healthcare",
    "services": "median_services",
    "commerce": "median_commerce",
    "loisirs": "median_entertainment",
}

COLONNES_POPULATION = [
    "population",
    "ind",
    "ind_x",
    "ind_y",
]

COLONNES_PC = [
    "PC1",
    "PC2",
    "PC3",
    "PC4",
    "PC5",
]

COLONNES_SOURCE = [
    "idcar_200m",
    "population",
    *FONCTIONS.values(),
    "PC1_pos",
    "nivvie",
    "geometry",
]


def creer_slug(texte: str) -> str:
    normalise = unicodedata.normalize("NFKD", texte)
    ascii_seul = normalise.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_seul.lower()).strip("-")


def calculer_quintile_local(serie: pd.Series) -> pd.Series:
    """Classer en quintiles locaux sans séparer les valeurs ex æquo."""
    valeurs = pd.to_numeric(serie, errors="coerce").replace(
        [np.inf, -np.inf],
        np.nan,
    )

    classes = pd.Series(0, index=serie.index, dtype="int64")
    valeurs_valides = valeurs.dropna()

    if valeurs_valides.empty:
        return classes

    seuils = valeurs_valides.quantile([0.2, 0.4, 0.6, 0.8]).to_numpy()

    classes.loc[valeurs_valides.index] = (
        np.searchsorted(
            seuils,
            valeurs_valides.to_numpy(),
            side="left",
        )
        + 1
    )

    return classes


def calculer_indice_relatif(serie: pd.Series, nom: str) -> pd.Series:
    """Ramener une variable à sa moyenne communale, qui devient égale à 1."""
    valeurs = pd.to_numeric(serie, errors="coerce").replace(
        [np.inf, -np.inf],
        np.nan,
    )

    moyenne = valeurs.mean(skipna=True)

    if not np.isfinite(moyenne) or moyenne == 0:
        raise ValueError(
            f"Impossible de normaliser {nom} : moyenne nulle ou absente."
        )

    return valeurs / moyenne

def calculer_correlation(
    gdf,
    colonne_x,
    colonne_y,
    methode,
):
    donnees = (
        gdf[[colonne_x, colonne_y]]
        .apply(
            lambda serie: pd.to_numeric(
                serie,
                errors="coerce",
            )
        )
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
    )

    if (
        len(donnees) < 3
        or donnees[colonne_x].nunique() < 2
        or donnees[colonne_y].nunique() < 2
    ):
        return None, len(donnees)

    if methode == "spearman":
        coefficient = (
            donnees[colonne_x]
            .rank(method="average")
            .corr(
                donnees[colonne_y].rank(method="average")
            )
        )
    else:
        coefficient = donnees[colonne_x].corr(
            donnees[colonne_y]
        )

    if not np.isfinite(coefficient):
        return None, len(donnees)

    return float(coefficient), len(donnees)


def calculer_analyses_echelle(
    gdf,
    fichier_nom,
):
    colonnes_absentes = [
        colonne
        for colonne in COLONNES_PC
        if colonne not in gdf.columns
    ]

    if colonnes_absentes:
        raise ValueError(
            f"Composantes absentes dans {fichier_nom} : "
            f"{colonnes_absentes}"
        )

    composantes = (
        gdf[COLONNES_PC]
        .apply(
            lambda serie: pd.to_numeric(
                serie,
                errors="coerce",
            )
        )
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
    )

    variances = composantes.var(ddof=1)
    variance_totale = variances.sum()

    if not np.isfinite(variance_totale) or variance_totale <= 0:
        raise ValueError(
            f"Variance PCA impossible à calculer dans {fichier_nom}."
        )

    evr_pc1 = float(
        variances["PC1"] / variance_totale
    )

    pearson_population, n_population = calculer_correlation(
        gdf,
        "PC1_pos",
        "population",
        "pearson",
    )

    spearman_revenu, n_revenu = calculer_correlation(
        gdf,
        "PC1_pos",
        "nivvie",
        "spearman",
    )
    
    revenu = pd.to_numeric(
        gdf["nivvie"],
        errors="coerce",
    ).replace([np.inf, -np.inf], np.nan)

    pc1 = pd.to_numeric(
        gdf["PC1"],
        errors="coerce",
    ).replace([np.inf, -np.inf], np.nan)

    quintiles_revenu = calculer_quintile_local(revenu)

    base_ecart = pd.DataFrame(
        {
            "pc1": pc1,
            "quintile": quintiles_revenu,
        }
    ).dropna()

    pc1_q1 = base_ecart.loc[
        base_ecart["quintile"].eq(1),
        "pc1",
    ]

    pc1_q5 = base_ecart.loc[
        base_ecart["quintile"].eq(5),
        "pc1",
    ]

    mediane_q1 = pc1_q1.median()
    mediane_q5 = pc1_q5.median()

    iqr_pc1 = pc1.quantile(0.75) - pc1.quantile(0.25)

    if (
        len(pc1_q1) > 0
        and len(pc1_q5) > 0
        and np.isfinite(iqr_pc1)
        and iqr_pc1 > 0
    ):
        ecart_q5_q1 = float(
            (mediane_q5 - mediane_q1) / iqr_pc1 )
    else:
        ecart_q5_q1 = None

    return {
        "pc1_evr": evr_pc1,
        "pc1_population_r": pearson_population,
        "population_correlation_n": n_population,
        "pc1_income_spearman": spearman_revenu,
        "income_correlation_n": n_revenu,
        "pc1_income_gap": ecart_q5_q1,
        "pc1_income_gap_n": int(len(pc1_q1) + len(pc1_q5)),
        "pc1_income_q1_median": (
        float(mediane_q1)
        if np.isfinite(mediane_q1) else None),
        "pc1_income_q5_median": (float(mediane_q5) if np.isfinite(mediane_q5) else None),
    }

def trouver_fichiers(
    dossier: Path,
    ville: str,
    bw_min: int,
    bw_max: int,
) -> list[tuple[int, int, Path]]:
    motif = re.compile(
        rf"^stats_carr200m_filo_merged_{re.escape(ville)}_"
        rf"bw(?P<bw>\d+)_cut(?P<cutoff>\d+)_pca\.gpkg$",
        flags=re.IGNORECASE,
    )

    fichiers: list[tuple[int, int, Path]] = []

    for fichier in dossier.glob("*.gpkg"):
        correspondance = motif.match(fichier.name)

        if correspondance is None:
            continue

        bw = int(correspondance.group("bw"))
        cutoff = int(correspondance.group("cutoff"))

        if not bw_min <= bw <= bw_max:
            continue

        if cutoff != 5 * bw:
            print(
                f"  Ignoré : {fichier.name} "
                f"(cutoff={cutoff}, attendu={5 * bw})"
            )
            continue

        fichiers.append((bw, cutoff, fichier))

    return sorted(fichiers, key=lambda element: element[0])

def harmoniser_population(
    gdf: gpd.GeoDataFrame,
    fichier_nom: str,
) -> gpd.GeoDataFrame:

    colonnes_disponibles = {
        str(colonne).lower(): colonne
        for colonne in gdf.columns
    }

    colonne_population = next(
        (
            colonnes_disponibles[nom]
            for nom in COLONNES_POPULATION
            if nom in colonnes_disponibles
        ),
        None,
    )

    if colonne_population is None:
        raise ValueError(
            f"Aucune colonne de population trouvée dans "
            f"{fichier_nom}. Colonnes recherchées : "
            f"{COLONNES_POPULATION}"
        )

    gdf = gdf.copy()

    gdf["population"] = pd.to_numeric(
        gdf[colonne_population],
        errors="coerce",
    )

    print(
        f"  Population récupérée depuis : "
        f"{colonne_population}"
    )

    return gdf

def exporter_echelle(
    fichier_source: Path,
    fichier_sortie: Path,
) -> int:
    gdf = gpd.read_file(fichier_source)

    gdf = harmoniser_population(
        gdf,
        fichier_source.name,
    )
    
    analyses = calculer_analyses_echelle(
        gdf,
        fichier_source.name,
    )

    colonnes_absentes = [
        colonne
        for colonne in COLONNES_SOURCE
        if colonne not in gdf.columns
    ]

    if colonnes_absentes:
        raise ValueError(
            f"Colonnes absentes dans {fichier_source.name} : "
            f"{colonnes_absentes}"
        )

    gdf = gdf[COLONNES_SOURCE].copy()
    gdf = gdf.loc[
        gdf.geometry.notna() & ~gdf.geometry.is_empty
    ].copy()

    for nom, colonne in FONCTIONS.items():
        gdf[f"rel_{nom}"] = calculer_indice_relatif(
            gdf[colonne],
            colonne,
        )

    gdf["rel_pc1"] = calculer_indice_relatif(
        gdf["PC1_pos"],
        "PC1_pos",
    )

    gdf["q_revenu"] = calculer_quintile_local(gdf["nivvie"])
    gdf["q_population"] = calculer_quintile_local(gdf["population"])

    gdf = gdf.to_crs("EPSG:4326")

    fichier_sortie.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(
        fichier_sortie,
        driver="GeoJSON",
        index=False,
    )

    return len(gdf), analyses


def normaliser_limite_geojson(
    donnees: dict,
    ville: str,
    code: str,
) -> dict:
    if donnees.get("type") == "Feature":
        feature = donnees
    elif donnees.get("type") == "FeatureCollection":
        features = donnees.get("features", [])

        if not features:
            raise ValueError("La réponse GeoJSON ne contient aucune géométrie.")

        feature = features[0]
    else:
        raise ValueError("La réponse de l'API n'est pas un GeoJSON reconnu.")

    geometrie = feature.get("geometry")

    if not geometrie or geometrie.get("type") not in {
        "Polygon",
        "MultiPolygon",
    }:
        raise ValueError("La limite communale ne contient pas de polygone.")

    proprietes = feature.get("properties") or {}
    proprietes["nom"] = ville
    proprietes["code"] = code

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": proprietes,
                "geometry": geometrie,
            }
        ],
    }


def obtenir_limite_communale(
    ville: str,
    code: str,
    fichier_sortie: Path,
    actualiser: bool,
) -> bool:
    if fichier_sortie.exists() and not actualiser:
        print("  Limite communale : fichier existant réutilisé")
        return True

    url = (
        f"https://geo.api.gouv.fr/communes/{code}"
        "?format=geojson&geometry=contour"
    )

    requete = Request(
        url,
        headers={
            "User-Agent": "Observatoire-proximite/0.1",
            "Accept": "application/geo+json, application/json",
        },
    )

    try:
        with urlopen(requete, timeout=30) as reponse:
            donnees = json.loads(reponse.read().decode("utf-8"))

        limite = normaliser_limite_geojson(donnees, ville, code)

        fichier_sortie.parent.mkdir(parents=True, exist_ok=True)

        with fichier_sortie.open("w", encoding="utf-8") as flux:
            json.dump(
                limite,
                flux,
                ensure_ascii=False,
                separators=(",", ":"),
            )

        print("  Limite communale : téléchargée")
        return True

    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
        print(f"  Attention : limite communale indisponible ({error})")
        return fichier_sortie.exists()


parser = ArgumentParser(
    description=(
        "Exporter toutes les villes, leurs échelles disponibles et leurs "
        "limites communales pour l'observatoire web."
    )
)

parser.add_argument(
    "racine",
    type=Path,
    help="Dossier processed/ext contenant un sous-dossier par ville",
)

parser.add_argument(
    "--sortie",
    type=Path,
    default=Path("public/data"),
    help="Dossier public/data du projet Nuxt",
)

parser.add_argument(
    "--villes",
    nargs="*",
    choices=list(VILLES),
    help="Sous-ensemble à exporter ; toutes les villes par défaut",
)

parser.add_argument("--bw-min", type=int, default=50)
parser.add_argument("--bw-max", type=int, default=1000)

parser.add_argument(
    "--actualiser-limites",
    action="store_true",
    help="Télécharger à nouveau les contours communaux déjà présents",
)

args = parser.parse_args()

racine_source = args.racine.resolve()
dossier_sortie = args.sortie.resolve()
villes_demandees = args.villes or list(VILLES)

if not racine_source.exists():
    raise FileNotFoundError(
        f"Dossier source introuvable : {racine_source}"
    )

dossier_sortie.mkdir(parents=True, exist_ok=True)

manifest_general = {
    "reading": "local",
    "relative_reference": 1,
    "pc1_evr_threshold": 0.85,
    "cities": [],
}

for ville in villes_demandees:
    code = VILLES[ville]
    slug = creer_slug(ville)
    dossier_carreaux = racine_source / ville / "carreaux"

    print()
    print("=" * 72)
    print(f"{ville} — code commune {code}")
    print("=" * 72)

    if not dossier_carreaux.exists():
        print(f"Dossier absent, ville ignorée : {dossier_carreaux}")
        continue

    fichiers = trouver_fichiers(
        dossier_carreaux,
        ville,
        args.bw_min,
        args.bw_max,
    )

    if not fichiers:
        print("Aucune échelle conforme trouvée, ville ignorée.")
        continue

    dossier_ville = dossier_sortie / slug
    dossier_ville.mkdir(parents=True, exist_ok=True)

    fichier_limite = dossier_ville / "boundary.geojson"
    limite_disponible = obtenir_limite_communale(
        ville,
        code,
        fichier_limite,
        args.actualiser_limites,
    )

    manifest_ville = {
        "name": ville,
        "slug": slug,
        "code": code,
        "boundary": (
            f"/data/{slug}/boundary.geojson"
            if limite_disponible
            else None
        ),
        "scales": [],
    }

    print(f"  {len(fichiers)} échelle(s) détectée(s)")

    for bw, cutoff, fichier_source in fichiers:
        fichier_geojson = dossier_ville / f"bw{bw}.geojson"

        print(f"  BW {bw} m — cutoff {cutoff} m")
        
        nombre_carreaux, analyses = exporter_echelle(
            fichier_source,
            fichier_geojson,
       )

        taille_mo = fichier_geojson.stat().st_size / 1_000_000
        print(f"    {nombre_carreaux:,} carreaux — {taille_mo:.2f} Mo")

        manifest_ville["scales"].append(
            {
                "bw": bw,
                "cutoff": cutoff,
                "file": f"/data/{slug}/bw{bw}.geojson",
                "analysis": analyses,
            }
        )

    fichier_manifest_ville = dossier_ville / "manifest.json"

    with fichier_manifest_ville.open("w", encoding="utf-8") as flux:
        json.dump(
            manifest_ville,
            flux,
            ensure_ascii=False,
            indent=2,
        )

    manifest_general["cities"].append(manifest_ville)

fichier_manifest_general = dossier_sortie / "cities.json"

with fichier_manifest_general.open("w", encoding="utf-8") as flux:
    json.dump(
        manifest_general,
        flux,
        ensure_ascii=False,
        indent=2,
    )

print()
print("Export multiville terminé")
print(f"Villes exportées : {len(manifest_general['cities'])}")
print(f"Manifeste général : {fichier_manifest_general}")
