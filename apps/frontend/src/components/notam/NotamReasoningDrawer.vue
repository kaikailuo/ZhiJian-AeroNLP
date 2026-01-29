<template>
  <div :class="drawerSection">
    <button @click="toggle" :class="expandControl">
      <span :class="labelStyle">AI REASONING & RAW DATA</span>
      <n-icon :size="14" :class="arrowIconStyle(model.isExpanded)">
        <ChevronDown16Regular />
      </n-icon>
    </button>

    <n-collapse-transition :show="model.isExpanded">
      <div :class="expandedContent">
        <div v-if="model.thoughts.length > 0" :class="logContainer">
          <div v-for="log in model.thoughts" :key="log.id" :class="logItem">
            <span :class="agentTag(log.agent)">{{ log.agent }}</span>
            <span :class="logText">
              {{ log.content }}
              <span v-if="log.isStreaming" :class="cursor">_</span>
            </span>
          </div>
        </div>

        <div :class="rawBox">
          <div :class="rawTitle">ORIGINAL MESSAGE</div>
          <pre :class="rawPre">{{ model.rawText }}</pre>
        </div>
      </div>
    </n-collapse-transition>
  </div>
</template>

<script setup lang="ts">
import { NIcon, NCollapseTransition } from 'naive-ui';
import { ChevronDown16Regular } from '@vicons/fluent';
import { css } from '@/styled-system/css';
import type { NotamCardModel, AgentType } from '@/models/NotamCard';

const props = defineProps<{
  model: NotamCardModel
}>();

const toggle = () => {
  props.model.isExpanded = !props.model.isExpanded;
};

// --- Styles ---

const drawerSection = css({ mt: '1' });

const expandControl = css({
  display: 'flex', alignItems: 'center', gap: '2',
  bg: 'transparent', border: 'none', cursor: 'pointer',
  color: 'surface.textDim', fontSize: '10px', fontWeight: 'bold',
  p: '0', mb: '1',
  _hover: { color: 'brand.primary' }
});

const labelStyle = css({ textTransform: 'uppercase', letterSpacing: '0.05em' });

const arrowIconStyle = (expanded: boolean) => css({
  transition: 'transform 0.2s',
  transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)'
});

const expandedContent = css({
  borderTop: '1px dashed token(colors.surface.outline)',
  pt: '2', mt: '1'
});

const logContainer = css({ display: 'flex', flexDirection: 'column', gap: '1', mb: '3' });
const logItem = css({ display: 'flex', gap: '2', fontSize: '10px', fontFamily: 'mono' });

const agentTag = (agent: AgentType) => css({
  minWidth: '60px', textAlign: 'right', fontWeight: 'bold',
  color: agent === 'DISCOVERY' ? 'blue.500' : (agent === 'ANALYST' ? 'purple.500' : 'green.500')
});

const logText = css({ color: 'surface.text', flex: 1, lineHeight: '1.4' });

const rawBox = css({ 
  bg: 'surface.canvas', p: '2', borderRadius: 'md', 
  border: '1px solid token(colors.surface.outline)' 
});
const rawTitle = css({ fontSize: '9px', color: 'surface.textDim', mb: '1', fontWeight: 'bold' });
const rawPre = css({ 
  fontFamily: 'mono', fontSize: '10px', color: 'surface.textDim', 
  whiteSpace: 'pre-wrap', wordBreak: 'break-all', margin: 0 
});
const cursor = css({ animation: 'blink 1s infinite' });
</script>

<style scoped>
@keyframes blink { 50% { opacity: 0; } }
</style>