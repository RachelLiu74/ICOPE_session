# -*- coding: utf-8 -*-
"""ICOPE Warm-up Q&A v3 backend.

Flask app that serves the student/teacher web front-end and stores
student submissions in a local SQLite database, so the teacher can view
aggregated statistics and download them as CSV.

v3 changes:
- Student must pick their team from a required dropdown (student code
  is optional free text).
- Q1-5 are ungraded multiple-choice opinion polls.
- Q6-8 are single-choice scored questions.
- Q9-10 are multi-select (checkbox) scored questions, correct only when
  the selected set exactly matches the answer key.

Run:
    python app.py

Then open http://<this-machine-ip>:5057/ on the classroom network.
Teacher login password: 17383
"""
import csv
import hmac
import io
import os
import secrets
import sqlite3
import time
from datetime import datetime, timezone
from functools import wraps

from flask import Flask, Response, g, jsonify, render_template, request

from questions import ALL_QUESTIONS, TEAM_LOOKUP, TEAMS

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "icope_qa.db")

TEACHER_PASSWORD = "17383"
TOKEN_TTL_SECONDS = 4 * 60 * 60  # teacher session valid for 4 hours

MAX_NAME_LEN = 60
MAX_CODE_LEN = 40

app = Flask(__name__)

# In-memory teacher session tokens: token -> expiry unix timestamp.
# Simple by design (single-classroom tool); cleared on server restart.
_teacher_tokens = {}

