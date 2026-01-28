<template>
  <div class="geo-page">
    <header class="hero">
      <div class="hero-left">
        <h1 class="title">地图可视化</h1>
        <p class="subtitle">前端</p>

        <div class="hero-actions">
          <button class="btn btn-primary" @click="goHome">
            <span class="btn-dot" aria-hidden="true"></span>
            返回总览
          </button>
        </div>
      </div>

      <div class="hero-right">
        <button class="btn btn-ghost" @click="toggleMode">
          <span class="cube" aria-hidden="true"></span>
          2D / 3D 切换
        </button>
      </div>

      <div class="hero-glow-line" aria-hidden="true"></div>
    </header>

    <main class="content">
      <button
        class="drawer-toggle"
        :style="drawerToggleStyle"
        @pointerdown="onTogglePointerDown"
        @click="onToggleClick"
      >
        <span class="drawer-toggle-icon" aria-hidden="true"></span>
        {{ drawerOpen ? "收起面板" : "展开面板" }}
        <span class="drag-hint" aria-hidden="true">拖动</span>
      </button>

      <div class="drawer" :data-open="drawerOpen" :style="drawerStyle" @pointerdown.stop>
        <LayerPanel
          :features="features"
          @toggle="handleToggle"
          @toggleAll="handleToggleAll"
          @reset="handleReset"
          @collapse="drawerOpen = false"
          @dragStart="onPanelDragStart"
        />
      </div>

      <MapContainer :features="features" :mode="mode" :drawerOpen="drawerOpen" />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import LayerPanel from "@/components/geo-intel/LayerPanel.vue";
import MapContainer from "@/components/geo-intel/MapContainer.vue";
import { mapsAPI } from "@/services/maps";

type FeatureKey = "worldChart" | "airspace" | "flightTrack" | "weather" | "mode3d" | "geofence";
export type GeoIntelFeatures = Record<FeatureKey, boolean>;
type MapMode = "2D" | "3D";

const router = useRouter();
const goHome = () => router.push("/");

const defaultFeatures: GeoIntelFeatures = {
  worldChart: true,
  airspace: false,
  flightTrack: false,
  weather: false,
  mode3d: false,
  geofence: false,
};

const features = reactive<GeoIntelFeatures>({ ...defaultFeatures });
const drawerOpen = ref(true);

const mode = ref<MapMode>("2D");
const toggleMode = () => {
  mode.value = mode.value === "2D" ? "3D" : "2D";
  features.mode3d = mode.value === "3D";
};

const handleToggle = (key: FeatureKey, value: boolean) => {
  features[key] = value;
  if (key === "mode3d") mode.value = value ? "3D" : "2D";
};

const handleToggleAll = (value: boolean) => {
  (Object.keys(features) as FeatureKey[]).forEach((k) => (features[k] = value));
  mode.value = features.mode3d ? "3D" : "2D";
};

const handleReset = () => {
  (Object.keys(features) as FeatureKey[]).forEach((k) => (features[k] = defaultFeatures[k]));
  mode.value = features.mode3d ? "3D" : "2D";
};

const TOGGLE_POS_KEY = "geoIntel.group.togglePos.v1";
const PANEL_POS_KEY = "geoIntel.group.panelPos.v1";

const togglePos = reactive({ left: 10, top: 180 });
const panelPos = reactive({ left: 24, top: 240 });

type DragSource = "toggle" | "panel" | null;
const dragSource = ref<DragSource>(null);

let startPointer = { x: 0, y: 0 };
let startToggle = { left: 0, top: 0 };
let startPanel = { left: 0, top: 0 };

let moved = false;

const loadPos = () => {
  try {
    const rawT = localStorage.getItem(TOGGLE_POS_KEY);
    if (rawT) {
      const t = JSON.parse(rawT);
      if (typeof t?.left === "number" && typeof t?.top === "number") {
        togglePos.left = t.left;
        togglePos.top = t.top;
      }
    }
  } catch {}

  try {
    const rawP = localStorage.getItem(PANEL_POS_KEY);
    if (rawP) {
      const p = JSON.parse(rawP);
      if (typeof p?.left === "number" && typeof p?.top === "number") {
        panelPos.left = p.left;
        panelPos.top = p.top;
      }
    }
  } catch {}
};

const savePos = () => {
  try {
    localStorage.setItem(TOGGLE_POS_KEY, JSON.stringify({ left: togglePos.left, top: togglePos.top }));
  } catch {}
  try {
    localStorage.setItem(PANEL_POS_KEY, JSON.stringify({ left: panelPos.left, top: panelPos.top }));
  } catch {}
};

const beginDrag = (source: DragSource, e: PointerEvent) => {
  dragSource.value = source;
  moved = false;

  startPointer = { x: e.clientX, y: e.clientY };
  startToggle = { left: togglePos.left, top: togglePos.top };
  startPanel = { left: panelPos.left, top: panelPos.top };

  (e.currentTarget as HTMLElement | null)?.setPointerCapture?.(e.pointerId);

  window.addEventListener("pointermove", onDragMove, { passive: false });
  window.addEventListener("pointerup", onDragUp);
};

const onDragMove = (e: PointerEvent) => {
  if (!dragSource.value) return;
  e.preventDefault();

  const dx = e.clientX - startPointer.x;
  const dy = e.clientY - startPointer.y;

  if (Math.abs(dx) + Math.abs(dy) > 4) moved = true;

  togglePos.left = startToggle.left + dx;
  togglePos.top = startToggle.top + dy;

  panelPos.left = startPanel.left + dx;
  panelPos.top = startPanel.top + dy;
};

const onDragUp = () => {
  if (!dragSource.value) return;
  dragSource.value = null;

  window.removeEventListener("pointermove", onDragMove);
  window.removeEventListener("pointerup", onDragUp);

  savePos();
};

