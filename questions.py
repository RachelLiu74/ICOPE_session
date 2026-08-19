# -*- coding: utf-8 -*-
"""ICOPE Warm-up Q&A v3 question bank + team roster.

Question types:
- "mc_ungraded": multiple choice, single-select, NO correct answer.
                 Used purely as a warm-up opinion poll (Q1-5).
- "mc_single":   multiple choice, single-select, scored (Q6-8).
- "mc_multi":    multiple choice, multi-select (checkboxes), scored.
                 Correct if the student's selected set exactly matches
                 the "correct" set (Q9-10).

Correct answers are only ever read on the server; the public
`/api/questions` endpoint strips the "correct" field before sending
question data to the browser.
"""

TEAMS = [
    {
        "id": "t1",
        "name": "知食份子:你的專屬營養師",
        "tag": "Edge AI",
        "project": "邊緣AI整合飲食建議平台",
    },
    {
        "id": "t2",
        "name": "使命必達搬蟲工-Buffet 吃到飽",
        "tag": "物聯網/機器人",
        "project": "智慧昆蟲養殖自主搬運與排程管理機器人",
    },
    {
        "id": "t3",
        "name": "Error 404: Team Not Found",
        "tag": "Edge AI",
        "project": "具備虛實訓練的智慧Edge AI 桌球拍",
    },
    {
        "id": "t4",
        "name": "癡心絕隊",
        "tag": "物聯網",
        "project": "具備主動式職安監測之智慧型物聯網系統",
    },
    {
        "id": "t5",
        "name": "台灣の翼",
        "tag": "無人機",
        "project": "聯翼共巡：具多模態感知之國產晶片輕量化提升河川污染巡檢效率無人機系統",
    },
    {
        "id": "t6",
        "name": "比飛多",
        "tag": "無人機",
        "project": "國產 UP301FCB AI 飛控板於無人機智慧巡檢任務之應用驗證型 Demo",
    },
    {
        "id": "t7",
        "name": "聽見你的心",
        "tag": "穿戴裝置",
        "project": "",
    },
    {
        "id": "t8",
        "name": "其他",
        "tag": "",
        "project": "",
    },
]

TEAM_LOOKUP = {t["id"]: t for t in TEAMS}


# ---------------------------------------------------------------------
# Q1-5: opinion-poll multiple choice, ICOPE warm-up, no correct answer
# ---------------------------------------------------------------------
UNGRADED_QUESTIONS = [
    {
        "id": "q1",
        "type": "mc_ungraded",
        "section": "PART 1 · 想法投票（無標準答案）",
        "text": "你覺得台灣邁入「超高齡社會」的時間點，大概是？",
        "options": {
            "A": "已經是了",
            "B": "2025 年前後",
            "C": "2030 年後",
            "D": "還很久",
        },
    },
    {
        "id": "q2",
        "type": "mc_ungraded",
        "section": "PART 1 · 想法投票（無標準答案）",
        "text": "你覺得長輩最不願意承認自己需要「照護」的原因是？",
        "options": {
            "A": "覺得麻煩別人",
            "B": "覺得自己還很健康",
            "C": "擔心失去自主權",
            "D": "不知道有哪些資源",
        },
    },
    {
        "id": "q3",
        "type": "mc_ungraded",
        "section": "PART 1 · 想法投票（無標準答案）",
        "text": "如果要用一種科技幫助長輩維持社交，你會優先選擇？",
        "options": {
            "A": "穿戴裝置",
            "B": "陪伴機器人",
            "C": "視訊 / 社群軟體",
            "D": "智慧喇叭語音助理",
        },
    },
    {
        "id": "q4",
        "type": "mc_ungraded",
        "section": "PART 1 · 想法投票（無標準答案）",
        "text": "你覺得團隊報告中，最容易被忽略的照護面向是？",
        "options": {
            "A": "認知",
            "B": "心理健康",
            "C": "聽力 / 視力",
            "D": "營養",
        },
    },
    {
        "id": "q5",
        "type": "mc_ungraded",
        "section": "PART 1 · 想法投票（無標準答案）",
        "text": "你認為「以人為中心」的智慧照護服務，最重要的成功關鍵是？",
        "options": {
            "A": "技術先進",
            "B": "長輩願意持續使用",
            "C": "成本低廉",
            "D": "資料量大",
        },
    },
]


