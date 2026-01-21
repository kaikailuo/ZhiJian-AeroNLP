<template>
  <div class="login-shell">
    <section class="login-hero">
      <div class="hero-content">
        <p class="badge">AeroNLP 指挥中枢</p>
        <h1>NOTAM 智能情报平台</h1>
        <p>
          将原始航行通告转化为结构化运行洞察，用于快速态势感知、告警与任务规划。
        </p>
        <div class="hero-grid">
          <div class="hero-card">
            <h3>解析</h3>
            <p>自动抽取跑道、机场与限制类关键信号。</p>
          </div>
          <div class="hero-card">
            <h3>监控</h3>
            <p>实时观察清单、告警规则与时间线分析。</p>
          </div>
          <div class="hero-card">
            <h3>协同</h3>
            <p>运维、训练与合规共享看板。</p>
          </div>
        </div>
      </div>
    </section>
    <section class="login-panel">
      <n-card class="login-card" title="安全登录">
        <n-form :model="form" @submit.prevent="handleLogin">
          <n-form-item label="邮箱">
            <n-input v-model:value="form.email" placeholder="you@aeronlp.local" />
          </n-form-item>
          <n-form-item label="密码">
            <n-input
              v-model:value="form.password"
              type="password"
              placeholder="至少 8 位"
            />
          </n-form-item>
          <n-space vertical size="large">
            <n-button type="primary" block :loading="loading" @click="handleLogin">
              进入指挥舱
            </n-button>
            <n-button tertiary block :loading="loading" @click="handleRegister">
              创建账号
            </n-button>
          </n-space>
          <p class="login-hint">
            演示账号：<strong>admin@aeronlp.local</strong> / <strong>admin123</strong>
          </p>
          <p v-if="error" class="login-error">{{ error }}</p>
        </n-form>
      </n-card>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { NButton, NCard, NForm, NFormItem, NInput, NSpace } from "naive-ui";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const auth = useAuthStore();
const loading = ref(false);
const error = ref("" as string | "");

const form = ref({
  email: "admin@aeronlp.local",
  password: "admin123",
});

const handleLogin = async () => {
  try {
    loading.value = true;
    error.value = "";
    await auth.login(form.value.email, form.value.password);
    router.push({ name: "home" });
  } catch (err: any) {
    error.value = err?.response?.data?.message || "登录失败。";
  } finally {
    loading.value = false;
  }
};

const handleRegister = async () => {
  try {
    loading.value = true;
    error.value = "";
    await auth.register(form.value.email, form.value.password);
    await handleLogin();
  } catch (err: any) {
    error.value = err?.response?.data?.message || "注册失败。";
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-shell {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  min-height: 100vh;
}

.login-hero {
  background: linear-gradient(140deg, rgba(11, 16, 32, 0.95), rgba(12, 26, 62, 0.9)),
    url("https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=1200&q=80")
      center/cover;
  color: #e7edff;
  padding: 64px;
}

.hero-content h1 {
  font-size: 42px;
  margin: 16px 0 12px;
}

.hero-content p {
  max-width: 480px;
  color: rgba(231, 237, 255, 0.78);
  line-height: 1.7;
}

.hero-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 32px;
}

.hero-card {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px;
  border-radius: 12px;
}

.login-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
}

.login-card {
  width: 100%;
  max-width: 380px;
}

.login-hint {
  margin-top: 16px;
  font-size: 12px;
  color: #5b6a82;
}

.login-error {
  margin-top: 12px;
  color: #d92d20;
  font-weight: 600;
}

@media (max-width: 980px) {
  .login-shell {
    grid-template-columns: 1fr;
  }
  .hero-grid {
    grid-template-columns: 1fr;
  }
}
</style>
