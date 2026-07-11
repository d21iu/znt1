const $ = (id) => document.getElementById(id);

const checkType = $("checkType");
const experimentType = $("experimentType");
const grade = $("grade");
const experimentName = $("experimentName");
const content = $("content");
const fileInput = $("file");
const submitBtn = $("submitBtn");
const statusEl = $("status");
const resultPanel = $("result");
const demoCase = $("demoCase");
const importDemoBtn = $("importDemoBtn");

// 内置文本测试案例（来自课程 samples/text），供教师快速体验检测效果
const DEMO_CASES = [
  {
    id: "complete",
    label: "① 规范完整报告（液压泵性能测试）",
    experiment_name: "液压泵性能测试实验",
    content: `实验名称：液压泵性能测试实验
实验目的：掌握齿轮泵容积效率、总效率的测试方法，理解压力-流量特性。
实验原理：在额定转速下，通过溢流阀调节负载压力，记录泵出口流量与输入功率，计算效率。
实验步骤：
1. 检查油箱油位与油液清洁度，确认溢流阀处于全开。
2. 启动电机，空载运行 2 min 排气。
3. 逐步关闭溢流阀，记录压力 2、4、6、8、10 MPa 下的流量与功率。
4. 停机后泄压，擦拭漏油。
实验数据：
| 压力(MPa) | 流量(L/min) | 输入功率(kW) |
| 2 | 18.2 | 1.05 |
| 4 | 17.6 | 1.12 |
| 6 | 16.9 | 1.18 |
| 8 | 15.8 | 1.25 |
| 10 | 14.1 | 1.30 |
误差分析：流量采用涡轮流量计，精度 ±1%；功率表精度 ±0.5%。主要误差来源为油温变化引起粘度改变。
结论：随负载压力升高，泵流量下降，总效率在 6 MPa 附近最高，与教材趋势一致。
安全说明：实验全程佩戴护目镜；调压缓慢；拆卸接头前必须泄压。`,
  },
  {
    id: "missing_purpose",
    label: "② 缺实验目的/原理（气动回路速度控制）",
    experiment_name: "气动回路速度控制",
    content: `实验名称：气动回路速度控制
实验步骤：连接气缸、节流阀与换向阀，调节排气节流观察速度。
数据：气压 0.5，气缸行程 100，时间 3.2
结论：节流越小速度越慢。`,
  },
  {
    id: "missing_units",
    label: "③ 数据缺单位（溢流阀开启压力）",
    experiment_name: "溢流阀开启压力测定",
    content: `实验目的：测定溢流阀开启压力
实验步骤：缓慢升高泵出口压力，记录溢流阀开始溢流时的压力读数。
实验数据：第一次 6.2，第二次 6.5，第三次 6.3
结论：溢流阀调定压力约为 6.3。`,
  },
  {
    id: "no_error_analysis",
    label: "④ 缺误差分析（单作用气缸回路）",
    experiment_name: "单作用气缸气动回路",
    content: `实验目的：分析单作用气缸气动回路
实验原理：压缩空气经减压阀、换向阀进入气缸无杆腔，推动活塞伸出。
实验步骤：搭建回路，调节减压阀至 0.6 MPa，记录伸出行程与时间。
实验数据：压力 0.6 MPa，行程 80 mm，时间 1.2 s，平均速度 66.7 mm/s。
结论：压力越高伸出越快。`,
  },
  {
    id: "unreasonable",
    label: "⑤ 结论不合理（节流调速回路）",
    experiment_name: "液压节流调速回路特性",
    content: `实验目的：液压系统节流调速回路特性
实验数据：节流口开度 50% 时负载压力 5 MPa、流量 12 L/min；开度 100% 时 3 MPa、20 L/min。
误差分析：压力表精度 1.6 级。
结论：节流口开度越大，负载压力越高，说明节流口开大后阻力更大，与伯努利方程矛盾，数据完全错误应重做。`,
  },
];

function populateDemoCases() {
  DEMO_CASES.forEach((c) => {
    const opt = document.createElement("option");
    opt.value = c.id;
    opt.textContent = c.label;
    demoCase.appendChild(opt);
  });
}

function importDemoCase() {
  const c = DEMO_CASES.find((x) => x.id === demoCase.value);
  if (!c) {
    statusEl.textContent = "请先选择一个示例报告";
    return;
  }
  checkType.value = "text";
  syncUI();
  experimentType.value = "hydraulic";
  experimentName.value = c.experiment_name;
  content.value = c.content;
  statusEl.textContent = `已导入示例：${c.experiment_name}`;
}

