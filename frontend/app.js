const $ = (id) => document.getElementById(id);

const checkType = $("checkType");
const experimentType = $("experimentType");
const grade = $("grade");
const experimentName = $("experimentName");
const frameInterval = $("frameInterval");
const apiBase = $("apiBase");
const content = $("content");
const fileInput = $("file");
const submitBtn = $("submitBtn");
const statusEl = $("status");
const resultPanel = $("result");

function syncUI() {
  const type = checkType.value;
  $("textInput").classList.toggle("hidden", type !== "text");
  $("fileInput").classList.toggle("hidden", type === "text");
  $("experimentNameWrap").classList.toggle("hidden", type !== "text");
  $("frameIntervalWrap").classList.toggle("hidden", type !== "video");
  $("fileLabel").textContent = type === "image" ? "上传实验图片" : "上传操作视频";
  fileInput.accept = type === "image" ? "image/*" : "video/*";
}

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
  // 留空则用同源地址（容器内前后端同端口部署时的默认行为）
  const base = (apiBase.value.trim() || window.location.origin).replace(/\/$/, "");
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
      if (!file) throw new Error("请选择文件");
      const form = new FormData();
      form.append(type === "image" ? "image" : "video", file);
      form.append("experiment_type", experimentType.value);
      form.append("grade", grade.value);
      if (type === "video") {
        form.append("frame_interval", frameInterval.value || "1");
      }
      const path =
        type === "image"
          ? "/api/hydraulic-lab/check-image"
          : "/api/hydraulic-lab/check-video";
      res = await fetch(`${base}${path}`, { method: "POST", body: form });
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
