<template>
  <div ref="mapContainer" class="map"></div>
</template>

<script setup lang="ts">
import {
  Map as MapLibreMap,
  NavigationControl,
  ScaleControl,
} from "maplibre-gl"

import "maplibre-gl/dist/maplibre-gl.css"

const mapContainer = ref<HTMLDivElement | null>(null)

let map: MapLibreMap | null = null

onMounted(() => {
  if (!mapContainer.value) {
    return
  }

  map = new MapLibreMap({
    container: mapContainer.value,

    style: {
      version: 8,

      sources: {
        openstreetmap: {
          type: "raster",
          tiles: [
            "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
          ],
          tileSize: 256,
          attribution: "© OpenStreetMap contributors",
        },
      },

      layers: [
        {
          id: "openstreetmap",
          type: "raster",
          source: "openstreetmap",
        },
      ],
    },

    center: [5.3698, 43.2965],
    zoom: 11,
  })

  map.addControl(
    new NavigationControl(),
    "top-right",
  )

  map.addControl(
    new ScaleControl({
      unit: "metric",
    }),
    "bottom-left",
  )
})

onBeforeUnmount(() => {
  map?.remove()
  map = null
})
</script>

<style scoped>
.map {
  width: 100%;
  height: 100%;
  min-height: 500px;
}
</style>