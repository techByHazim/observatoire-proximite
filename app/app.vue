<script setup lang="ts">
import MapView from "./components/MapView.client.vue"
</script>

<template>
  <div class="application">
    <header class="header">
      <div>
        <h1>Observatoire de la proximité urbaine</h1>
        <p>Prototype cartographique — Marseille</p>
      </div>
    </header>

    <main class="workspace">
      <aside class="sidebar">
        <section>
          <h2>Territoire</h2>

          <label for="city">Ville</label>

          <select id="city">
            <option>Marseille</option>
          </select>
        </section>

        <section>
          <h2>Échelle de proximité</h2>

          <label for="scale">
            Distance caractéristique
          </label>

          <select id="scale">
            <option>400 mètres</option>
          </select>
        </section>

        <section>
          <h2>Fonction sociale</h2>

          <div class="functions">
            <button class="active">
              Commerce
            </button>

            <button>Santé</button>
            <button>Éducation</button>
            <button>Services</button>
            <button>Loisirs</button>
          </div>
        </section>
      </aside>

      <section class="map-container">
        <ClientOnly>
          <MapView />

          <template #fallback>
            <div class="map-loading">
              Chargement de la carte…
            </div>
          </template>
        </ClientOnly>
      </section>
    </main>
  </div>
</template>

<style>
* {
  box-sizing: border-box;
}

html,
body,
#__nuxt {
  width: 100%;
  height: 100%;
  margin: 0;
}

body {
  font-family:
    Inter,
    Arial,
    sans-serif;
  color: #17202a;
  background: #f4f6f8;
}

button,
select {
  font: inherit;
}

.application {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

.header {
  padding: 18px 24px;
  color: white;
  background: #17324d;
}

.header h1 {
  margin: 0;
  font-size: 24px;
}

.header p {
  margin: 5px 0 0;
  color: #cbd7e3;
}

.workspace {
  display: grid;
  grid-template-columns: 280px 1fr;
  flex: 1;
  min-height: 0;
}

.sidebar {
  padding: 24px;
  overflow-y: auto;
  background: white;
  border-right: 1px solid #dfe5eb;
}

.sidebar section + section {
  margin-top: 28px;
}

.sidebar h2 {
  margin: 0 0 12px;
  font-size: 16px;
}

.sidebar label {
  display: block;
  margin-bottom: 7px;
  color: #526170;
  font-size: 14px;
}

.sidebar select {
  width: 100%;
  padding: 10px;
  background: white;
  border: 1px solid #cbd5df;
  border-radius: 6px;
}

.functions {
  display: grid;
  gap: 8px;
}

.functions button {
  padding: 10px 12px;
  color: #344454;
  text-align: left;
  cursor: pointer;
  background: #f3f6f8;
  border: 1px solid #dce3e9;
  border-radius: 6px;
}

.functions button.active {
  color: white;
  background: #197278;
  border-color: #197278;
}

.map-container {
  min-width: 0;
  min-height: 500px;
  height: 100%;
  overflow: hidden;
}

.map-loading {
  display: grid;
  place-items: center;
  width: 100%;
  height: 100%;
  min-height: 500px;
  color: #526170;
  background: #e9eef2;
}

@media (max-width: 750px) {
  .workspace {
    grid-template-columns: 1fr;
  }

  .sidebar {
    border-right: 0;
    border-bottom: 1px solid #dfe5eb;
  }

  .map-container {
    height: 65vh;
  }
}
</style>