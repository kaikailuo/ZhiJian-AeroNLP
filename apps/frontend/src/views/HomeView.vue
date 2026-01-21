<template>
  <div class="page-shell">
    <aside class="side-panel">
      <h1>ZhiJian-AeroNLP</h1>
      <p>航行情报作战舱</p>
      <nav class="nav-list">
        <router-link class="nav-item" to="/">总览</router-link>
        <router-link class="nav-item" to="/notam">NOTAM 中心</router-link>
        <router-link class="nav-item" to="/maps">地理情报</router-link>
        <router-link class="nav-item" to="/routes">航路规划</router-link>
        <router-link class="nav-item" to="/training">训练实验室</router-link>
        <router-link class="nav-item" to="/api-keys">API 密钥库</router-link>
      </nav>
      <div class="side-footer">
        <n-button tertiary block @click="handleLogout">退出登录</n-button>
      </div>
    </aside>
    <main class="main-panel fade-in">
      <header class="page-header">
        <div>
          <h2>任务总览</h2>
          <p>实时情报流与系统健康快照。</p>
        </div>
        <div class="badge">{{ summary.system_status.db }} 数据库</div>
      </header>

      <section class="grid-3">
        <div class="card">
          <p class="card-title">近期 NOTAM</p>
          <div class="stat-value">{{ summary.recent_notam_count }}</div>
          <p class="card-sub">最近一次会话解析数量</p>
        </div>
        <div class="card">
          <p class="card-title">活跃告警</p>
          <div class="stat-value">{{ summary.active_alerts }}</div>
          <p class="card-sub">规则触发中的告警</p>
        </div>
        <div class="card">
          <p class="card-title">待处理任务</p>
          <div class="stat-value">{{ summary.pending_tasks }}</div>
          <p class="card-sub">队列积压情况</p>
        </div>
      </section>

      <section class="grid-2" style="margin-top: 24px">
        <div class="card">
          <div class="card-header">
            <div>
              <h3>解析成功率</h3>
              <p class="card-sub">模型质量指标</p>
            </div>
            <div class="badge">{{ Math.round(summary.parse_success_rate * 100) }}%</div>
          </div>
          <div ref="chartRef" style="height: 220px"></div>
        </div>
        <div class="card">
          <div class="card-header">
            <div>
              <h3>地理地图占位</h3>
              <p class="card-sub">实时空域可视化（MVP）</p>
            </div>
          </div>
          <div class="map-placeholder">
            <div class="map-grid"></div>
            <span>全球地图图层即将接入</span>
          </div>
        </div>
      </section>

      <section class="grid-2" style="margin-top: 24px">
        <div class="card">
          <div class="card-header">
            <h3>告警动态</h3>
            <p class="card-sub">最新规则触发记录</p>
          </div>
          <div class="alert-list">
            <div v-for="alert in summary.alerts" :key="alert.id" class="alert-item">
              <div class="alert-dot"></div>
              <div>
                <strong>{{ alert.message }}</strong>
                <p>{{ alert.created_at }}</p>
              </div>
            </div>
          </div>
        </div>
        <div class="card">
          <div class="card-header">
            <h3>快速入口</h3>
            <p class="card-sub">跳转到建设中的模块</p>
          </div>
          <div class="quick-actions">
            <router-link to="/notam" class="quick-card">NOTAM 解析</router-link>
            <router-link to="/maps" class="quick-card">打开地图</router-link>
            <router-link to="/routes" class="quick-card">航路规划</router-link>
            <router-link to="/training" class="quick-card">训练中心</router-link>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { NButton } from "naive-ui";
import * as echarts from "echarts";
import { dashboardAPI } from "@/services/dashboard";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const auth = useAuthStore();
const chartRef = ref<HTMLDivElement | null>(null);

const summary = ref({
  recent_notam_count: 0,
  active_alerts: 0,
  pending_tasks: 0,
  parse_success_rate: 0,
  system_status: { db: "--" },
  alerts: [] as Array<{ id: number; message: string; created_at: string }>,
});

const fetchSummary = async () => {
  const { data } = await dashboardAPI.summary();
  summary.value = data;
};

const handleLogout = async () => {
  await auth.logout();
  router.push({ name: "login" });
};

onMounted(async () => {
  await fetchSummary();
  if (chartRef.value) {
    const chart = echarts.init(chartRef.value);
    chart.setOption({
      xAxis: {
        type: "category",
        data: ["00Z", "04Z", "08Z", "12Z", "16Z", "20Z"],
        axisLine: { lineStyle: { color: "#8aa0c2" } },
      },
      yAxis: {
        type: "value",
        axisLine: { show: false },
        splitLine: { lineStyle: { color: "#e6ecf5" } },
      },
      series: [
        {
          data: [12, 24, 18, 30, 28, 36],
          type: "line",
          smooth: true,
          lineStyle: { color: "#1a74ff", width: 3 },
          areaStyle: { color: "rgba(26, 116, 255, 0.2)" },
        },
      ],
      grid: { left: 16, right: 16, bottom: 24, top: 20 },
    });
  }
});
</script>

<style scoped>
.nav-list {
  display: grid;
  gap: 10px;
  margin-top: 24px;
}

.nav-item {
  padding: 10px 14px;
  border-radius: 10px;
  color: rgba(223, 231, 255, 0.85);
  font-weight: 500;
  transition: background 0.2s ease;
}

.nav-item.router-link-active {
  background: rgba(26, 116, 255, 0.2);
  color: #ffffff;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.card-title {
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #6b7a94;
}

.card-sub {
  color: #6b7a94;
  font-size: 13px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.map-placeholder {
  height: 220px;
  border-radius: 12px;
  border: 1px dashed rgba(11, 16, 32, 0.2);
  display: grid;
  place-items: center;
  color: #66748c;
  background: linear-gradient(135deg, rgba(26, 116, 255, 0.05), rgba(31, 225, 255, 0.08));
  position: relative;
  overflow: hidden;
}

.map-grid {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(255, 255, 255, 0.2) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.2) 1px, transparent 1px);
  background-size: 24px 24px;
  opacity: 0.3;
}

.alert-list {
  display: grid;
  gap: 12px;
}

.alert-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.alert-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ff8a00;
  margin-top: 6px;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.quick-card {
  padding: 16px;
  border-radius: 12px;
  border: 1px solid rgba(11, 16, 32, 0.1);
  background: rgba(26, 116, 255, 0.08);
  font-weight: 600;
  text-align: center;
}

.side-footer {
  margin-top: 32px;
}

@media (max-width: 960px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .quick-actions {
    grid-template-columns: 1fr;
  }
}
</style>