const onTogglePointerDown = (e: PointerEvent) => {
  beginDrag("toggle", e);
};

const onToggleClick = () => {
  if (moved) return;
  drawerOpen.value = !drawerOpen.value;
};

const onPanelDragStart = (e: PointerEvent) => {
  beginDrag("panel", e);
};

const drawerToggleStyle = computed(() => ({
  left: `${togglePos.left}px`,
  top: `${togglePos.top}px`,
}));

const drawerStyle = computed(() => ({
  left: `${panelPos.left}px`,
  top: `${panelPos.top}px`,
}));

onMounted(() => {
  loadPos();

  //  API 接口
  mapsAPI.summary().catch(() => {});
});

onBeforeUnmount(() => {
  window.removeEventListener("pointermove", onDragMove);
  window.removeEventListener("pointerup", onDragUp);
});
</script>

<style scoped>
.geo-page {
  padding: 16px;
  min-height: 100%;
  position: relative;
}

.geo-page::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(900px 520px at 16% 8%, rgba(0, 180, 255, 0.18), transparent 60%),
    radial-gradient(780px 520px at 86% 10%, rgba(148, 90, 255, 0.16), transparent 62%),
    radial-gradient(900px 700px at 52% 92%, rgba(0, 255, 198, 0.10), transparent 58%);
}

.hero {
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  padding: 18px 18px 14px;
  border-radius: 16px;

  background: rgba(255, 255, 255, 0.74);
  border: 1px solid rgba(255, 255, 255, 0.55);
  box-shadow:
    0 14px 32px rgba(10, 30, 60, 0.08),
    0 1px 0 rgba(255, 255, 255, 0.58) inset;
  backdrop-filter: blur(10px);
}

.hero::after {
  content: "";
  position: absolute;
  inset: -2px;
  border-radius: 18px;
  padding: 2px;
  background: linear-gradient(
    110deg,
    rgba(0, 170, 255, 0.25),
    rgba(160, 110, 255, 0.18),
    rgba(0, 255, 198, 0.18)
  );
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.hero-glow-line {
  position: absolute;
  left: -20%;
  right: -20%;
  bottom: -1px;
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(0, 150, 255, 0.45),
    rgba(0, 255, 198, 0.35),
    transparent
  );
  filter: blur(0.2px);
}

.hero-left {
  min-width: 320px;
}

.title {
  margin: 0;
  font-size: 26px;
  letter-spacing: 0.2px;
  color: rgba(10, 18, 30, 0.92);
}

.subtitle {
  margin: 8px 0 0;
  color: rgba(20, 30, 50, 0.62);
  font-size: 13px;
}

.hero-actions {
  margin-top: 12px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.hero-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.btn {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  padding: 10px 14px;
  cursor: pointer;
  font-size: 13px;
  transition: transform 120ms ease, box-shadow 120ms ease, background 120ms ease;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  user-select: none;
}

.btn:active {
  transform: translateY(1px);
}

.btn-primary {
  color: white;
  border: 0;
  background: linear-gradient(135deg, rgba(0, 140, 255, 0.95), rgba(130, 70, 255, 0.95));
  box-shadow: 0 12px 20px rgba(60, 80, 220, 0.22);
}

.btn-primary:hover {
  box-shadow: 0 16px 28px rgba(60, 80, 220, 0.28);
}

.btn-ghost {
  color: rgba(15, 25, 40, 0.82);
  background: rgba(255, 255, 255, 0.65);
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 10px 18px rgba(10, 30, 60, 0.1);
}

.btn-ghost:hover {
  box-shadow: 0 14px 24px rgba(10, 30, 60, 0.14);
}

.btn-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.14);
}

.cube {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  background: linear-gradient(135deg, rgba(0, 140, 255, 0.95), rgba(0, 255, 198, 0.85));
  box-shadow: 0 0 0 3px rgba(0, 140, 255, 0.12);
  position: relative;
}
.cube::after {
  content: "";
  position: absolute;
  inset: 3px;
  border-radius: 3px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.65), rgba(255, 255, 255, 0.05));
}

.content {
  position: relative;
  margin-top: 12px;
  min-height: calc(100vh - 170px);
}

.drawer-toggle {
  position: fixed;
  z-index: 70;

  display: inline-flex;
  align-items: center;
  gap: 8px;

  border-radius: 999px;
  padding: 10px 12px;
  cursor: grab;

  border: 1px solid rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.75);
  box-shadow: 0 10px 18px rgba(10, 30, 60, 0.1);
  backdrop-filter: blur(10px);

  font-size: 12px;
  color: rgba(15, 25, 40, 0.85);
  user-select: none;
  touch-action: none;
}

.drawer-toggle:active {
  cursor: grabbing;
}

.drawer-toggle-icon {
  width: 14px;
  height: 14px;
  border-radius: 5px;
  background: linear-gradient(135deg, rgba(0, 140, 255, 0.95), rgba(130, 70, 255, 0.95));
  box-shadow: 0 0 0 3px rgba(120, 90, 255, 0.12);
}

.drag-hint {
  margin-left: 6px;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 11px;
  color: rgba(15, 25, 40, 0.55);
  border: 1px dashed rgba(0, 0, 0, 0.12);
  background: rgba(255, 255, 255, 0.55);
}

.drawer {
  position: fixed;
  z-index: 80;
  width: 320px;
  max-width: calc(100vw - 40px);

  transform: translateX(-110%);
  opacity: 0;
  transition: transform 180ms ease, opacity 180ms ease;

  pointer-events: none;
}

.drawer[data-open="true"] {
  transform: translateX(0);
  opacity: 1;
  pointer-events: auto;
}
</style>
