<template>
  <div class="page-shell">
    <SideNav />

    <main 
      class="main-panel fade-in" 
      :class="css({
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        boxSizing: 'border-box',
        bg: 'surface.base',
        transition: 'background 0.3s, color 0.3s',
        // 集成滚动条样式
        '& ::-webkit-scrollbar': { width: '6px', height: '6px' },
        '& ::-webkit-scrollbar-track': { bg: 'transparent' },
        '& ::-webkit-scrollbar-thumb': { bg: 'surface.outlineStrong', borderRadius: '9999px' },
        '& ::-webkit-scrollbar-thumb:hover': { bg: 'surface.textDim' },
        scrollbarWidth: 'thin',
        scrollbarColor: 'token(colors.surface.outlineStrong) transparent'
      })"
    >
      <header 
        :class="css({
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          h: '56px',
          flexShrink: 0,
          mb: '4',
          px: '2'
        })"
      >
        <div 
          :class="css({
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'flex-start',
            gap: '0'
          })"
        >
          <h2 
            :class="css({ 
              fontSize: 'lg', 
              fontWeight: 'bold', 
              color: 'surface.text',
              letterSpacing: 'tight',
              lineHeight: '0' 
            })"
          >
            {{ pref.t("app.title") }}
          </h2>
          <p 
            :class="css({ 
              color: 'surface.textDim', 
              fontSize: 'xs',
              fontFamily: 'mono',
              opacity: 0.8,
              lineHeight: '0'
            })"
          >
            {{ pref.t("app.subtitle") }}
          </p>
        </div>

        <div 
          :class="css({
            display: 'flex',
            alignItems: 'center',
            gap: '3',
            bg: 'surface.sunken',
            p: '1',
            borderRadius: 'lg',
            border: '1px solid token(colors.surface.outline)'
          })"
        >
          <div 
            :class="css({
              position: 'relative',
              display: 'flex',
              alignItems: 'center'
            })"
          >
            <select 
              v-model="selectedKeyId" 
              :class="css({
                appearance: 'none',
                bg: 'surface.sunken',
                color: 'surface.text',
                pl: '2.5', pr: '6', py: '1',
                borderRadius: 'sm',
                fontSize: 'xs',
                fontWeight: '500',
                cursor: 'pointer',
                outline: 'none',
                minWidth: '140px',
                border: '1px solid transparent',
                transition: 'background 0.2s',
                _hover: { bg: 'rgba(0,0,0,0.05)' },
                _focus: { ring: '1px solid token(colors.brand.primary)' },
                '& option': {
                  bg: 'surface.base',
                  color: 'surface.text'
                }
              })"
            >
              <option value="" disabled>
                -- {{ pref.t("action.selectEngine") }} --
              </option>
              <option v-for="k in keyStore.keys" :key="k.id" :value="k.id">
                {{ k.provider }} - {{ k.name }}
              </option>
            </select>
            <div 
              :class="css({
                position: 'absolute',
                right: '3',
                top: '50%',
                transform: 'translateY(-50%)',
                fontSize: '10px',
                color: 'surface.textDim',
                pointerEvents: 'none'
              })"
            >▼</div>
          </div>

          <div :class="css({ w: '1px', h: '16px', bg: 'surface.outlineStrong' })"></div>

          <button
            :class="css({
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              w: '32px',
              h: '32px',
              borderRadius: 'md',
              bg: 'transparent',
              border: 'none',
              color: 'surface.textDim',
              cursor: 'pointer',
              transition: 'all 0.2s',
              _hover: { 
                bg: 'surface.sunken',
                color: 'brand.primary', 
                transform: 'scale(1.05)'
              },
              _active: { transform: 'scale(0.95)' }
            })"
            @click="pref.toggleTheme"
            :title="pref.t('action.toggleTheme')"
          >
            <svg
              v-if="!pref.isDark"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="12" cy="12" r="5"></circle>
              <line x1="12" y1="1" x2="12" y2="3"></line>
              <line x1="12" y1="21" x2="12" y2="23"></line>
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
              <line x1="1" y1="12" x2="3" y2="12"></line>
              <line x1="21" y1="12" x2="23" y2="12"></line>
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
            <svg
              v-else
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            </svg>
          </button>

          <button
            :class="css({
              fontSize: 'xs', fontWeight: 'bold', color: 'surface.text',
              px: '0', w: '30px', h: '30px',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              borderRadius: 'full', 
              cursor: 'pointer', 
              bg: 'transparent',
              border: 'none',
              transition: 'all 0.2s',
              fontFamily: 'mono',
              _hover: { 
                bg: 'surface.sunken', 
                color: 'brand.primary',
                transform: 'scale(1.05)'
              },
              _active: { transform: 'scale(0.95)' }
            })"
            @click="pref.toggleLocale"
            :title="pref.t('action.switchLang')"
          >
            {{ pref.locale === "zh" ? "中" : "EN" }}
          </button>
        </div>
      </header>

      <NotamWorkbench>
        <template #left>
          <NotamInputConsole
            :engine-ready="Boolean(selectedKeyId)"
          />
        </template>
        <template #right>
          <NotamStream />
        </template>
      </NotamWorkbench>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useKeyStore } from "@/stores/keyStore";
import { usePreferenceStore } from "@/stores/preferenceStore";
import { css } from "@/styled-system/css";
import SideNav from "@/components/layout/SideNav.vue";
import NotamWorkbench from "@/components/notam/NotamWorkbench.vue";
import NotamInputConsole from "@/components/notam/NotamInputConsole.vue";
import NotamStream from "@/components/notam/NotamStream.vue";

const keyStore = useKeyStore();
const pref = usePreferenceStore();
const selectedKeyId = computed({
  get: () => keyStore.selectedKeyId,
  set: (value: string) => keyStore.selectKey(value),
});

if (!keyStore.selectedKeyId && keyStore.keys.length > 0) keyStore.selectKey(keyStore.keys[0].id);
</script>
