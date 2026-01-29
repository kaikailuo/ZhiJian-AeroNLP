<template>
  <div :class="cardContainer">
    <div :class="cx(stripBase, stripColorClasses[notam.data.severity] || stripColorClasses.info)"></div>

    <div :class="mainContent">
      
      <div :class="headerRow">
        <div :class="idGroup">
          <n-icon :size="18" :class="headerIconClass(notam.data.severity)">
            <component :is="severityConfig[notam.data.severity]?.icon" />
          </n-icon>
          
          <span :class="airportBadge">{{ notam.airportCode }}</span>
          
          <div :class="idWrapper">
            <span :class="idSeries">{{ notam.data.identifier?.split('/')[0] || 'Pending' }}</span>
            <span :class="idYear">/{{ notam.data.identifier?.split('/')[1] || '..' }}</span>
          </div>
        </div>
        
        <div :class="headerRightActions">
            <button :class="historyBtn" title="History Search">
                <n-icon :component="History16Regular" />
            </button>
            
            <div :class="statusBadgeStyle">
               <span v-if="shouldPulse" class="pulsing-dot"></span>
               {{ localizedStatus }}
            </div>
        </div>
      </div>

      <div :class="bodySection">
        
        <div v-if="notam.data.summary" :class="summaryBox(notam.data.severity)">
          <div :class="summaryIconWrapper(notam.data.severity)">
             <n-icon :size="18">
                <component :is="severityConfig[notam.data.severity]?.icon" />
             </n-icon>
          </div>
          <div :class="summaryContent">{{ notam.data.summary }}</div>
        </div>
        
        <div v-if="notam.data.tags.length" :class="tagsRow">
          <span v-for="tag in notam.data.tags" :key="tag" :class="tagStyle">#{{ tag }}</span>
        </div>

        <NotamReasoningBar :model="notam" />
        <NotamRawViewer :text="notam.rawText" />

      </div>

      <div :class="footerRow">
        <div :class="confidenceGroup" title="AI Confidence Score">
          <div :class="confidenceDot(notam.data.confidence > 80)"></div>
          <span>{{ pref.t('status.confidence') }}: {{ notam.data.confidence || 0 }}%</span>
        </div>

        <div :class="actionsGroup">
          <button :class="actionBtn" title="Locate on Map" @click="handleLocate">
             <n-icon :component="Location16Regular" />
             <span>{{ pref.t('action.locate') }}</span>
          </button>
          <button :class="actionBtn" title="Human Correction">
             <n-icon :component="Edit16Regular" />
             <span>{{ pref.t('action.fix') }}</span>
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { css, cx } from "@/styled-system/css";
import { NotamCardModel, AgentType, NotamStage, TimeStatus } from "@/models/NotamCard";
import { NIcon } from "naive-ui";
import NotamReasoningBar from './NotamReasoningBar.vue';
import NotamRawViewer from './NotamRawViewer.vue';
import { useNotamRunStore } from '@/stores/notamRunStore'; // [新增] 引入 Store
import { usePreferenceStore } from '@/stores/preferenceStore'; // [新增]
// 引入 Fluent Icons (看起来更像仪表盘)
import {
  Warning24Filled,
  ErrorCircle24Filled,
  Info24Regular,
  CheckmarkCircle24Regular,
  Location16Regular,
  Edit16Regular,
  ChevronRight16Regular,
  History16Regular,
} from "@vicons/fluent";

const props = defineProps<{
  notam: NotamCardModel;
}>();
const store = useNotamRunStore();
const pref = usePreferenceStore(); // [新增]

// [配置] 严重性配置：映射到组件对象
const severityConfig: Record<string, { icon: any }> = {
  critical: { icon: ErrorCircle24Filled },
  warning: { icon: Warning24Filled },
  info: { icon: Info24Regular },
  active: { icon: CheckmarkCircle24Regular },
};

const processingStages: readonly NotamStage[] = [
  NotamStage.CONNECTING,
  NotamStage.DISCOVERING,
  NotamStage.ANALYZING,
  NotamStage.VALIDATING,
];

const isProcessing = computed(() => processingStages.includes(props.notam.stage));

