export default {
  app: {
    title: "NOTAM Intelligence Cockpit",
    subtitle: "Multi-Agent Reasoning Stream",
  },
  action: {
    selectEngine: "Select Engine",
    toggleTheme: "Toggle Theme",
    switchLang: "Switch Language",
    run: "RUN",
    clear: "CLEAR",
    loadExample: "LOAD EXAMPLE",
    upload: "Upload File",
    monitor: "MONITOR",
    stopMonitor: "Stop Monitoring",

    locate: "Locate",
    fix: "Fix"
  },
  console: {
    title: "COMMAND CONSOLE",
    manual: "Manual Input",
    live: "Live Feed",
    beta: "BETA",
    placeholder: "Type or paste NOTAM here... Or drag files directly.",
    ln: "Ln",
    col: "Col",
    runTip: "to Run",
    dropText: "Release to Analyze Batch",
    dropSub: "Supports .txt, .json, .pdf"
  },
  radar: {
    title: "SURVEILLANCE RADAR",
    tracking: "TRACKING",
    scanning: "SCANNING...",
    locked: "TARGET LOCKED",
    noTarget: "NO TARGET",
    awaiting: "AWAITING SIGNAL",
    awaitingSub: "Type airport code (e.g. ZBAA)",
    watchList: "WATCH LIST",
    monitor: "+ MONITOR",
    labels: {
      icao: "ICAO",
      name: "NAME",
      fir: "FIR",
      pos: "POS"
    }
  },
  stream: {
    title: "INTELLIGENCE STREAM",
    awaiting: "Awaiting Signal",
    standby: "System standing by for NOTAM input...",
    batchJob: "BATCH JOB",
    processing: "PROCESSING",
    tasks: "TASKS",
    inputPayload: "Input Payload",
    reasoningChain: "Reasoning Chain",
    processLog: "Process Log",
    
    connecting: "Connecting...",
    discoveryAgent: "Agent DISCOVERY",
    analystAgent: "Agent ANALYST",
    validatorAgent: "Agent VALIDATOR",
    consensusAgent: "Agent CONSENSUS",
    rendering: "Rendering View...",
    renderCompleted: "RENDER COMPLETED",
    parsingFailed: "PARSING FAILED",
  },
  reasoningDrawer: {
    title: "Reasoning Chain",
    finished: "Analysis process completed",
    ops: "OPS",
    idle: "AI Reasoning Engine Ready",
    idleThinking: "AI Reasoning Engine Thinking...",

    showRawText: "SHOW ORIGINAL MESSAGE"
  },
  status: {
    scanning: "SCANNING",
    locked: "LOCKED",
    warning: "WARNING",

    confidence: "CONFIDENCE",

    stage: {
      idle: "IDLE",
      connecting: "CONNECTING",
      discovering: "SCANNING",
      analyzing: "ANALYZING",
      validating: "VALIDATING",
      finalized: "DONE",
      failed: "FAILED"
    },
    time: {
      active: "ACTIVE",
      pending: "PENDING",
      expired: "EXPIRED",
      perm: "PERM",
      unknown: "UNKNOWN"
    }
  }
};