"""将大模型返回的 JSON 转为统一检测报告。"""

from app.models import CheckReport, Issue, KeyEvent

DISCLAIMER = (
    "本系统用于辅助教师发现液压与气压传动实验中的问题，"
    "最终判断与评分应由教师完成。"
)


def dict_to_issues(raw: list) -> list[Issue]:
    issues = []
    for item in raw or []:
        try:
            issues.append(Issue(**item))
        except Exception:
            continue
    return issues


def dict_to_key_events(raw: list | None) -> list[KeyEvent] | None:
    if not raw:
        return None
    events = []
    for item in raw:
        try:
            events.append(KeyEvent(**item))
        except Exception:
            continue
    return events or None


def build_ai_report(ai_result: dict, suffix: str = "") -> CheckReport:
    issues = dict_to_issues(ai_result.get("issues"))
    key_events = dict_to_key_events(ai_result.get("key_events"))

    score = int(ai_result.get("score", 0))
    score = max(0, min(100, score))

    level = ai_result.get("level", "warning")
    if level not in ("pass", "warning", "fail"):
        level = "warning"

    teacher_review = bool(ai_result.get("teacher_review_required", False))
    if any(i.severity == "high" or i.category == "安全风险" for i in issues):
        teacher_review = True

    summary = str(ai_result.get("summary") or "大模型检测完成。").strip()
    if DISCLAIMER not in summary:
        summary = f"{DISCLAIMER} {summary}"
    if suffix:
        summary = f"{summary} {suffix}"

    return CheckReport(
        score=score,
        level=level,
        issues=issues,
        teacher_review_required=teacher_review,
        summary=summary,
        key_events=key_events,
    )