# ---------------------------------------------------------------------
# Q6-8: single-choice, scored
# ---------------------------------------------------------------------
SINGLE_QUESTIONS = [
    {
        "id": "q6",
        "type": "mc_single",
        "section": "PART 2 · 選擇題（單選，會計分）",
        "text": "ICOPE 六力中，哪一項與「肌少症、跌倒風險」最直接相關？",
        "options": {
            "A": "認知力",
            "B": "行動力",
            "C": "聽力",
            "D": "心理健康",
        },
        "correct": "B",
        "explain": "行動力（Locomotion）涵蓋肌力、平衡與步態，與肌少症、跌倒風險直接相關。",
    },
    {
        "id": "q7",
        "type": "mc_single",
        "section": "PART 2 · 選擇題（單選，會計分）",
        "text": "WHO 提出 ICOPE 框架的主要目的是？",
        "options": {
            "A": "治療癌症的臨床指引",
            "B": "以社區為基礎，提供長者整合式照護",
            "C": "疫苗接種排程",
            "D": "兒童發展篩檢工具",
        },
        "correct": "B",
        "explain": "ICOPE 目的是在社區與基層場域，及早發現並整合照護長者的內在能力衰退。",
    },
    {
        "id": "q8",
        "type": "mc_single",
        "section": "PART 2 · 選擇題（單選，會計分）",
        "text": "下列何者最符合「以人為中心」的照護精神？",
        "options": {
            "A": "只依檢驗數據做決定",
            "B": "尊重長者本人的意願與生活目標",
            "C": "完全由醫護人員決定治療方式",
            "D": "忽略家屬與長者的想法",
        },
        "correct": "B",
        "explain": "以人為中心強調尊重長者本人意願、生活目標與偏好，而非只看數據或單方面決定。",
    },
]


# ---------------------------------------------------------------------
# Q9-10: multi-select, scored (exact set match required)
# ---------------------------------------------------------------------
MULTI_QUESTIONS = [
    {
        "id": "q9",
        "type": "mc_multi",
        "section": "PART 3 · 複選題（會計分）",
        "text": "ICOPE 六大內在能力包含下列哪些？（複選，請選出全部正確選項）",
        "options": {
            "A": "認知力",
            "B": "行動力",
            "C": "財務能力",
            "D": "營養與活力",
            "E": "視力",
            "F": "聽力",
            "G": "心理健康",
            "H": "睡眠品質",
        },
        "correct": ["A", "B", "D", "E", "F", "G"],
        "explain": "ICOPE 六力為：認知力、行動力、營養與活力、視力、聽力、心理健康；財務能力與睡眠品質不在六力之列。",
    },
    {
        "id": "q10",
        "type": "mc_multi",
        "section": "PART 3 · 複選題（會計分）",
        "text": "下列哪些是 ICOPE 照護路徑中會出現的步驟？（複選，請選出全部正確選項）",
        "options": {
            "A": "篩檢",
            "B": "評估",
            "C": "擬定個別化照護計畫",
            "D": "追蹤與社區資源連結",
            "E": "忽略直到重症",
            "F": "立即開刀",
        },
        "correct": ["A", "B", "C", "D"],
        "explain": "ICOPE 照護路徑為：篩檢 → 評估 → 擬定個別化照護計畫 → 追蹤與社區資源連結，強調早期介入而非等到重症。",
    },
]

ALL_QUESTIONS = UNGRADED_QUESTIONS + SINGLE_QUESTIONS + MULTI_QUESTIONS
