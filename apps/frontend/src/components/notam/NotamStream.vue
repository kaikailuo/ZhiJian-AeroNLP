<template>
  <section :class="streamSection">
    <div :class="panelTitle">{{ pref.t('stream.title') }}</div>

    <div v-if="runs.length === 0" :class="emptyState">
      <div :class="emptyIcon">📡</div>
      <div>{{ pref.t('stream.awaiting') }}</div>
      <div :class="emptyHint">{{ pref.t('stream.standby') }}</div>
    </div>

    <div v-else :class="streamList">
      <div
        v-for="run in runs"
        :key="run.id"
        :class="runCard"
      >
        <div :class="cardHeader">
          <div :class="headerLeft">
            <span :class="idBadge">#{{ run.id.slice(0, 8) }}</span>
            <span :class="typeBadge">{{ run.type === 'batch' ? 'BATCH JOB' : 'NOTAMN' }}</span>
          </div>
          
          <div :class="statusCapsule(run.stage)">
            <span v-if="isActive(run.stage)" :class="pulseDot"></span>
            <span :class="statusText">{{ formatStatus(run.stage) }}</span>
          </div>
        </div>

        <div :class="cardBody">
          <div v-if="run.type === 'batch' && run.batchProgress" :class="batchContainer">
             <div :class="batchInfo">
                <span>Processing: {{ run.batchProgress.filename }}</span>
                <span>{{ run.batchProgress.current }} / {{ run.batchProgress.total }}</span>
             </div>
             <div :class="progressBarBg">
                <div :class="progressBarFill" :style="{ width: `${(run.batchProgress.current / run.batchProgress.total) * 100}%` }"></div>
             </div>
             
             <div v-if="run.stage === 'finalized'" :class="fieldsGrid" style="margin-top: 12px;">
                <div v-for="(value, key) in run.fields" :key="key" :class="fieldItem">
                  <span :class="fieldKey">{{ key }}</span>
                  <span :class="fieldVal">{{ value }}</span>
                </div>
             </div>
          </div>

          <div v-else>
             <div v-if="Object.keys(run.fields).length === 0 && isActive(run.stage)" :class="skeletonPulse">
                {{ pref.t('stream.processing') }}
             </div>
             <div v-else-if="Object.keys(run.fields).length > 0" :class="fieldsGrid">
               <div v-for="(value, key) in run.fields" :key="key" :class="fieldItem">
                 <span :class="fieldKey">{{ key }}</span>
                 <span :class="fieldVal">{{ value }}</span>
               </div>
             </div>
          </div>
          
          <div v-if="run.alerts.length" :class="alertList">
            <div v-for="alert in run.alerts" :key="alert.id" :class="alertBadge(alert.severity)">
              <span>⚠️ {{ alert.message }}</span>
            </div>
          </div>
        </div>

        <NotamReasoningDrawer
          v-if="run.thoughts.length || run.rawText"
          :items="mapThoughts(run)"
          :is-streaming="isActive(run.stage)"
          :default-open="isActive(run.stage)" 
          :title="run.type === 'batch' ? pref.t('stream.processLog') : pref.t('stream.reasoningChain')"
        />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { css } from "@/styled-system/css";
import { useNotamRunStore, type NotamRun } from "@/stores/notamRunStore";
import NotamReasoningDrawer from "@/components/notam/NotamReasoningDrawer.vue";
import { usePreferenceStore } from "@/stores/preferenceStore";
const pref = usePreferenceStore();

const { runs } = useNotamRunStore();

// Helper: 格式化状态文字
const formatStatus = (stage: string) => {
  switch (stage) {
    case 'discovering': return pref.t('stream.discoveryAgent');
    case 'analyzing': return pref.t('stream.analystAgent');
    case 'validating': return pref.t('stream.validatorAgent');
    case 'finalized': return pref.t('stream.renderCompleted');
    case 'failed': return pref.t('stream.parsingFailed');
    default: return stage.toUpperCase();
  }
};

const isActive = (stage: string) => ['discovering', 'analyzing', 'validating', 'debating'].includes(stage);

const mapThoughts = (run: NotamRun) => {
  // 保持 thoughts 类型兼容
  return run.thoughts.map((t) => ({
    id: t.id,
    agent: t.agent,
    text: t.text,
    isStreaming: t.isStreaming // 传递 streaming 状态
  }));
};

// --- Styles ---

