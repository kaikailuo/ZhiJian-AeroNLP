<template>
  <section class="map-shell">
    <div class="map-topbar">
      <div class="topbar-left">
        <div class="map-title">地图容器（演示）</div>
        <div class="map-subtitle">
          当前模式：<strong>{{ mode }}</strong> · 图层状态会联动展示（无需真实地图引擎）
        </div>
      </div>

      <div class="topbar-right">
        <!-- 删除：打开面板按钮 -->
        <span class="pill" :data-mode="mode">{{ modeLabel }}</span>
      </div>
    </div>

    <div class="map-canvas" :data-mode="mode">
      <div class="scanlines" aria-hidden="true"></div>
      <div class="grid" aria-hidden="true"></div>

      <svg class="routes" viewBox="0 0 1000 520" preserveAspectRatio="none" aria-hidden="true">
        <path class="route r1" d="M60,380 C240,120 430,140 560,210 C700,285 820,260 950,120" />
        <path class="route r2" d="M80,120 C220,220 320,320 520,300 C680,285 740,210 920,400" />
        <path class="route r3" d="M130,420 C220,380 330,260 430,250 C590,235 640,350 780,360 C880,370 930,330 970,290" />
        <circle class="node" cx="60" cy="380" r="5" />
        <circle class="node" cx="950" cy="120" r="5" />
        <circle class="node" cx="80" cy="120" r="5" />
        <circle class="node" cx="920" cy="400" r="5" />
      </svg>

      <div class="hud">
        <div class="hud-title">演示图层</div>

        <div class="hud-row" v-for="item in hudItems" :key="item.key">
          <span class="dot" :data-on="item.on"></span>
          <span class="label">{{ item.label }}</span>
          <span class="value">{{ item.on ? "ON" : "OFF" }}</span>
        </div>

        <!-- 删除：底部 KPI 三块 -->
      </div>

      <div class="corner-hint">
        提示：拖动按钮可移动；抽拉面板可开关；2D/3D 切换仅演示 UI 与状态联动
      </div>

      <div class="center-tip">
        <div class="center-title">Map Canvas Demo</div>
        <div class="center-desc">
          这是演示底图：后续接入 Leaflet/Mapbox/Cesium 时，只替换 MapContainer 内部实现即可。
        </div>

        <div class="chips" v-if="enabledLabels.length > 0">
          <span class="chip" v-for="label in enabledLabels" :key="label">{{ label }}</span>
        </div>
        <div class="chips" v-else>
          <span class="chip muted">当前开启的功能：（无）</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { GeoIntelFeatures } from "@/views/GeoIntelView.vue";

type MapMode = "2D" | "3D";

const props = defineProps<{
  features: GeoIntelFeatures;
  mode: MapMode;
  drawerOpen: boolean;
}>();

const labels: Record<keyof GeoIntelFeatures, string> = {
  worldChart: "全球航图",
  airspace: "空域限制",
  flightTrack: "航班轨迹",
  weather: "气象叠加",
  mode3d: "3D入口",
  geofence: "地理围栏",
};

const enabledLabels = computed(() => {
  const keys = Object.keys(props.features) as (keyof GeoIntelFeatures)[];
  return keys.filter((k) => props.features[k]).map((k) => labels[k]);
});

const modeLabel = computed(() => (props.mode === "3D" ? "3D（演示）" : "2D（演示）"));

const hudItems = computed(() => {
  const keys = Object.keys(props.features) as (keyof GeoIntelFeatures)[];
  return keys.map((k) => ({
    key: k,
    label: labels[k],
    on: props.features[k],
  }));
});
</script>

<style scoped>
.map-shell {
  border-radius: 16px;
  overflow: hidden;

  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(255, 255, 255, 0.55);
  box-shadow: 0 14px 30px rgba(10, 30, 60, 0.10);
  backdrop-filter: blur(10px);

  min-height: 660px;
}

