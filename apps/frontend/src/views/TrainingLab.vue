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
        <router-link class="nav-item router-link-active" to="/training">训练实验室</router-link>
        <router-link class="nav-item" to="/api-keys">API 密钥库</router-link>
      </nav>
    </aside>

    <main class="main-panel fade-in">
      <header class="page-header">
        <div>
          <h2>训练实验室</h2>
          <p>随机抽取 NOTAM 进行解析挑战，即时获取反馈</p>
        </div>
        <router-link to="/" class="badge">返回总览</router-link>
      </header>

      <div class="lab-container">
        <!-- Sidebar: Training Status -->
        <div class="card" style="height: fit-content;">
           <div class="card-header">
             <h3>训练状态</h3>
             <p class="card-sub">Session Stats</p>
           </div>
           
           <div class="status-panel">
               <div class="stat-item">
                   <div class="label">当前连胜</div>
                   <div class="value">{{ streak }}</div>
               </div>
               <div class="stat-item">
                   <div class="label">答题总数</div>
                   <div class="value">{{ history.length }}</div>
               </div>
               <div class="stat-item">
                   <div class="label">正确率</div>
                   <div class="value">{{ accuracy }}%</div>
               </div>
           </div>

           <div class="divider"></div>

           <div class="history-list">
               <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px;">
                    <h4 style="font-size: 13px; color: #6b7a94; margin:0;">答题记录</h4>
                    <span style="font-size:12px; color:#999;" v-if="history.length > 0">点击回顾</span>
               </div>
               <div v-if="history.length === 0" style="color: #999; font-size: 13px;">暂无记录</div>
               <div 
                  v-for="(rec, i) in history" 
                  :key="i" 
                  class="history-item"
                  @click="reviewHistory(rec)"
                  :class="{'active-history': currentExercise?.id === rec.id}"
               >
                   <div class="history-dot" :class="rec.result ? 'dot-success' : 'dot-fail'"></div>
                   <span class="history-text">#{{ rec.title }}</span>
               </div>
           </div>

           <div style="margin-top: 24px;">
               <n-button block ghost type="primary" @click="resetSession">
                   重置会话
               </n-button>
               <n-button block style="margin-top: 12px;" @click="showCertModal = true">
                   🏆 荣誉证书
               </n-button>
           </div>
        </div>

        <!-- Right: Active Exercise Workspace -->
        <div class="card" v-if="currentExercise">
            <div class="card-header">
               <div>
                  <h3>题号 #{{ currentExercise.displayId }}</h3>
                  <p class="card-sub">随机抽取 / Random Draw</p>
               </div>
               <n-tag type="info" size="small">单选题</n-tag>
            </div>

            <!-- NOTAM Display -->
            <div class="notam-container">
              <p class="notam-label">NOTAM 原文</p>
              <pre class="notam-text">{{ currentExercise.notam }}</pre>
            </div>

            <h4 class="question-header">{{ currentExercise.question }}</h4>
            
            <n-radio-group v-model:value="selectedOption" name="quiz-options" class="options-group">
                <n-space vertical>
                    <n-radio 
                        v-for="(opt, idx) in currentExercise.options" 
                        :key="idx" 
                        :value="idx"
                        class="option-radio"
                        :disabled="!!submissionResult"
                    >
                        <span class="option-text">{{ opt }}</span>
                    </n-radio>
                </n-space>
            </n-radio-group>

            <div class="actions">
                <n-button 
                    v-if="!submissionResult"
                    type="primary" 
                    size="large"
                    @click="submitAnswer" 
                    :loading="loading"
                    :disabled="selectedOption === null"
                >
                    提交答案
                </n-button>

                <n-button 
                    v-else
                    type="primary" 
                    size="large"
                    @click="nextQuestion"
                >
                    下一题
                </n-button>
            </div>

            <!-- Feedback -->
             <n-collapse-transition :show="!!submissionResult">
                <div 
                    v-if="submissionResult" 
                    class="feedback-panel"
                    :class="submissionResult.isCorrect ? 'bg-success' : 'bg-fail'"
                >
                    <div class="feedback-title">
                        {{ submissionResult.isCorrect ? '✅ 回答正确' : '❌ 回答错误' }}
                    </div>
                    <div class="feedback-desc">
                        {{ submissionResult.feedback }}
                    </div>
                     <div class="api-log">
                        服务端响应: {{ submissionResult.apiMsg }}
                    </div>
                </div>
             </n-collapse-transition>
        </div>
      </div>
    </main>

    <!-- Certificate Modal -->
    <n-modal v-model:show="showCertModal">
      <n-card style="width: 600px" title="荣誉证书 / Certificates" :bordered="false" size="huge" role="dialog" aria-modal="true">
         
         <div v-if="unlockedCert" class="cert-view">
            <div class="cert-paper">
                <div class="cert-border">
                    <div class="cert-header">CERTIFICATE OF ACHIEVEMENT</div>
                    <div class="cert-body">
                        This certifies that<br>
                        <span class="cert-name">OPERATOR #{{ Math.floor(Math.random()*1000)+1000 }}</span><br>
                        has successfully completed the requirements for<br>
                        <span class="cert-title">{{ unlockedCert.title }}</span>
                    </div>
                    <div class="cert-footer">
                        <div class="cert-date">{{ new Date().toLocaleDateString() }}</div>
                        <div class="cert-sign">ZhiJian Aero-Ops Command</div>
                    </div>
                    <div class="cert-stamp">APPROVED</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 20px;">
                <n-button type="primary" @click="unlockedCert = null">查看所有证书</n-button>
            </div>
         </div>

         <div v-else class="cert-list">
             <div 
                v-for="cert in achievements" 
                :key="cert.id" 
                class="cert-item"
                :class="{ 'cert-locked': !cert.unlocked, 'cert-unlocked': cert.unlocked }"
             >
                <div class="cert-icon">{{ cert.unlocked ? '🏆' : '🔒' }}</div>
                <div class="cert-info">
                    <div class="cert-name">{{ cert.title }}</div>
                    <div class="cert-desc">{{ cert.desc }}</div>
                    <div class="cert-progress">
                        进度: {{ totalAnswered }}/{{ cert.reqCount }} 题 (正确率 ≥ {{ cert.reqAcc }}%)
                    </div>
                </div>
                <n-button 
                    size="small" 
                    :disabled="!cert.unlocked" 
                    @click="viewCert(cert)"
                    :type="cert.unlocked ? 'primary' : 'default'"
                >
                    {{ cert.unlocked ? '查看证书' : '未解锁' }}
                </n-button>
             </div>
         </div>
      </n-card>
    </n-modal>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useMessage, NTag, NRadioGroup, NRadio, NSpace, NButton, NCollapseTransition, NModal, NCard } from 'naive-ui';