const streamSection = css({ 
  display: "flex", 
  flexDirection: "column", 
  // height: "100%", 
  // overflow: "hidden" 
});
const panelTitle = css({ color: "surface.textDim", fontSize: "10px", fontWeight: "bold", letterSpacing: "1px", mb: "2" });
const streamList = css({
  flex: "1",
  // overflowY: "auto",
  // pr: "2",
  display: "flex",
  flexDirection: "column",
  gap: "4",
  minHeight: "0",
});
const emptyState = css({ textAlign: "center", color: "surface.textDim", mt: "24", fontSize: "sm" });
const emptyIcon = css({ fontSize: "40px", mb: "2", opacity: 0.3 });
const emptyHint = css({ fontSize: "14px", opacity: 0.6, mt: "2" });

const runCard = css({
  bg: "surface.base",
  border: "1px solid token(colors.surface.outline)",
  // borderRadius: "xl",
  borderRadius: "lg", // 稍微减小圆角，显得更硬朗
  overflow: "hidden",
  display: "flex",
  flexDirection: "column",
  boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
  height: "fit-content", // <--- 新增：确保高度适应内容
  mb: "3", // <--- 新增：卡片之间增加一点外部间距
  transition: "all 0.2s ease", // <--- 可选：增加平滑过渡
});

const cardHeader = css({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  p: "3",
  bg: "surface.sunken",
  borderBottom: "1px solid token(colors.surface.outline)",
});
const headerLeft = css({ display: "flex", alignItems: "center", gap: "3" });
// const runId = css({ fontSize: "9px", color: "surface.textDim", fontFamily: "mono" });

const idBadge = css({ fontSize: "12px", fontFamily: "mono", fontWeight: "bold", color: "surface.text" });
const typeBadge = css({ fontSize: "9px", bg: "surface.sunken", color: "surface.textDim", px: "1.5", py: "0.5", borderRadius: "sm", fontWeight: "600" });

// Status Capsule
const statusCapsule = (stage: string) => css({
  display: "flex", alignItems: "center", gap: "2",
  px: "2.5", py: "1", borderRadius: "full",
  fontSize: "9px", fontWeight: "bold", letterSpacing: "0.5px",
  bg: isActive(stage) ? "rgba(26, 116, 255, 0.08)" : (stage === 'finalized' ? "rgba(16, 185, 129, 0.1)" : "surface.sunken"),
  color: isActive(stage) ? "brand.primary" : (stage === 'finalized' ? "green.600" : "surface.textDim"),
  border: isActive(stage) ? "1px solid rgba(26, 116, 255, 0.2)" : "1px solid transparent"
});
const statusText = css({ fontSize: "12px", color: "surface.textDim" });
const pulseDot = css({
  w: "6px", h: "6px", borderRadius: "full", bg: "brand.primary",
  animation: "pulse 1.5s infinite"
});



const cardBody = css({
  p: "3",
  display: "grid",
  gap: "2",
  minHeight: "60px",
});

// [新增] Batch 样式
const batchContainer = css({ display: "flex", flexDirection: "column", gap: "2" });
const batchInfo = css({ display: "flex", justifyContent: "space-between", fontSize: "11px", color: "surface.textDim", fontWeight: "600" });
const progressBarBg = css({ h: "6px", w: "100%", bg: "surface.sunken", borderRadius: "full", overflow: "hidden" });
const progressBarFill = css({ h: "100%", bg: "brand.primary", transition: "width 0.2s ease" });

const skeletonPulse = css({ fontSize: "11px", color: "surface.textDim", fontStyle: "italic", animation: "pulse 2s infinite" });
// const placeholder = css({ color: "surface.textDim", fontSize: "sm" });
const fieldsGrid = css({ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "2" });
const fieldItem = css({ bg: "surface.elevated", borderRadius: "md", p: "2", border: "1px solid token(colors.surface.outline)" });
const fieldKey = css({ display: "block", fontSize: "9px", color: "surface.textDim", mb: "1", textTransform: "uppercase" });
const fieldVal = css({ fontSize: "12px", fontWeight: "bold", color: "surface.text", wordBreak: "break-all" });

const alertList = css({ display: "grid", gap: "2", mt: "1" });
const alertBadge = (severity: string) =>
  css({
    fontSize: "14px",
    fontWeight: "500",
    px: "2",
    py: "1",
    borderRadius: "md",
    border: severity === "critical" ? "1px solid #FCA5A5" : "1px solid #FDE68A",
    bg: severity === "critical" ? "rgba(239,68,68,0.12)" : "rgba(234,179,8,0.12)",
    color: severity === "critical" ? "red.500" : "yellow.500",
    display: "flex",
    gap: "2",
  });

</script>
