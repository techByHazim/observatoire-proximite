from argparse import ArgumentParser
from pathlib import Path
import json
import re

import geopandas as gpd
import numpy as np
import pandas as pd


FONCTIONS = {
    "education": "median_education",
    "sante": "median_healthcare",
    "services": "median_services",
    "commerce": "median_commerce",
    "loisirs": "median_entertainment",
}

COLONNES_SOURCE = [
    "idcar_200m",
    "population",
    *FONCTIONS.values(),
    "PC1_pos",
    "nivvie",
    "geometry",
]


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
    """Ramener une variable à la moyenne communale, qui devient égale à 1."""
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
                f"Fichier ignoré : {fichier.name} "
                f"(cutoff={cutoff}, attendu={5 * bw})"
            )
            continue

        fichiers.append((bw, cutoff, fichier))

    return sorted(fichiers, key=lambda element: element[0])


def exporter_echelle(
    fichier_source: Path,
    fichier_sortie: Path,
) -> int:
    gdf = gpd.read_file(fichier_source)

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

    # Fonctions sociales : valeur relative à la moyenne de Marseille.
    for nom, colonne in FONCTIONS.items():
        gdf[f"rel_{nom}"] = calculer_indice_relatif(
            gdf[colonne],
            colonne,
        )

    # PC1_pos est lui aussi ramené à sa moyenne communale.
    gdf["rel_pc1"] = calculer_indice_relatif(
        gdf["PC1_pos"],
        "PC1_pos",
    )

    # Les variables contextuelles restent représentées par quintiles locaux.
    gdf["q_revenu"] = calculer_quintile_local(gdf["nivvie"])
    gdf["q_population"] = calculer_quintile_local(gdf["population"])

    gdf = gdf.to_crs("EPSG:4326")

    fichier_sortie.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(
        fichier_sortie,
        driver="GeoJSON",
        index=False,
    )

    return len(gdf)


parser = ArgumentParser(
    description=(
        "Exporter automatiquement toutes les échelles disponibles "
        "pour l'observatoire web."
    )
)

parser.add_argument(
    "dossier",
    type=Path,
    help="Dossier contenant les GeoPackages PCA d'une ville",
)

parser.add_argument(
    "--ville",
    default="Marseille",
    help="Nom de la ville utilisé dans les noms de fichiers",
)

parser.add_argument(
    "--sortie",
    type=Path,
    default=Path("public/data"),
    help="Dossier public/data du projet Nuxt",
)

parser.add_argument("--bw-min", type=int, default=50)
parser.add_argument("--bw-max", type=int, default=1000)

args = parser.parse_args()

dossier_source = args.dossier.resolve()
dossier_sortie = args.sortie.resolve()
ville = args.ville.strip()
ville_slug = ville.lower().replace(" ", "-")

if not dossier_source.exists():
    raise FileNotFoundError(
        f"Dossier source introuvable : {dossier_source}"
    )

fichiers = trouver_fichiers(
    dossier_source,
    ville,
    args.bw_min,
    args.bw_max,
)

if not fichiers:
    raise FileNotFoundError(
        "Aucun fichier conforme trouvé. Format attendu : "
        f"stats_carr200m_filo_merged_{ville}_bw<BW>_cut<CUTOFF>_pca.gpkg"
    )

dossier_ville = dossier_sortie / ville_slug
dossier_ville.mkdir(parents=True, exist_ok=True)

manifest = {
    "city": ville,
    "reading": "local",
    "relative_reference": 1,
    "scales": [],
}

print(f"{len(fichiers)} échelle(s) détectée(s).")

for bw, cutoff, fichier_source in fichiers:
    fichier_sortie = dossier_ville / f"bw{bw}.geojson"

    print()
    print(f"BW {bw} m — cutoff {cutoff} m")
    print(f"Lecture : {fichier_source.name}")

    nombre_carreaux = exporter_echelle(
        fichier_source,
        fichier_sortie,
    )

    taille_mo = fichier_sortie.stat().st_size / 1_000_000

    print(
        f"Export : {nombre_carreaux:,} carreaux — {taille_mo:.2f} Mo"
    )

    manifest["scales"].append(
        {
            "bw": bw,
            "cutoff": cutoff,
            "file": f"/data/{ville_slug}/bw{bw}.geojson",
        }
    )

fichier_manifest = dossier_ville / "manifest.json"

with fichier_manifest.open("w", encoding="utf-8") as flux:
    json.dump(
        manifest,
        flux,
        ensure_ascii=False,
        indent=2,
    )

print()
print("Export multi-échelle terminé")
print(f"Manifeste : {fichier_manifest}")
