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
    stopMonitor: "Stop Monitoring"
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
    renderCompleted: "RENDER COMPLETED",
    parsingFailed: "PARSING FAILED",
    inputPayload: "Input Payload",
    reasoningChain: "Reasoning Chain",
    processLog: "Process Log"
  },
  reasoningDrawer: {
    title: "Reasoning Chain",
    ops: "OPS"
  },
  status: {
    scanning: "SCANNING",
    locked: "LOCKED",
    warning: "WARNING"
  }
};