.map-topbar {
  padding: 12px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;

  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.topbar-left {
  min-width: 260px;
}

.map-title {
  font-weight: 700;
  color: rgba(10, 18, 30, 0.92);
}

.map-subtitle {
  margin-top: 4px;
  font-size: 12px;
  color: rgba(20, 30, 50, 0.62);
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pill {
  font-size: 12px;
  padding: 5px 10px;
  border-radius: 999px;
  border: 1px solid rgba(0, 0, 0, 0.10);
  background: rgba(255, 255, 255, 0.72);
  color: rgba(15, 25, 40, 0.82);
}

.pill[data-mode="3D"] {
  border-color: rgba(0, 170, 255, 0.28);
  box-shadow: 0 0 0 4px rgba(0, 170, 255, 0.10);
}

.map-canvas {
  position: relative;
  min-height: 600px;
  overflow: hidden;
  background:
    radial-gradient(900px 520px at 20% 10%, rgba(0, 180, 255, 0.14), transparent 55%),
    radial-gradient(720px 520px at 85% 16%, rgba(148, 90, 255, 0.12), transparent 60%),
    radial-gradient(900px 650px at 50% 90%, rgba(0, 255, 198, 0.09), transparent 58%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.75), rgba(255, 255, 255, 0.65));
}

.map-canvas[data-mode="3D"] {
  background:
    radial-gradient(900px 520px at 20% 10%, rgba(0, 180, 255, 0.18), transparent 55%),
    radial-gradient(720px 520px at 85% 16%, rgba(148, 90, 255, 0.16), transparent 60%),
    radial-gradient(900px 650px at 50% 90%, rgba(0, 255, 198, 0.12), transparent 58%),
    linear-gradient(180deg, rgba(245, 252, 255, 0.85), rgba(255, 255, 255, 0.65));
}

.scanlines {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.02),
    rgba(0, 0, 0, 0.02) 1px,
    transparent 1px,
    transparent 7px
  );
  opacity: 0.35;
}

.grid {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(to right, rgba(0, 0, 0, 0.04) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(0, 0, 0, 0.04) 1px, transparent 1px);
  background-size: 60px 60px;
  opacity: 0.25;
}

.routes {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0.65;
}

.route {
  fill: none;
  stroke-width: 2.6;
  stroke-linecap: round;
  stroke-dasharray: 6 10;
  animation: dash 6s linear infinite;
}
.r1 {
  stroke: rgba(0, 140, 255, 0.75);
}
.r2 {
  stroke: rgba(0, 255, 198, 0.60);
  animation-duration: 7.5s;
}
.r3 {
  stroke: rgba(148, 90, 255, 0.55);
  animation-duration: 8.2s;
}

.node {
  fill: rgba(0, 140, 255, 0.9);
  stroke: rgba(255, 255, 255, 0.85);
  stroke-width: 2;
  filter: drop-shadow(0 6px 8px rgba(0, 140, 255, 0.20));
}

@keyframes dash {
  to {
    stroke-dashoffset: -120;
  }
}

/* HUD */
.hud {
  position: absolute;
  right: 14px;
  top: 14px;
  width: 260px;

  border-radius: 16px;
  padding: 12px;

  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(255, 255, 255, 0.55);
  box-shadow: 0 14px 24px rgba(10, 30, 60, 0.12);
  backdrop-filter: blur(10px);
}

.hud-title {
  font-size: 13px;
  font-weight: 700;
  color: rgba(10, 18, 30, 0.92);
  margin-bottom: 10px;
}

.hud-row {
  display: grid;
  grid-template-columns: 10px 1fr auto;
  align-items: center;
  gap: 8px;

  padding: 7px 8px;
  border-radius: 12px;

  border: 1px solid rgba(0, 0, 0, 0.05);
  background: rgba(255, 255, 255, 0.65);
  margin-bottom: 8px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.15);
}
.dot[data-on="true"] {
  background: rgba(0, 170, 255, 0.90);
  box-shadow: 0 0 0 4px rgba(0, 170, 255, 0.12);
}

.label {
  font-size: 12px;
  color: rgba(15, 25, 40, 0.82);
}

.value {
  font-size: 12px;
  font-weight: 700;
  color: rgba(15, 25, 40, 0.60);
}

.corner-hint {
  position: absolute;
  left: 14px;
  top: 14px;
  max-width: 560px;

  font-size: 12px;
  color: rgba(20, 30, 50, 0.58);

  background: rgba(255, 255, 255, 0.60);
  border: 1px solid rgba(255, 255, 255, 0.55);
  border-radius: 999px;
  padding: 7px 10px;

  backdrop-filter: blur(10px);
}

.center-tip {
  position: absolute;
  left: 14px;
  bottom: 14px;
  right: 290px;

  border-radius: 16px;
  padding: 12px 14px;

  background: rgba(255, 255, 255, 0.70);
  border: 1px solid rgba(255, 255, 255, 0.55);
  box-shadow: 0 14px 24px rgba(10, 30, 60, 0.10);
  backdrop-filter: blur(10px);
}

.center-title {
  font-size: 13px;
  font-weight: 800;
  color: rgba(10, 18, 30, 0.92);
}

.center-desc hookup
.center-desc {
  margin-top: 4px;
  font-size: 12px;
  color: rgba(20, 30, 50, 0.62);
  line-height: 1.45;
}

.chips {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  font-size: 12px;
  padding: 5px 10px;
  border-radius: 999px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: rgba(255, 255, 255, 0.70);
  color: rgba(15, 25, 40, 0.80);
}
.chip.muted {
  color: rgba(15, 25, 40, 0.55);
}
</style>
