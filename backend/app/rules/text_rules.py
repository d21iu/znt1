# 已弃用：检测逻辑全部由大模型完成，本文件仅作教学参考保留。
import re

from app.models import Issue

UNIT_PATTERN = re.compile(
    r"(MPa|mpa|bar|kPa|Pa|L/min|l/min|m³/h|mm/s|r/min|rpm|kW|kW|℃|°C|mm|cm|m\b)",
    re.IGNORECASE,
)
NUMBER_WITH_CONTEXT = re.compile(r"[\d.]+\s*(MPa|bar|L/min|mm|kW|r/min)", re.I)

HIGH_RISK_KEYWORDS = [
    "带压拆",
    "带压卸",
    "未泄压",
    "超压",
    "爆裂",
    "喷油",
    "高压气体直射",
    "不泄压",
]

SECTION_KEYWORDS = {
    "实验目的": ["实验目的", "目的：", "目的:"],
    "实验原理": ["实验原理", "原理：", "原理:"],
    "实验步骤": ["实验步骤", "步骤：", "步骤:", "操作步骤"],
    "实验数据": ["实验数据", "数据记录", "数据：", "数据:"],
    "误差分析": ["误差分析", "误差", "不确定度", "相对误差"],
    "结论": ["结论", "实验结论", "小结"],
    "安全": ["安全", "泄压", "护目镜", "注意事项"],
}


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(k in text for k in keywords)


def run_text_rules(content: str) -> list[Issue]:
    issues: list[Issue] = []
    text = content.strip()
    if not text:
        issues.append(
            Issue(
                category="内容完整性",
                severity="high",
                problem="实验报告内容为空。",
                evidence="未收到任何文本。",
                suggestion="请填写完整的实验报告后再提交。",
                confidence=1.0,
            )
        )
        return issues

    for section, keywords in SECTION_KEYWORDS.items():
        if section == "安全":
            continue
        if not _contains_any(text, keywords):
            issues.append(
                Issue(
                    category="结构完整性",
                    severity="medium" if section in ("实验目的", "实验步骤") else "low",
                    problem=f"未检测到「{section}」相关表述。",
                    evidence=f"全文检索未匹配：{', '.join(keywords[:2])}…",
                    suggestion=f"建议补充{section}部分。",
                    confidence=0.85,
                )
            )

    if _contains_any(text, ["实验数据", "数据", "压力", "流量", "行程", "时间"]):
        has_units = bool(UNIT_PATTERN.search(text)) or bool(NUMBER_WITH_CONTEXT.search(text))
        bare_numbers = re.findall(r"(?:压力|流量|行程|时间|转速)[：:]\s*[\d.]+", text)
        if bare_numbers and not has_units:
            issues.append(
                Issue(
                    category="数据记录",
                    severity="medium",
                    problem="实验数据可能缺少单位。",
                    evidence="；".join(bare_numbers[:3]),
                    suggestion="建议为压力、流量、行程等数据补充 MPa、L/min、mm、s 等单位。",
                    confidence=0.8,
                )
            )

    if not _contains_any(text, SECTION_KEYWORDS["误差分析"]):
        if _contains_any(text, SECTION_KEYWORDS["实验数据"]):
            issues.append(
                Issue(
                    category="分析完整性",
                    severity="low",
                    problem="未检测到误差分析或结果讨论。",
                    evidence="报告中未见“误差分析”“不确定度”等关键词。",
                    suggestion="建议补充误差来源、仪表精度及对结论的影响。",
                    confidence=0.75,
                )
            )

    if not _contains_any(text, SECTION_KEYWORDS["安全"]):
        issues.append(
            Issue(
                category="安全规范",
                severity="low",
                problem="未提及实验安全注意事项。",
                evidence="未检测到泄压、护目镜、防喷等安全相关描述。",
                suggestion="建议补充本实验的安全操作要点（如泄压后拆装、佩戴护具）。",
                confidence=0.7,
            )
        )

    for kw in HIGH_RISK_KEYWORDS:
        if kw in text:
            issues.append(
                Issue(
                    category="安全风险",
                    severity="high",
                    problem=f"报告描述涉及高风险操作：「{kw}」。",
                    evidence=f"原文包含：{kw}",
                    suggestion="此类操作需教师现场确认；若仅为警示说明，请明确安全规程。",
                    confidence=0.9,
                )
            )

    return issues


def score_from_issues(issues: list[Issue]) -> tuple[int, str, bool]:
    score = 100
    teacher_review = False
    max_severity = "low"

    severity_penalty = {"low": 5, "medium": 12, "high": 25}
    for issue in issues:
        score -= severity_penalty.get(issue.severity, 8)
        if issue.severity == "high":
            max_severity = "high"
            teacher_review = True
        elif issue.severity == "medium" and max_severity != "high":
            max_severity = "medium"
        if issue.category == "安全风险":
            teacher_review = True

    score = max(0, min(100, score))
    if score >= 85 and max_severity == "low":
        level = "pass"
    elif score >= 60:
        level = "warning"
    else:
        level = "fail"
    return score, level, teacher_review