import { trainingAPI } from '@/services/training';

const message = useMessage();
const loading = ref(false);
const showCertModal = ref(false);
const unlockedCert = ref<any>(null);

interface QuizExercise {
  id: string;
  displayId: string;
  notam: string;
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

interface HistoryRecord {
    id: string;
    title: string;
    result: boolean;
    selectedOption: number;
    submissionResult: { isCorrect: boolean; feedback: string; apiMsg: string };
}

interface Achievement {
    id: string;
    title: string;
    desc: string;
    reqCount: number;
    reqAcc: number;
    unlocked: boolean;
}

// Achievements Config
const achievements = ref<Achievement[]>([
    { id: 'c1', title: '初级情报员 (Junior Analyst)', desc: '完成 5 道题目，且正确率在 50% 以上', reqCount: 5, reqAcc: 50, unlocked: false },
    { id: 'c2', title: '高级情报官 (Senior Officer)', desc: '完成 10 道题目，且正确率在 80% 以上', reqCount: 10, reqAcc: 80, unlocked: false },
    { id: 'c3', title: '航行作战专家 (Aero-Ops Master)', desc: '完成 20 道题目，且正确率在 90% 以上', reqCount: 20, reqAcc: 90, unlocked: false },
]);

// Mock Data Pool
const exercisePool: QuizExercise[] = [
  {
    id: 'q1',
    displayId: '8392',
    notam: `A) ZBAA\nB) 2310010000 C) 2310010800\nE) RWY 18L/36R CLSD DUE TO MAINT.`,
    question: '该 NOTAM 描述的主要影响是什么？',
    options: [
        '跑道 18L/36R 因维护而关闭',
        '跑道 18L/36R 开放但灯光不可用',
        '滑行道关闭',
        '跑道 18R/36L 关闭'
    ],
    correctIndex: 0,
    explanation: 'E项明确指出 "RWY 18L/36R CLSD" (Closed) "DUE TO MAINT" (Maintenance)。'
  },
  {
    id: 'q2',
    displayId: '1045',
    notam: `A) ZSSS\nB) 2311050000 C) 2311062359\nE) ILS RWY 35R U/S.`,
    question: '根据 NOTAM，ILS 系统状态如何？',
    options: [
        '跑道 35R 的 ILS 完全正常',
        '跑道 17L 的 ILS 不可用',
        '跑道 35R 的 ILS 不可用 (U/S)',
        '正在进行 ILS 飞行测试'
    ],
    correctIndex: 2,
    explanation: 'U/S 是 "Unserviceable" 的缩写，表示设施不可用。'
  },
  {
     id: 'q3',
     displayId: '5521',
     notam: `A) ZGGG\nB) 2312010000 C) PERM\nE) OBST LGT AT P66 (230912N 1131815E) U/S.`,
     question: '受影响的设施位于哪里？',
     options: [
         '跑道入口',
         'P66 点位 (具体坐标 230912N 1131815E)',
         '塔台顶部',
         '停机位 66'
     ],
     correctIndex: 1,
     explanation: 'NOTAM 指出 "AT P66" 并附带了经纬度坐标。OBST LGT 指障碍物灯光。'
  },
  {
     id: 'q4',
     displayId: '9822',
     notam: `A) ZSPD\nB) 2310101000 C) 2310101400\nE) TWY A BTN TWY A1 AND TWY A3 CLSD.`,
     question: '哪一段滑行道被关闭？',
     options: [
         '滑行道 A 全段',
         '滑行道 A1 和 A3 之间的滑行道 A',
         '滑行道 A1',
         '滑行道 A3'
     ],
     correctIndex: 1,
     explanation: 'BTN ... AND ... 表示 "Between ... and ..."，即 A1 到 A3 之间的 A 滑行道关闭。'
  },
  // 新增题目
  {
    id: 'q5',
    displayId: '1105',
    notam: `A) ZBAA\nB) 2310250000 C) 2310250400\nE) PAPI RWY 36R U/S.`,
    question: '该 NOTAM 报告了什么设施故障？',
    options: [
      '跑道灯光整体故障',
      '滑行道指示灯故障',
      '跑道 36R 的精密进近航道指示器 (PAPI) 不可用',
      '仪表着陆系统 (ILS) 故障'
    ],
    correctIndex: 2,
    explanation: 'PAPI (Precision Approach Path Indicator) 是精密进近航道指示器。U/S 代表不可用。'
  },
  {
    id: 'q6',
    displayId: '2230',
    notam: `A) ZUUU\nB) 2311100100 C) 2311100500\nE) GRASS CUTTING IN PROGR ON BOTH SIDES OF RWY 02L/20R. MEN AND EQPT PRES.`,
    question: '跑道附近正在进行什么活动？',
    options: [
      '除雪作业',
      '跑道铺设',
      '除草作业 (GRASS CUTTING)',
      '灯光维修'
    ],
    correctIndex: 2,
    explanation: '"GRASS CUTTING IN PROGR" 表示正在进行除草作业。"MEN AND EQPT PRES" 提示有人和设备在场。'
  },
  {
    id: 'q7',
    displayId: '3341',
    notam: `A) ZSHC\nB) 2312010000 C) 2312312359\nE) FIRE FIGHTING DOWNGRADED TO CAT 6.`,
    question: '机场的消防等级发生了什么变化？',
    options: [
      '升级到 6 级',
      '降级到 6 级',
      '取消所有消防服务',
      '正在进行消防演习'
    ],
    correctIndex: 1,
    explanation: 'DOWNGRADED 意为降级。Fire Fighting Category 降级可能会影响某些大型飞机的起降。'
  },
  {
    id: 'q8',
    displayId: '4788',
    notam: `A) ZBTJ\nB) 2311200000 C) 2311200400\nE) VOR/DME TJC 113.5MHZ U/S DUE TO MAINT.`,
    question: '哪个导航设备因维护不可用？',
    options: [
      'NDB 导航台',
      'ILS 系统',
      '频率为 113.5MHz 的 VOR/DME (代号 TJC)',
      '塔台通讯频率'
    ],
    correctIndex: 2,
    explanation: '明确指出了设施类型 "VOR/DME"、代号 "TJC" 和频率 "113.5MHZ"。'
  },
  {
    id: 'q9',
    displayId: '5912',
    notam: `A) ZGSZ\nB) 2310150900 C) 2310151100\nE) RESTRICTED AREA ZGR123 ACT. VERTICAL LIMITS: GND/3000M.\nF) GND G) 3000M AMSL`,
    question: '关于限制区 ZGR123 的描述，哪项正确？',
    options: [
      '限制区已取消',
      '限制区永久生效',
      '限制区活动中，高度范围是地面 (GND) 至平均海平面 3000 米',
      '限制区仅在夜间生效'
    ],
    correctIndex: 2,
    explanation: 'ACT 表示 Active (生效/活动)。F) 和 G) 项定义了垂直范围：地面 (GND) 到 3000米 (3000M AMSL)。'
  },
  {
    id: 'q10',
    displayId: '6023',
    notam: `A) ZWWW\nB) 2311082300 C) 2311090600\nE) AD CLSD DUE TO WIP.`,
    question: '机场 (AD) 的状态是？',
    options: [
      '机场完全关闭',
      '机场仅关闭进近雷达',
      '机场仅关闭出发程序',
      '机场正常运行'
    ],
    correctIndex: 0,
    explanation: '"AD CLSD" 即 Aerodrome Closed (机场关闭)。"WIP" = Work In Progress (施工中)。'
  },
  {
    id: 'q11',
    displayId: '7156',
    notam: `A) ZGGG\nB) 2311150000 C) PERM\nE) NEW FREQ 121.750MHZ FOR DELIVERY SERVICE AVBL.`,
    question: '新增了什么服务频率？',
    options: [
      '地面管制频率',
      '塔台频率',
      '放行许可 (Delivery) 频率 121.750MHZ',
      '进近管制频率'
    ],
    correctIndex: 2,
    explanation: '"DELIVERY SERVICE" 指放行许可服务。'
  },
  {
    id: 'q12',
    displayId: '8247',
    notam: `A) ZSAM\nB) 2312051200 C) 2312052000\nE) CRANE ERECTED AT 500M S OF ARP, HGT 45M.`,
    question: '关于障碍物的描述，以下哪项正确？',
    options: [
      '跑道上有车辆',
      '机场基准点 (ARP) 以南 500 米处竖立起重机，高度 45 米',
      '塔台正在施工',
      '滑行道上有路障'
    ],
    correctIndex: 1,
    explanation: 'CRANE = 起重机/吊车，ERECTED = 竖立，S OF ARP = 机场基准点以南。'
  },
  {
    id: 'q13',
    displayId: '9001',
    notam: `A) ZBAA\nB) 2310010000 C) 2310312359\nE) BIRD CONCENTRATION IN VICINITY OF RWY 01/19.`,
    question: '飞行员应警惕什么风险？',
    options: [
      '风切变',
      '跑道积冰',
      '跑道 01/19 附近的鸟群聚集 (鸟击风险)',
      '激光照射'
    ],
    correctIndex: 2,
    explanation: '"BIRD CONCENTRATION" 指鸟群聚集，"VICINITY" 意为附近。'
  },
  {
    id: 'q14',
    displayId: '9134',
    notam: `A) ZSSS\nB) 2311181200 C) 2311181600\nE) GNSS RAIM SERVICE UNRELIABLE.`,
    question: '什么系统服务不可靠？',
    options: [
      'VHF 通讯',
      'GNSS RAIM (全球卫星导航系统完好性监测)',
      '气象雷达',
      '跑道灯光'
    ],
    correctIndex: 1,
    explanation: '明确提到 "GNSS RAIM SERVICE" 不可靠 (UNRELIABLE)。'
  },
  {
    id: 'q15',
    displayId: '9355',
    notam: `A) ZGHA\nB) 2311220000 C) PERM\nE) STAND 105 RECONFIGURED TO ACFT TYPE B737/A320.`,
    question: '停机位 105 发生了什么变化？',
    options: [
      '关闭维修',
      '更名为停机位 106',
      '重新配置，现适用于 B737/A320 机型',
      '仅用于直升机'
    ],
    correctIndex: 2,
    explanation: '"RECONFIGURED" = 重新配置。"ACFT TYPE" = 机型。'
  },
  {
    id: 'q16',
    displayId: '1668',
    notam: `A) ZYHB\nB) 2310300000 C) 2310300800\nE) TWY C CLSD BTN INT RWY 05/23 AND TWY B.`,
    question: '滑行道 C 的关闭范围是？',
    options: [
      '全程关闭',
      '跑道 05/23 交叉口与滑行道 B 之间的路段',
      '滑行道 B 以东',
      '仅入口处'
    ],
    correctIndex: 1,
    explanation: '"BTN" (Between) ... "INT" (Intersection) RWY 05/23 "AND" TWY B。'
  },
  {
    id: 'q17',
    displayId: '2779',
    notam: `A) ZUUU\nB) 2311020100 C) 2311020400\nE) WIP ON APRON 3. TAXI WITH CAUTION.`,
    question: '3 号机坪 (Apron) 上有什么情况？',
    options: [
      '有积水',
      '正在进行施工 (WIP)，滑行需谨慎',
      '完全关闭',
      '停放了故障飞机'
    ],
    correctIndex: 1,
    explanation: 'WIP (Construction Work In Progress) 位于 APRON 3。"TAXI WITH CAUTION" 提示滑行需小心。'
  },
  {
    id: 'q18',
    displayId: '3890',
    notam: `A) ZLXY\nB) 2312101000 C) 2312101400\nE) RWY 23L THRESHOLD DISPLACED 300M INWARDS DUE TO WIP. DECLARED DIST: TORA 2900M.`,
    question: '跑道 23L 的入口 (Threshold) 发生了什么变化？',
    options: [
        '标志不清',
        '向内位移 300 米',
        '向外延伸 300 米',
        '完全封闭'
    ],
    correctIndex: 1,
    explanation: '"THRESHOLD DISPLACED ... INWARDS" 表示入口向内位移。'
  },
  {
    id: 'q19',
    displayId: '4991',
    notam: `A) ZYTX\nB) 2311120000 C) PERM\nE) STANDARD DEPARTURE CHART - INSTRUMENT (SID): RWY 06: CREATE NEW PROC 'VEN SNO 1A'.`,
    question: '该 NOTAM 通知了什么程序变更？',
    options: [
        '取消所有进离场程序',
        '跑道 06 新增仪表标准离场程序 (SID) "VEN SNO 1A"',
        '跑道 06 修改了进近程序',
        '更改了机场标高'
    ],
    correctIndex: 1,
    explanation: 'SID = Standard Instrument Departure。CREATE NEW PROC = 创建新程序。'
  },
  {
    id: 'q20',
    displayId: '5002',
    notam: `A) ZBAA\nB) 2311250000 C) 2311252359\nE) REF AIP SUP 12/23. TEMPO SEGREGATED PARALLEL OPS IN FORCE.`,
    question: '正在实施什么运行模式？',
    options: [
        '单跑道运行',
        '混合起降运行',
        '临时隔离平行运行 (Segregated Parallel Ops)',
        '目视进近模式'
    ],
    correctIndex: 2,
    explanation: '"SEGREGATED PARALLEL OPS" 即隔离平行运行模式。'
  }
];

// State
const currentExercise = ref<QuizExercise | null>(null);
const selectedOption = ref<number | null>(null);
const submissionResult = ref<{ isCorrect: boolean; feedback: string; apiMsg: string } | null>(null);

const history = ref<HistoryRecord[]>([]);
const streak = ref(0);
// Persist streak and history simple logic
const totalAnswered = computed(() => history.value.length);

const accuracy = computed(() => {
    if (history.value.length === 0) return 0;
    const correct = history.value.filter(h => h.result).length;
    return Math.round((correct / history.value.length) * 100);
});

// Logic
const checkAchievements = () => {
    const total = totalAnswered.value;
    const acc = accuracy.value;
    
    achievements.value.forEach(cert => {
        if (!cert.unlocked) {
            if (total >= cert.reqCount && acc >= cert.reqAcc) {
                cert.unlocked = true;
                message.success(`🎖️ 恭喜！您已解锁证书：${cert.title}`);
                saveProgress();
            }
        }
    });
};

const viewCert = (cert: Achievement) => {
    unlockedCert.value = cert;
};

// Persistence
const saveProgress = () => {
    localStorage.setItem('aero_training_history', JSON.stringify(history.value));
    localStorage.setItem('aero_training_streak', streak.value.toString());
    const unlockedIds = achievements.value.filter(c => c.unlocked).map(c => c.id);
    localStorage.setItem('aero_training_certs', JSON.stringify(unlockedIds));
};

const loadProgress = () => {
    const savedHist = localStorage.getItem('aero_training_history');
    if (savedHist) history.value = JSON.parse(savedHist);

    const savedStreak = localStorage.getItem('aero_training_streak');
    if (savedStreak) streak.value = parseInt(savedStreak);

    const savedCerts = localStorage.getItem('aero_training_certs');
    if (savedCerts) {
        const unlockedIds = JSON.parse(savedCerts);
        achievements.value.forEach(c => {
            if (unlockedIds.includes(c.id)) c.unlocked = true;
        });
    }
};

// Methods
const drawQuestion = () => {
    // Simple random draw for now, avoiding immediate repeat if possible
    let nextIdx = Math.floor(Math.random() * exercisePool.length);
    if (currentExercise.value && exercisePool.length > 1) {
        while (exercisePool[nextIdx].id === currentExercise.value.id) {
             nextIdx = Math.floor(Math.random() * exercisePool.length);
        }
    }
    currentExercise.value = exercisePool[nextIdx];
    selectedOption.value = null; // Reset selection
    submissionResult.value = null; // Reset result
};

const reviewHistory = (record: HistoryRecord) => {
    const exercise = exercisePool.find(e => e.id === record.id);
    if (exercise) {
        currentExercise.value = exercise;
        selectedOption.value = record.selectedOption;
        submissionResult.value = record.submissionResult;
    }
};

const submitAnswer = async () => {
    if (!currentExercise.value || selectedOption.value === null) return;
    
    loading.value = true;
    const isCorrect = selectedOption.value === currentExercise.value.correctIndex;
    
    // Simulate API delay
    await new Promise(r => setTimeout(r, 600));

    // Update Stats
    if (isCorrect) streak.value++;
    else streak.value = 0;

    const resultPayload = {
        isCorrect,
        feedback: isCorrect 
            ? `回答正确！ ${currentExercise.value.explanation}` 
            : `回答错误。正确答案是：${currentExercise.value.options[currentExercise.value.correctIndex]}。解析：${currentExercise.value.explanation}`,
        apiMsg: "Answer recorded successfully"
    };

    // Save full context to history
    history.value.unshift({
        id: currentExercise.value.id,
        title: currentExercise.value.displayId,
        result: isCorrect,
        selectedOption: selectedOption.value,
        submissionResult: resultPayload
    });

    // Set Result
    submissionResult.value = resultPayload;

    saveProgress();
    checkAchievements();

    loading.value = false;
};

const nextQuestion = () => {
    drawQuestion();
};

const resetSession = () => {
    history.value = [];
    streak.value = 0;
    saveProgress();
    
    // Lock certs? No, certs should persist even if session history is cleared for UI clutter reasons.
    // Actually user asked to "reset session", implies clearing history table. 
    // We should probably keep certs unlocked. 
    // But then re-locking achievements logic might be tricky. 
    // For simplicity, let's keep certs as permanent achievements.
    
    drawQuestion();
};

// Init
onMounted(() => {
    loadProgress();
    drawQuestion();
});

</script>

<style scoped>
/* Page Layout */
.lab-container {
    display: grid;
    grid-template-columns: 280px 1fr;
    gap: 24px;
    align-items: start;
}

@media (max-width: 900px) {
    .lab-container {
        grid-template-columns: 1fr;
    }
}

/* Nav (Copied from HomeView) */
.nav-list { display: grid; gap: 10px; margin-top: 24px; }
.nav-item { padding: 10px 14px; border-radius: 10px; color: rgba(223, 231, 255, 0.85); font-weight: 500; transition: background 0.2s ease; }
.nav-item.router-link-active { background: rgba(26, 116, 255, 0.2); color: #ffffff; }
.nav-item:not(.router-link-active):hover { background: rgba(255, 255, 255, 0.05); }

/* Header */
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.card-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 16px; }
.card-title { font-size: 13px; text-transform: uppercase; letter-spacing: 0.08em; color: #6b7a94; }
.card-sub { color: #6b7a94; font-size: 13px; }

/* Status Panel */
.status-panel { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 20px; }
.stat-item { text-align: center; }
.stat-item .label { font-size: 12px; color: #66748c; margin-bottom: 4px; }
.stat-item .value { font-size: 18px; font-weight: 600; color: #0a1220; }
.divider { height: 1px; background: #eee; margin: 16px 0; }

.history-list { max-height: 300px; overflow-y: auto; }
.history-item { 
    display: flex; 
    align-items: center; 
    gap: 10px; 
    padding: 8px 10px; 
    font-size: 13px; 
    cursor: pointer;
    border-radius: 6px;
    transition: background 0.2s;
}
.history-item:hover { background: #f5f7fb; }
.active-history { background: rgba(26, 116, 255, 0.1); }
.history-dot { width: 8px; height: 8px; border-radius: 50%; padding: 0; min-width: 8px; }
.dot-success { background: #1a7f37; }
.dot-fail { background: #cf222e; }
.history-text { color: #444; }

/* Workspace */
.notam-container {
    background: rgba(26, 116, 255, 0.04); 
    padding: 16px; 
    border-radius: 8px; 
    border: 1px dashed rgba(26, 116, 255, 0.2); 
    margin-bottom: 24px;
}
.notam-label { font-size: 12px; font-weight: 600; color: #1a74ff; margin-bottom: 8px; }
.notam-text { margin: 0; font-family: 'IBM Plex Mono', monospace; white-space: pre-wrap; font-size: 14px; color: var(--color-ink); }

.question-header { font-size: 18px; margin-bottom: 20px; line-height: 1.4; color: #0a1220; }

.options-group { width: 100%; margin-bottom: 24px; }
.option-radio { 
    padding: 12px 16px; 
    border: 1px solid #eee; 
    border-radius: 8px; 
    width: 100%; 
    transition: all 0.2s;
}
.option-radio:hover { background: #f9f9f9; border-color: #ddd; }
.option-radio:has(:checked) { border-color: #1a74ff; background: rgba(26, 116, 255, 0.04); }

.option-text { font-size: 15px; }

.actions { margin-top: 24px; }

/* Feedback */
.feedback-panel { margin-top: 24px; padding: 16px; border-radius: 8px; }
.bg-success { background: rgba(46, 160, 67, 0.1); color: #1a7f37; }
.bg-fail { background: rgba(218, 54, 51, 0.1); color: #cf222e; }

.feedback-title { font-weight: 600; font-size: 16px; margin-bottom: 8px; }
.feedback-desc { font-size: 14px; line-height: 1.5; }
.api-log { margin-top: 12px; font-size: 12px; opacity: 0.7; font-family: monospace; }

/* Certificate Styles */
.cert-list {
  display: grid;
  gap: 16px;
}
.cert-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: 12px;
  background: #f9f9f9;
  border: 1px solid #eee;
  transition: all 0.2s;
}
.cert-item.cert-unlocked {
  background: white;
  border-color: #1a74ff;
  box-shadow: 0 4px 12px rgba(26, 116, 255, 0.1);
}
.cert-item.cert-locked {
  opacity: 0.7;
  filter: grayscale(0.8);
}
.cert-icon {
  font-size: 32px;
}
.cert-info {
  flex: 1;
}
.cert-name {
  font-weight: 700;
  font-size: 16px;
  color: #0a1220;
}
.cert-desc {
  font-size: 13px;
  color: #66748c;
  margin-top: 4px;
}
.cert-progress {
  font-size: 12px;
  margin-top: 6px;
  color: #1a74ff;
  font-weight: 500;
}

/* Certificate Paper View */
.cert-view {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.cert-paper {
  width: 100%;
  max-width: 500px;
  background: #fff;
  padding: 20px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
  position: relative;
}
.cert-border {
  border: 4px double #1a74ff;
  padding: 30px;
  text-align: center;
  position: relative;
  background: radial-gradient(circle at center, #fff 0%, #f0f7ff 100%);
}
.cert-header {
  font-family: 'Times New Roman', serif;
  font-size: 24px;
  font-weight: bold;
  letter-spacing: 2px;
  margin-bottom: 30px;
  color: #0a1220;
  border-bottom: 2px solid #0a1220;
  padding-bottom: 10px;
  display: inline-block;
}
.cert-body {
  font-family: 'Times New Roman', serif;
  font-size: 16px;
  line-height: 2;
  color: #444;
  margin-bottom: 40px;
}
.cert-name {
  font-family: 'Courier New', monospace;
  font-size: 20px;
  font-weight: bold;
  color: #1a74ff;
  border-bottom: 1px dotted #999;
  padding: 0 10px;
}
.cert-title {
  font-size: 24px;
  font-weight: bold;
  color: #1a74ff; 
  display: block;
  margin-top: 10px;
}
.cert-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 40px;
  font-family: 'Times New Roman', serif;
}
.cert-date, .cert-sign {
  border-top: 1px solid #444;
  padding-top: 5px;
  width: 120px;
  font-size: 12px;
}
.cert-stamp {
  position: absolute;
  bottom: 40px;
  right: 60px;
  color: rgba(26, 116, 255, 0.15);
  font-size: 40px;
  font-weight: 900;
  transform: rotate(-20deg);
  border: 4px solid rgba(26, 116, 255, 0.15);
  padding: 5px 20px;
  border-radius: 10px;
  pointer-events: none;
}

</style>