// [新增] 本地化状态文本
const localizedStatus = computed(() => {
  if (isProcessing.value) {
    // 映射到 status.stage.analyzing 等
    return pref.t(`status.stage.${props.notam.stage}`);
  }
  if (props.notam.stage === NotamStage.FAILED) {
    return pref.t('status.stage.failed');
  }
  
  // 映射到 status.time.active 等
  const ts = props.notam.timeStatus || TimeStatus.UNKNOWN;
  return pref.t(`status.time.${ts}`).toUpperCase(); // 英文时保持大写风格，中文时 .toUpperCase 不影响
});

const shouldPulse = computed(() => {
  if (isProcessing.value) return true;
  return props.notam.timeStatus === TimeStatus.ACTIVE;
});

const handleLocate = () => {
  if (props.notam.airportCode && props.notam.airportCode !== 'PENDING') {
    store.updateGrounding(props.notam.airportCode);
    // 这里其实不需要手动做别的，Radar 组件监听了 store.currentGrounding，会自动变
  }
};

// --- CSS Styles (Panda) ---
const cardContainer = css({
  position: "relative",
  display: "flex",
  bg: "surface.base",
  borderRadius: "lg",
  border: "1px solid token(colors.surface.outline)",
  overflow: "hidden",
  transitionProperty: 'box-shadow, transform, border-color', 
  transitionDuration: '0.2s',
  mb: "3", // 卡片间距
  _hover: {
    boxShadow: "0 12px 24px -10px rgba(0, 0, 0, 0.15)", // 更柔和的投影
    transform: "scale(1.005)", // 极微小的放大，营造"浮起"感但位置不变
    borderColor: "brand.primary", // 边框高亮
  },
});

// [修改] 修复左边条：拆分为 Base 和 Variants
const stripBase = css({
  width: "4px",
  flexShrink: 0,
  alignSelf: "stretch", // 确保高度撑满
});

// 4. 动态样式计算
const statusBadgeStyle = computed(() => {
  // 默认样式 (处理中)
  let bg = 'rgba(26, 116, 255, 0.1)'; // Brand Blue
  let color = 'brand.primary';

  if (!isProcessing.value) {
    switch (props.notam.timeStatus) {
      case TimeStatus.ACTIVE:
        bg = 'rgba(16, 185, 129, 0.1)'; // Green
        color = 'status.active';
        break;
      case TimeStatus.PENDING:
        bg = 'rgba(245, 158, 11, 0.1)'; // Amber/Orange
        color = 'status.warning';
        break;
      case TimeStatus.EXPIRED:
        bg = 'surface.sunken';          // Gray
        color = 'surface.textDim';
        break;
      case TimeStatus.PERM:
        bg = 'rgba(124, 58, 237, 0.1)'; // Purple
        color = '#7c3aed';              // Hardcoded purple for PERM
        break;
    }
  }

  return css({
    fontSize: '9px', fontWeight: 'bold', px: '2', py: '0.5', borderRadius: 'full',
    display: 'flex', alignItems: 'center', gap: '3px',
    bg, 
    color,
    transition: 'all 0.3s' // 状态切换时平滑过渡
  });
});

// [关键] Panda 是编译时工具，不能在 css() 里放变量，必须预先写死 key
const stripColorClasses: Record<string, string> = {
  critical: css({ bg: "status.critical" }),
  warning: css({ bg: "status.warning" }),
  info: css({ bg: "status.info" }),
  active: css({ bg: "status.active" }),
  expired: css({ bg: "status.expired" }),
};

const mainContent = css({
  flex: 1,
  p: "2.5",
  display: "flex",
  flexDirection: "column",
  gap: "2",
});

const headerRow = css({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
});

const idGroup = css({ display: "flex", alignItems: "center", gap: "2" });

const headerRightActions = css({
  display: "flex",
  alignItems: "center",
  gap: "2",
});

const historyBtn = css({
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  color: "surface.textDim",
  bg: "transparent",
  border: "none",
  cursor: "pointer",
  p: "1",
  borderRadius: "md",
  _hover: { bg: "surface.sunken", color: "brand.primary" },
});

// [新增] Header Icon 颜色映射
const headerIconClass = (s: string) => css({ 
  display: 'flex',
  color: s === 'critical' ? 'status.critical' : 
         s === 'warning'  ? 'status.warning' : 
         s === 'active'   ? 'status.active' : 'brand.primary' 
});