_QUESTION_LOOKUP = {q["id"]: q for q in ALL_QUESTIONS}


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            team_id TEXT NOT NULL,
            team_name TEXT NOT NULL,
            student_code TEXT,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            duration_seconds REAL NOT NULL,
            score INTEGER NOT NULL,
            total_scored INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER NOT NULL,
            question_id TEXT NOT NULL,
            question_type TEXT NOT NULL,
            answer_value TEXT,
            is_correct INTEGER,
            FOREIGN KEY (submission_id) REFERENCES submissions(id)
        )
        """
    )
    conn.commit()
    conn.close()


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def issue_teacher_token():
    token = secrets.token_hex(16)
    _teacher_tokens[token] = time.time() + TOKEN_TTL_SECONDS
    return token


def require_teacher(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "unauthorized"}), 401
        token = auth[len("Bearer "):]
        expiry = _teacher_tokens.get(token)
        if not expiry or expiry < time.time():
            _teacher_tokens.pop(token, None)
            return jsonify({"error": "unauthorized"}), 401
        return fn(*args, **kwargs)

    return wrapper


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/questions")
def api_questions():
    """Public question list. Correct answers are never sent to the client."""
    public = []
    for q in ALL_QUESTIONS:
        item = {
            "id": q["id"],
            "type": q["type"],
            "section": q["section"],
            "text": q["text"],
            "options": q["options"],
        }
        public.append(item)
    return jsonify(public)


@app.route("/api/teams")
def api_teams():
    """Public team roster for the required student dropdown."""
    return jsonify(
        [
            {"id": t["id"], "name": t["name"], "tag": t["tag"], "project": t["project"]}
            for t in TEAMS
        ]
    )


@app.route("/api/submit", methods=["POST"])
def api_submit():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name") or "").strip()
    team_id = str(data.get("team_id") or "").strip()
    student_code = str(data.get("student_code") or "").strip()
    start_time = data.get("start_time")
    answers = data.get("answers")

    if not name:
        return jsonify({"error": "請輸入姓名"}), 400
    if len(name) > MAX_NAME_LEN:
        return jsonify({"error": "姓名過長"}), 400
    team = TEAM_LOOKUP.get(team_id)
    if not team:
        return jsonify({"error": "請選擇組別"}), 400
    if len(student_code) > MAX_CODE_LEN:
        return jsonify({"error": "代號過長"}), 400
    if not isinstance(answers, list) or not answers:
        return jsonify({"error": "缺少作答內容"}), 400
    if not isinstance(start_time, str):
        return jsonify({"error": "缺少開始作答時間"}), 400

    try:
        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    except ValueError:
        return jsonify({"error": "開始作答時間格式錯誤"}), 400

    end_dt = datetime.now(timezone.utc)
    duration = max(0.0, (end_dt - start_dt).total_seconds())

    score = 0
    total_scored = 0
    rows = []
    results = []
    seen_ids = set()

    for a in answers:
        if not isinstance(a, dict):
            continue
        qid = a.get("question_id")
        q = _QUESTION_LOOKUP.get(qid)
        if not q or qid in seen_ids:
            continue
        seen_ids.add(qid)
        raw_value = a.get("value")

        if q["type"] == "mc_ungraded":
            value = str(raw_value or "").strip().upper()
            if value not in q["options"]:
                value = ""
            rows.append((qid, q["type"], value, None))

        elif q["type"] == "mc_single":
            total_scored += 1
            value = str(raw_value or "").strip().upper()
            is_correct = 1 if value == q["correct"] else 0
            score += is_correct
            rows.append((qid, q["type"], value, is_correct))
            results.append(
                {
                    "question_id": qid,
                    "correct": bool(is_correct),
                    "correct_answer": q["correct"],
                    "explain": q.get("explain", ""),
                }
            )

        elif q["type"] == "mc_multi":
            total_scored += 1
            if isinstance(raw_value, list):
                selected = sorted({str(v).strip().upper() for v in raw_value if str(v).strip()})
            else:
                selected = []
            selected = [k for k in selected if k in q["options"]]
            is_correct = 1 if selected == sorted(q["correct"]) else 0
            score += is_correct
            rows.append((qid, q["type"], ",".join(selected), is_correct))
            results.append(
                {
                    "question_id": qid,
                    "correct": bool(is_correct),
                    "correct_answer": ",".join(sorted(q["correct"])),
                    "your_answer": ",".join(selected),
                    "explain": q.get("explain", ""),
                }
            )

    if total_scored == 0:
        return jsonify({"error": "沒有作答任何計分題目"}), 400

    db = get_db()
    cur = db.execute(
        "INSERT INTO submissions "
        "(name, team_id, team_name, student_code, start_time, end_time, "
        "duration_seconds, score, total_scored, created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            name[:MAX_NAME_LEN],
            team["id"],
            team["name"],
            student_code[:MAX_CODE_LEN],
            start_dt.isoformat(),
            end_dt.isoformat(),
            duration,
            score,
            total_scored,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    submission_id = cur.lastrowid
    for qid, qtype, value, is_correct in rows:
        db.execute(
            "INSERT INTO answers (submission_id, question_id, question_type, answer_value, is_correct) "
            "VALUES (?,?,?,?,?)",
            (submission_id, qid, qtype, value, is_correct),
        )
    db.commit()

    return jsonify(
        {
            "score": score,
            "total_scored": total_scored,
            "duration_seconds": round(duration, 1),
            "results": results,
        }
    )


@app.route("/api/teacher/login", methods=["POST"])
def teacher_login():
    data = request.get_json(silent=True) or {}
    password = str(data.get("password") or "")
    if not hmac.compare_digest(password, TEACHER_PASSWORD):
        return jsonify({"error": "密碼錯誤"}), 401
    return jsonify({"token": issue_teacher_token()})


@app.route("/api/teacher/logout", methods=["POST"])
@require_teacher
def teacher_logout():
    auth = request.headers.get("Authorization", "")
    token = auth[len("Bearer "):]
    _teacher_tokens.pop(token, None)
    return jsonify({"ok": True})


@app.route("/api/teacher/stats")
@require_teacher
def teacher_stats():
    db = get_db()
    submissions = db.execute("SELECT * FROM submissions ORDER BY id").fetchall()
    participant_count = len(submissions)

    avg_score = avg_duration = min_duration = max_duration = 0.0
    if participant_count:
        scores = [s["score"] for s in submissions]
        durations = [s["duration_seconds"] for s in submissions]
        avg_score = sum(scores) / participant_count
        avg_duration = sum(durations) / participant_count
        min_duration = min(durations)
        max_duration = max(durations)

    team_counts = {}
    for s in submissions:
        team_counts[s["team_name"]] = team_counts.get(s["team_name"], 0) + 1
    team_breakdown = [{"team_name": k, "count": v} for k, v in team_counts.items()]

    question_stats = []
    for q in ALL_QUESTIONS:
        answer_rows = db.execute(
            "SELECT answers.answer_value AS answer_value, answers.is_correct AS is_correct, "
            "submissions.name AS student_name "
            "FROM answers JOIN submissions ON submissions.id = answers.submission_id "
            "WHERE answers.question_id = ?",
            (q["id"],),
        ).fetchall()

        total = len(answer_rows)
        counts = {k: 0 for k in q["options"]}
        for row in answer_rows:
            if q["type"] == "mc_multi":
                selected = [v for v in (row["answer_value"] or "").split(",") if v]
            else:
                selected = [row["answer_value"]] if row["answer_value"] else []
            for k in selected:
                if k in counts:
                    counts[k] += 1

        options_out = [
            {
                "key": k,
                "label": q["options"][k],
                "count": counts[k],
                "pct": round(counts[k] / total * 100, 1) if total else 0,
            }
            for k in q["options"]
        ]

        entry = {
            "id": q["id"],
            "type": q["type"],
            "section": q["section"],
            "text": q["text"],
            "response_count": total,
            "options": options_out,
        }

        if q["type"] in ("mc_single", "mc_multi"):
            correct_count = sum(1 for row in answer_rows if row["is_correct"])
            entry["correct_answer"] = (
                q["correct"] if q["type"] == "mc_single" else ",".join(sorted(q["correct"]))
            )
            entry["correct_count"] = correct_count
            entry["correct_pct"] = round(correct_count / total * 100, 1) if total else 0

        question_stats.append(entry)

    return jsonify(
        {
            "participant_count": participant_count,
            "avg_score": round(avg_score, 2),
            "avg_duration_seconds": round(avg_duration, 1),
            "min_duration_seconds": round(min_duration, 1),
            "max_duration_seconds": round(max_duration, 1),
            "team_breakdown": team_breakdown,
            "questions": question_stats,
        }
    )


@app.route("/api/teacher/download.csv")
@require_teacher
def teacher_download_csv():
    db = get_db()
    submissions = db.execute("SELECT * FROM submissions ORDER BY id").fetchall()
    answers = db.execute("SELECT * FROM answers ORDER BY submission_id").fetchall()

    answers_by_submission = {}
    for row in answers:
        answers_by_submission.setdefault(row["submission_id"], {})[row["question_id"]] = row

    output = io.StringIO()
    writer = csv.writer(output)

    header = [
        "submission_id", "name", "team_name", "student_code",
        "start_time", "end_time", "duration_seconds", "score", "total_scored",
    ]
    for q in ALL_QUESTIONS:
        header.append(q["id"])
        if q["type"] in ("mc_single", "mc_multi"):
            header.append(q["id"] + "_correct")
    writer.writerow(header)

    for s in submissions:
        row = [
            s["id"], s["name"], s["team_name"], s["student_code"],
            s["start_time"], s["end_time"], s["duration_seconds"], s["score"], s["total_scored"],
        ]
        sub_answers = answers_by_submission.get(s["id"], {})
        for q in ALL_QUESTIONS:
            a = sub_answers.get(q["id"])
            row.append(a["answer_value"] if a else "")
            if q["type"] in ("mc_single", "mc_multi"):
                row.append(a["is_correct"] if a and a["is_correct"] is not None else "")
        writer.writerow(row)

    csv_bytes = ("\ufeff" + output.getvalue()).encode("utf-8")
    filename = f"icope_qa_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        csv_bytes,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# Initialize the database as soon as the module is imported so that
# production WSGI servers (e.g. gunicorn on Render/Railway), which import
# `app` directly instead of running this file, still get the tables created.
init_db()

if __name__ == "__main__":
    # host=0.0.0.0 so students on the same classroom network can connect
    # via this machine's LAN IP; debug is kept off for security.
    # PORT env var is honored for cloud hosts (Render/Railway); defaults to
    # 5057 locally because 5000 is already occupied by an unrelated service
    # on this machine.
    port = int(os.environ.get("PORT", 5057))
    app.run(host="0.0.0.0", port=port, debug=False)
