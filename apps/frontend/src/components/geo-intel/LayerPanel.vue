<template>
  <section class="panel" @pointerdown.stop>
    <!-- 标题栏：拖动手柄 -->
    <div class="panel-header" @pointerdown="emitDragStart">
      <div class="header-left">
        <div class="panel-title">演示图层</div>
        <div class="panel-subtitle">拖动此处可移动面板</div>
      </div>

      <!-- ✅ 已删除：收起按钮 -->
      <!-- <div class="header-actions">
        <button class="mini-btn" @click.stop="$emit('collapse')" title="收起面板">
          收起
        </button>
      </div> -->
    </div>

    <div class="panel-body">
      <div class="items">
        <label class="item" v-for="it in items" :key="it.key">
          <span class="item-left">
            <span class="dot" :data-on="features[it.key]"></span>
            <span class="name">{{ it.label }}</span>
          </span>

          <button
            class="switch"
            :data-on="features[it.key]"
            @click.prevent="onToggle(it.key, !features[it.key])"
          >
            <span class="knob"></span>
            <span class="state">{{ features[it.key] ? "ON" : "OFF" }}</span>
          </button>
        </label>
      </div>

      <div class="actions">
        <!-- ✅ 全开/全关合并按钮（自动判断当前状态）
             ✅ 只针对 items 里的功能，不包含 mode3d（已从面板移除） -->
        <button class="btn btn-soft" @click="toggleAllOneBtn">
          {{ allOn ? "全关" : "全开" }}
        </button>

        <button class="btn btn-ghost" @click="$emit('reset')">重置</button>
      </div>

      <div class="tip">提示：面板可拖动；全开/全关会自动判断当前状态。</div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { GeoIntelFeatures } from "@/views/GeoIntelView.vue";

type FeatureKey = keyof GeoIntelFeatures;

const props = defineProps<{
  features: GeoIntelFeatures;
}>();

const emit = defineEmits<{
  (e: "toggle", key: FeatureKey, value: boolean): void;
  (e: "reset"): void;
  (e: "dragStart", ev: PointerEvent): void;
}>();

/**
 * ✅ 面板里删除 3D 入口：这里不包含 mode3d
 */
const items = [
  { key: "worldChart" as const, label: "全球航图" },
  { key: "airspace" as const, label: "空域限制" },
  { key: "flightTrack" as const, label: "航班轨迹" },
  { key: "weather" as const, label: "气象叠加" },
  { key: "geofence" as const, label: "地理围栏" },
];

const onToggle = (key: FeatureKey, value: boolean) => {
  emit("toggle", key, value);
};

const allOn = computed(() => items.every((it) => !!props.features[it.key]));

const toggleAllOneBtn = () => {
  const next = !allOn.value;
  items.forEach((it) => emit("toggle", it.key, next));
};

const emitDragStart = (e: PointerEvent) => {
  emit("dragStart", e);
};
</script>

<style scoped>
.panel {
  width: 320px;
  border-radius: 16px;
  overflow: hidden;

  background: rgba(255, 255, 255, 0.74);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 18px 30px rgba(10, 30, 60, 0.14);
  backdrop-filter: blur(10px);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;

  padding: 12px 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);

  cursor: grab;
  user-select: none;
  touch-action: none;

  background: linear-gradient(
    135deg,
    rgba(0, 170, 255, 0.1),
    rgba(130, 70, 255, 0.08),
    rgba(0, 255, 198, 0.07)
  );
}

.panel-header:active {
  cursor: grabbing;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.panel-title {
  font-weight: 800;
  color: rgba(10, 18, 30, 0.92);
  font-size: 13px;
}

.panel-subtitle {
  font-size: 11px;
  color: rgba(20, 30, 50, 0.56);
}

.header-actions {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.mini-btn {
  border: 1px solid rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.75);
  border-radius: 10px;
  padding: 6px 10px;
  cursor: pointer;
  font-size: 12px;
  transition: transform 120ms ease, box-shadow 120ms ease;
}

.mini-btn:active {
  transform: translateY(1px);
}

.mini-btn:hover {
  box-shadow: 0 10px 16px rgba(10, 30, 60, 0.12);
}

.panel-body {
  padding: 12px;
}

.items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;

  padding: 10px 10px;
  border-radius: 14px;

  border: 1px solid rgba(0, 0, 0, 0.06);
  background: rgba(255, 255, 255, 0.62);
}

.item-left {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.15);
}

.dot[data-on="true"] {
  background: rgba(0, 170, 255, 0.9);
  box-shadow: 0 0 0 4px rgba(0, 170, 255, 0.12);
}

.name {
  font-size: 12px;
  color: rgba(15, 25, 40, 0.86);
}

.switch {
  border: 1px solid rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.72);
  border-radius: 999px;
  padding: 6px 10px;
  cursor: pointer;

  display: inline-flex;
  align-items: center;
  gap: 8px;

  transition: box-shadow 120ms ease, transform 120ms ease;
}

.switch:hover {
  box-shadow: 0 10px 16px rgba(10, 30, 60, 0.1);
}

.switch:active {
  transform: translateY(1px);
}

.switch .knob {
  width: 18px;
  height: 18px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.12);
  transition: transform 150ms ease, background 150ms ease;
}

.switch[data-on="true"] .knob {
  background: linear-gradient(135deg, rgba(0, 140, 255, 0.95), rgba(0, 255, 198, 0.85));
  transform: translateX(10px);
}

.state {
  font-size: 12px;
  font-weight: 800;
  color: rgba(15, 25, 40, 0.62);
}

.actions {
  margin-top: 12px;
  display: flex;
  gap: 10px;
}

.btn {
  flex: 1;
  border-radius: 12px;
  padding: 10px 12px;
  cursor: pointer;
  font-size: 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  transition: transform 120ms ease, box-shadow 120ms ease;
}

.btn:active {
  transform: translateY(1px);
}

.btn-soft {
  background: linear-gradient(135deg, rgba(0, 140, 255, 0.18), rgba(130, 70, 255, 0.16));
}

.btn-ghost {
  background: rgba(255, 255, 255, 0.7);
}

.btn:hover {
  box-shadow: 0 12px 18px rgba(10, 30, 60, 0.1);
}

.tip {
  margin-top: 10px;
  font-size: 11px;
  color: rgba(20, 30, 50, 0.56);
}
</style>