const airportBadge = css({
  fontFamily: "mono",
  fontWeight: "bold",
  fontSize: "xs",
  bg: "surface.sunken",
  px: "1.5",
  py: "0.5",
  borderRadius: "md",
  color: "surface.text",
});

const idWrapper = css({
  fontFamily: "mono",
  fontSize: "sm",
  lineHeight: "1",
  display: "flex",
  alignItems: "baseline",
});
const idSeries = css({ fontWeight: "bold", color: "brand.primary" });
const idYear = css({ fontSize: "xs", color: "surface.textDim" });
const timeBadge = (stage: NotamStage) => {
  const isWorking = processingStages.includes(stage);
  return css({
    fontSize: '9px', fontWeight: 'bold', px: '2', py: '0.5', borderRadius: 'full',
    display: 'flex', alignItems: 'center', gap: '3px',
    // 动态颜色：工作中是蓝色背景，完成后是绿色背景
    bg: isWorking ? 'rgba(26, 116, 255, 0.1)' : 'rgba(16, 185, 129, 0.1)',
    color: isWorking ? 'brand.primary' : 'status.active'
  });
};
// [重构] 摘要容器样式：根据严重性改变背景色
const summaryBox = (severity: string) =>
  css({
    display: "flex",
    gap: "2",
    p: "2",
    borderRadius: "md",
    fontSize: "13px",
    lineHeight: "1.4",
    fontWeight: "500",
    border: "1px solid", // 加上边框增强界限感

    // 动态配色方案
    bg:
      severity === "critical"
        ? "rgba(239, 68, 68, 0.08)" // Red-500 8%
        : severity === "warning"
          ? "rgba(245, 158, 11, 0.08)" // Amber-500 8%
          : "surface.sunken",

    borderColor:
      severity === "critical"
        ? "rgba(239, 68, 68, 0.2)"
        : severity === "warning"
          ? "rgba(245, 158, 11, 0.2)"
          : "token(colors.surface.outline)",

    color: "surface.text",
  });

const summaryIconWrapper = (s:string) => css({ 
  pt:'1px', 
  color: s === 'critical' ? 'status.critical' : 
         s === 'warning'  ? 'status.warning' : 
         s === 'active'   ? 'status.active' : 'brand.primary' 
});

const summaryContent = css({
  flex: 1,
});

const bodySection = css({
  display: "flex",
  flexDirection: "column",
  gap: "2",
});

const tagsRow = css({ display: "flex", flexWrap: "wrap", gap: "2" });
const tagStyle = css({
  fontSize: "10px",
  color: "brand.primary",
  bg: "surface.sunken", // 使用 sunken 代替之前的 rgba 硬编码
  border: "1px solid token(colors.surface.outline)",
  px: "1.5",
  borderRadius: "sm",
});

// [新增] Footer 样式
const footerRow = css({
  display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: '1', pt: '2',
  borderTop: '1px dashed token(colors.surface.outline)',
  opacity: 0.9
});

const confidenceGroup = css({ display: 'flex', alignItems: 'center', gap: '1.5', fontSize: '11px', color: 'surface.textDim' });
const confidenceDot = (high: boolean) => css({
  w: '4px', h: '4px', borderRadius: 'full',
  bg: high ? 'status.active' : 'status.warning'
});

const actionsGroup = css({ display: 'flex', gap: '2' });
const actionBtn = css({
  fontSize: '11px', bg: 'transparent', 
  border: '1px solid token(colors.surface.outline)',
  color: 'surface.textDim', px: '2', py: '1', borderRadius: 'md', cursor: 'pointer',
  display: 'flex', alignItems: 'center', gap: '1',
  _hover: { bg: 'surface.sunken', borderColor: 'brand.primary', color: 'brand.primary' }
});

</script>

<style scoped>
/* 使用 CSS 变量来获取 Panda 生成的颜色值，支持主题切换 */
.pulsing-dot {
  width: 6px;
  height: 6px;
  background: var(--colors-status-active);
  /* 对应 status.active */
  border-radius: 50%;
  box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.4);
  /* 这里暂时可以保留 RGBA 做阴影，或者用 Token */
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 var(--colors-status-active);
    opacity: 1;
  }

  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(0, 0, 0, 0);
    opacity: 0;
  }

  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(0, 0, 0, 0);
    opacity: 1;
  }
}
</style>