function syncUI() {
  const type = checkType.value;
  $("textInput").classList.toggle("hidden", type !== "text");
  $("fileInput").classList.toggle("hidden", type === "text");
  $("experimentNameWrap").classList.toggle("hidden", type !== "text");
  $("fileLabel").textContent = "上传实验图片";
  fileInput.accept = "image/*";
}

populateDemoCases();
importDemoBtn.addEventListener("click", importDemoCase);
checkType.addEventListener("change", syncUI);
syncUI();

function levelClass(level) {
  return level === "pass" ? "pass" : level === "fail" ? "fail" : "warning";
}

function renderReport(data) {
  resultPanel.classList.remove("hidden");
  $("score").textContent = data.score ?? "—";
  const levelEl = $("level");
  levelEl.textContent = data.level ?? "—";
  levelEl.className = `badge value ${levelClass(data.level)}`;
  $("teacherReview").textContent = data.teacher_review_required ? "是" : "否";
  $("summaryText").textContent = data.summary || "";

  const issuesList = $("issuesList");
  issuesList.innerHTML = "";
  if (!data.issues || data.issues.length === 0) {
    issuesList.innerHTML = '<p class="status">未列出具体问题。</p>';
  } else {
    data.issues.forEach((issue) => {
      const card = document.createElement("div");
      card.className = "issue-card";
      card.innerHTML = `
        <div class="head">
          <strong>${issue.category}</strong>
          <span class="severity ${issue.severity}">${issue.severity}</span>
        </div>
        <p><strong>问题：</strong>${issue.problem}</p>
        <p><strong>依据：</strong>${issue.evidence}</p>
        <p><strong>建议：</strong>${issue.suggestion}</p>
        <p><strong>置信度：</strong>${(issue.confidence * 100).toFixed(0)}%</p>
      `;
      issuesList.appendChild(card);
    });
  }

  const keyTitle = $("keyEventsTitle");
  const keyList = $("keyEventsList");
  keyList.innerHTML = "";
  if (data.key_events && data.key_events.length > 0) {
    keyTitle.classList.remove("hidden");
    data.key_events.forEach((ev) => {
      const card = document.createElement("div");
      card.className = "issue-card";
      const [a, b] = ev.time_range || [0, 0];
      card.innerHTML = `
        <p><strong>时间段：</strong>${a}s – ${b}s</p>
        <p><strong>问题：</strong>${ev.problem}</p>
        <p><strong>建议：</strong>${ev.suggestion}</p>
      `;
      keyList.appendChild(card);
    });
  } else {
    keyTitle.classList.add("hidden");
  }

  $("rawJson").textContent = JSON.stringify(data, null, 2);
}

async function runCheck() {
  // 前后端同源部署，直接用当前站点 origin
  const base = window.location.origin.replace(/\/$/, "");
  const type = checkType.value;
  submitBtn.disabled = true;
  statusEl.textContent = "检测中，请稍候…";
  resultPanel.classList.add("hidden");

  try {
    let res;
    if (type === "text") {
      const body = {
        grade: grade.value,
        experiment_name: experimentName.value,
        content: content.value,
      };
      if (!body.content.trim()) {
        throw new Error("请填写实验报告内容");
      }
      res = await fetch(`${base}/api/hydraulic-lab/check-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
    } else {
      const file = fileInput.files[0];
      if (!file) throw new Error("请选择图片");
      const form = new FormData();
      form.append("image", file);
      form.append("experiment_type", experimentType.value);
      form.append("grade", grade.value);
      res = await fetch(`${base}/api/hydraulic-lab/check-image`, {
        method: "POST",
        body: form,
      });
    }

    if (!res.ok) {
      let msg = `请求失败 ${res.status}`;
      const errText = await res.text();
      try {
        const errJson = JSON.parse(errText);
        msg = errJson.detail ?? msg;
        if (Array.isArray(msg)) msg = msg.map((e) => e.msg || e).join("; ");
      } catch {
        if (errText) msg = errText.slice(0, 500);
      }
      throw new Error(msg);
    }
    const data = await res.json();
    renderReport(data);
    statusEl.textContent = "检测完成";
  } catch (e) {
    statusEl.textContent = `错误：${e.message}`;
  } finally {
    submitBtn.disabled = false;
  }
}

submitBtn.addEventListener("click", runCheck);
