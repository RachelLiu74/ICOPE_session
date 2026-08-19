(() => {
  "use strict";

  const state = {
    questions: [],
    teams: [],
    ungradedQuestions: [],
    singleQuestions: [],
    multiQuestions: [],
    name: "",
    teamId: "",
    studentCode: "",
    startTime: null,
    ungradedAnswers: {}, // question_id -> option key
    singleAnswers: {}, // question_id -> option key
    multiAnswers: {}, // question_id -> Set of option keys
    teacherToken: null,
  };

  // ---------- view switching ----------
  function showView(id) {
    document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
    document.getElementById(id).classList.add("active");
  }

  // ---------- helpers ----------
  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  async function apiFetch(path, options = {}) {
    const res = await fetch(path, options);
    let data = null;
    try {
      data = await res.json();
    } catch (e) {
      data = null;
    }
    if (!res.ok) {
      const message = (data && data.error) || `請求失敗 (${res.status})`;
      throw new Error(message);
    }
    return data;
  }

  // ---------- load questions & teams ----------
  async function loadQuestions() {
    const list = await apiFetch("/api/questions");
    state.questions = list;
    state.ungradedQuestions = list.filter((q) => q.type === "mc_ungraded");
    state.singleQuestions = list.filter((q) => q.type === "mc_single");
    state.multiQuestions = list.filter((q) => q.type === "mc_multi");
  }

  async function loadTeams() {
    const teams = await apiFetch("/api/teams");
    state.teams = teams;
    const select = document.getElementById("input-team");
    teams.forEach((t) => {
      const opt = document.createElement("option");
      opt.value = t.id;
      opt.textContent = t.project ? `${t.name}（${t.tag}：${t.project}）` : `${t.name}（${t.tag}）`;
      select.appendChild(opt);
    });
  }

  // ---------- landing ----------
  document.getElementById("btn-role-student").addEventListener("click", () => {
    document.getElementById("student-login-error").textContent = "";
    showView("view-student-login");
  });
  document.getElementById("btn-role-teacher").addEventListener("click", () => {
    document.getElementById("teacher-login-error").textContent = "";
    showView("view-teacher-login");
  });
  document.getElementById("btn-back-from-student-login").addEventListener("click", () => showView("view-landing"));
  document.getElementById("btn-back-from-teacher-login").addEventListener("click", () => showView("view-landing"));
  document.getElementById("btn-back-landing").addEventListener("click", () => showView("view-landing"));

  // ---------- student: start quiz ----------
  document.getElementById("btn-start-quiz").addEventListener("click", async () => {
    const errEl = document.getElementById("student-login-error");
    const name = document.getElementById("input-name").value.trim();
    const teamId = document.getElementById("input-team").value;
    const studentCode = document.getElementById("input-code").value.trim();
    if (!name) {
      errEl.textContent = "請輸入姓名";
      return;
    }
    if (!teamId) {
      errEl.textContent = "請選擇組別";
      return;
    }
    errEl.textContent = "";
    state.name = name;
    state.teamId = teamId;
    state.studentCode = studentCode;
    state.ungradedAnswers = {};
    state.singleAnswers = {};
    state.multiAnswers = {};

    try {
      if (state.questions.length === 0) {
        await loadQuestions();
      }
    } catch (e) {
      errEl.textContent = "載入題目失敗，請確認伺服器是否啟動";
      return;
    }

    state.startTime = new Date().toISOString();
    renderPart1();
    showView("view-part1");
  });

  // ---------- Part 1: ungraded opinion-poll questions (single-select) ----------
  function renderPart1() {
    const container = document.getElementById("open-questions");
    container.innerHTML = "";
    state.ungradedQuestions.forEach((q, idx) => {
      const block = el("div", "question-block");
      block.appendChild(el("div", "question-label", `想法投票 ${idx + 1} / ${state.ungradedQuestions.length}`));
      block.appendChild(el("div", "question-text", q.text));
      const optWrap = el("div", "mc-options");
      Object.keys(q.options).forEach((key) => {
        const opt = el("div", "mc-opt");
        opt.dataset.key = key;
        opt.appendChild(el("b", null, key));
        opt.appendChild(el("span", null, q.options[key]));
        opt.addEventListener("click", () => {
          state.ungradedAnswers[q.id] = key;
          Array.from(optWrap.children).forEach((c) => c.classList.remove("selected"));
          opt.classList.add("selected");
        });
        optWrap.appendChild(opt);
      });
      block.appendChild(optWrap);
      container.appendChild(block);
    });
    document.getElementById("part1-progress").textContent = `共 ${state.ungradedQuestions.length} 題，皆可留空`;
  }

  document.getElementById("btn-to-part2").addEventListener("click", () => {
    renderPart2();
    showView("view-part2");
  });
  document.getElementById("btn-back-to-part1").addEventListener("click", () => showView("view-part1"));

  // ---------- Part 2-3: single-select (Q6-8) + multi-select (Q9-10), scored ----------
  function renderPart2() {
    const container = document.getElementById("mc-questions");
    container.innerHTML = "";
    let qNum = state.ungradedQuestions.length;

    state.singleQuestions.forEach((q) => {
      qNum += 1;
      const block = el("div", "question-block");
      block.appendChild(el("div", "question-label", `單選題 · Q${qNum}`));
      block.appendChild(el("div", "question-text", q.text));
      const optWrap = el("div", "mc-options");
      Object.keys(q.options).forEach((key) => {
        const opt = el("div", "mc-opt");
        opt.dataset.key = key;
        opt.appendChild(el("b", null, key));
        opt.appendChild(el("span", null, q.options[key]));
        opt.addEventListener("click", () => {
          state.singleAnswers[q.id] = key;
          Array.from(optWrap.children).forEach((c) => c.classList.remove("selected"));
          opt.classList.add("selected");
        });
        optWrap.appendChild(opt);
      });
      block.appendChild(optWrap);
      container.appendChild(block);
    });

    state.multiQuestions.forEach((q) => {
      qNum += 1;
      if (!state.multiAnswers[q.id]) state.multiAnswers[q.id] = new Set();
      const block = el("div", "question-block");
      block.appendChild(el("div", "question-label", `複選題（可選多項）· Q${qNum}`));
      block.appendChild(el("div", "question-text", q.text));
      const optWrap = el("div", "mc-options");
      Object.keys(q.options).forEach((key) => {
        const opt = el("div", "mc-opt");
        opt.dataset.key = key;
        opt.appendChild(el("b", null, key));
        opt.appendChild(el("span", null, q.options[key]));
        opt.addEventListener("click", () => {
          const set = state.multiAnswers[q.id];
          if (set.has(key)) {
            set.delete(key);
            opt.classList.remove("selected");
          } else {
            set.add(key);
            opt.classList.add("selected");
          }
        });
        optWrap.appendChild(opt);
      });
      block.appendChild(optWrap);
      container.appendChild(block);
    });
  }

  document.getElementById("btn-submit-quiz").addEventListener("click", async () => {
    const errEl = document.getElementById("submit-error");

    const missingSingle = state.singleQuestions.filter((q) => !state.singleAnswers[q.id]);
    const missingMulti = state.multiQuestions.filter(
      (q) => !state.multiAnswers[q.id] || state.multiAnswers[q.id].size === 0
    );
    if (missingSingle.length > 0 || missingMulti.length > 0) {
      errEl.textContent = `還有 ${missingSingle.length + missingMulti.length} 題選擇題尚未作答`;
      return;
    }
    errEl.textContent = "";

    const answers = [];
    state.ungradedQuestions.forEach((q) => {
      answers.push({ question_id: q.id, value: state.ungradedAnswers[q.id] || "" });
    });
    state.singleQuestions.forEach((q) => {
      answers.push({ question_id: q.id, value: state.singleAnswers[q.id] });
    });
    state.multiQuestions.forEach((q) => {
      answers.push({ question_id: q.id, value: Array.from(state.multiAnswers[q.id]) });
    });

    const submitBtn = document.getElementById("btn-submit-quiz");
    submitBtn.disabled = true;
    try {
      const result = await apiFetch("/api/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: state.name,
          team_id: state.teamId,
          student_code: state.studentCode,
          start_time: state.startTime,
          answers,
        }),
      });
      renderResult(result);
      showView("view-result");
    } catch (e) {
      errEl.textContent = e.message;
    } finally {
      submitBtn.disabled = false;
    }
  });

  function renderResult(result) {
    document.getElementById("result-score").textContent = `${result.score} / ${result.total_scored}`;
    document.getElementById("result-duration").textContent = `作答時間：約 ${Math.round(result.duration_seconds)} 秒`;

    const detail = document.getElementById("result-detail");
    detail.innerHTML = "";
    const scoredQuestions = [...state.singleQuestions, ...state.multiQuestions];
    result.results.forEach((r, idx) => {
      const q = scoredQuestions.find((sq) => sq.id === r.question_id);
      const item = el("div", `result-item ${r.correct ? "correct" : "wrong"}`);
      item.appendChild(el("span", "tag", r.correct ? "✔" : "✘"));
      const textWrap = el("div");
      textWrap.appendChild(el("div", null, `Q${idx + 1}：${q ? q.text : r.question_id}`));
      const correctLabel = q
        ? r.correct_answer
            .split(",")
            .map((k) => `${k} ${q.options[k] || ""}`)
            .join("、")
        : r.correct_answer;
      textWrap.appendChild(el("div", "muted", `正確答案：${correctLabel}`));
      if (r.explain) textWrap.appendChild(el("div", "muted", r.explain));
      item.appendChild(textWrap);
      detail.appendChild(item);
    });
  }

  // ---------- teacher: login ----------
  document.getElementById("btn-teacher-login").addEventListener("click", async () => {
    const errEl = document.getElementById("teacher-login-error");
    const password = document.getElementById("input-teacher-password").value;
    errEl.textContent = "";
    try {
      const result = await apiFetch("/api/teacher/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
      state.teacherToken = result.token;
      document.getElementById("input-teacher-password").value = "";
      await refreshStats();
      showView("view-teacher-dashboard");
    } catch (e) {
      errEl.textContent = e.message;
    }
  });

  document.getElementById("btn-teacher-logout").addEventListener("click", async () => {
    try {
      await apiFetch("/api/teacher/logout", {
        method: "POST",
        headers: { Authorization: `Bearer ${state.teacherToken}` },
      });
    } catch (e) {
      // ignore
    }
    state.teacherToken = null;
    showView("view-landing");
  });

  document.getElementById("btn-refresh-stats").addEventListener("click", refreshStats);

  async function refreshStats() {
    if (!state.teacherToken) return;
    let stats;
    try {
      stats = await apiFetch("/api/teacher/stats", {
        headers: { Authorization: `Bearer ${state.teacherToken}` },
      });
    } catch (e) {
      document.getElementById("teacher-login-error").textContent = e.message;
      showView("view-teacher-login");
      return;
    }
    renderOverview(stats);
    renderQuestionStats(stats.questions);
  }

  function renderOverview(stats) {
    const container = document.getElementById("overview-cards");
    container.innerHTML = "";
    const totalScored = state.singleQuestions.length + state.multiQuestions.length || 5;
    const cards = [
      ["作答人數", stats.participant_count],
      ["平均分數（選擇題）", `${stats.avg_score} / ${totalScored}`],
      ["平均作答時間", `${stats.avg_duration_seconds} 秒`],
      ["最短 / 最長時間", `${stats.min_duration_seconds}s / ${stats.max_duration_seconds}s`],
    ];
    cards.forEach(([label, value]) => {
      const card = el("div", "overview-card");
      card.appendChild(el("div", "label", label));
      card.appendChild(el("div", "value", String(value)));
      container.appendChild(card);
    });

    if (stats.team_breakdown && stats.team_breakdown.length) {
      const teamCard = el("div", "overview-card");
      teamCard.appendChild(el("div", "label", "各組作答人數"));
      const value = el("div", "value");
      value.style.fontSize = "14px";
      stats.team_breakdown.forEach((t) => {
        value.appendChild(el("div", null, `${t.team_name}：${t.count} 人`));
      });
      teamCard.appendChild(value);
      container.appendChild(teamCard);
    }
  }

  const SECTION_LABELS = {
    mc_ungraded: "想法投票",
    mc_single: "單選題",
    mc_multi: "複選題",
  };

  function renderQuestionStats(questions) {
    const container = document.getElementById("question-stats");
    container.innerHTML = "";
    questions.forEach((q, idx) => {
      const card = el("div", "qstat-card");
      const tagClass = q.type === "mc_ungraded" ? "open" : "mc";
      const tag = el("span", `section-tag ${tagClass}`, SECTION_LABELS[q.type] || q.type);
      card.appendChild(tag);
      card.appendChild(el("h3", null, `Q${idx + 1}：${q.text}`));

      const correctSet = q.type === "mc_multi" && q.correct_answer ? q.correct_answer.split(",") : [];

      q.options.forEach((opt) => {
        const isCorrect =
          q.type === "mc_single" ? opt.key === q.correct_answer : q.type === "mc_multi" ? correctSet.includes(opt.key) : false;
        const row = el("div", "bar-row");
        row.appendChild(el("div", `bar-label${isCorrect ? " is-correct" : ""}`, opt.key));
        const track = el("div", "bar-track");
        const fill = el("div", `bar-fill${isCorrect ? " is-correct" : ""}`);
        fill.style.width = `${opt.pct}%`;
        track.appendChild(fill);
        row.appendChild(track);
        row.appendChild(el("div", "bar-count", `${opt.count} 人 (${opt.pct}%)`));
        card.appendChild(row);
      });

      if (q.type === "mc_ungraded") {
        card.appendChild(el("p", "muted", `作答人數：${q.response_count}（無標準答案，僅供參考）`));
      } else {
        card.appendChild(
          el(
            "p",
            "muted",
            `作答人數：${q.response_count}　正確率：${q.correct_pct}%（正解：${q.correct_answer}）`
          )
        );
      }
      container.appendChild(card);
    });
  }

  document.getElementById("btn-download-csv").addEventListener("click", async () => {
    if (!state.teacherToken) return;
    try {
      const res = await fetch("/api/teacher/download.csv", {
        headers: { Authorization: `Bearer ${state.teacherToken}` },
      });
      if (!res.ok) throw new Error("下載失敗");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "icope_qa_stats.csv";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e) {
      alert(e.message);
    }
  });

  // preload question bank & team roster so the student flow starts instantly
  Promise.all([loadQuestions(), loadTeams()]).catch(() => {});
})();

