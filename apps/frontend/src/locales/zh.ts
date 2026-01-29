export default {
  app: {
    title: "NOTAM 智能情报作战舱",
    subtitle: "多智能体推理流 / Multi-Agent Reasoning Stream",
  },
  action: {
    selectEngine: "选择推理引擎",
    toggleTheme: "切换主题",
    switchLang: "切换语言",
    run: "执行",
    clear: "清空",
    loadExample: "加载示例",
    upload: "上传文件",
    monitor: "加入监控",
    stopMonitor: "停止监控",

    locate: "定位",
    fix: "修正"
  },
  console: {
    title: "指令控制台",
    manual: "人工输入",
    live: "实时流",
    beta: "测试版",
    placeholder: "在此输入或粘贴 NOTAM... 支持直接拖入文件",
    ln: "行",
    col: "列",
    runTip: "运行",
    dropText: "松开以分析批量文件",
    dropSub: "支持 .txt, .json, .pdf"
  },
  radar: {
    title: "态势雷达",
    tracking: "追踪中",
    scanning: "扫描中...",
    locked: "目标锁定",
    noTarget: "无目标",
    awaiting: "等待信号",
    awaitingSub: "请输入机场代码 (如 ZBAA)",
    watchList: "监控列表",
    monitor: "+ 添加监控",
    labels: {
      icao: "四字码",
      name: "名称",
      fir: "情报区",
      pos: "坐标"
    }
  },
  stream: {
    title: "情报流",
    awaiting: "等待信号",
    standby: "系统就绪，等待 NOTAM 输入...",
    batchJob: "批量任务",
    processing: "正在处理",
    tasks: "个任务",
    inputPayload: "输入载荷",
    reasoningChain: "推理链",
    processLog: "处理日志",
    
    connecting: "建立连接中...",
    discoveryAgent: "探索智能体 (Discovery)",
    analystAgent: "分析智能体 (Analyst)",
    validatorAgent: "校验智能体 (Validator)",
    consensusAgent: "共识智能体 (Debate)",
    rendering: "渲染视图...",
    renderCompleted: "渲染完成",
    parsingFailed: "解析失败",
  },
  reasoningDrawer: {
    title: "推理链",
    finished: "推理完成",
    ops: "操作",
    idle: "AI 推理引擎已就绪",
    idleThinking: "AI 推理引擎思考中...",

    showRawText: "显示原始消息"
  },
  status: {
    scanning: "扫描中",
    locked: "已锁定",
    warning: "告警",

    confidence: "置信度",

    stage: {
      idle: "闲置",
      connecting: "连接中",
      discovering: "扫描中",
      analyzing: "分析中",
      validating: "验证中",
      finalized: "已完成",
      failed: "失败"
    },
    time: {
      active: "生效中",
      pending: "即将生效",
      expired: "已过期",
      perm: "永久有效",
      unknown: "未知"
    }
  }
};