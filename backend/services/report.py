from core.models import ValidationResult

def generate_markdown_report(validations: list[ValidationResult]) -> str:
    """
    Takes a list of ValidationResults and formats them into a beautiful,
    human-readable Markdown report with an API Health Score.
    """
    total = len(validations)
    passed = sum(1 for v in validations if v.passed)
    
    # Calculate Health Score & Grouping
    health_score = 100
    
    critical_failures = []       # 500s
    doc_mismatches = []          # e.g., expected 200, got 201
    validation_failures = []     # 400s, 415s, etc.
    performance_warnings = []    # SLA breached
    false_positives = []         # 404s
    passed_tests = []
    
    for val in validations:
        res = val.test_result
        name = res.test_case.name
        route = f"`{res.test_case.endpoint.method} {res.test_case.endpoint.path}`"
        
        if val.passed:
            passed_tests.append(f"- ✅ **PASS** | {name} ({route})")
            continue
            
        reason = val.failure_reason
        actual = res.actual_status
        expected = res.test_case.expected_status
        
        # Categorization and Scoring
        if "Performance SLA" in reason:
            health_score -= 2
            performance_warnings.append(f"- ⚠️ **SLOW** | {name} ({route})\n  - {reason}")
        elif actual >= 500:
            health_score -= 10
            critical_failures.append(f"- 🚨 **CRITICAL** | {name} ({route})\n  - {reason}")
        elif actual == 404:
            health_score -= 0
            false_positives.append(f"- ❓ **FALSE POSITIVE** | {name} ({route})\n  - {reason} (Likely resource missing)")
        elif actual >= 400:
            health_score -= 3
            validation_failures.append(f"- ❌ **FAIL** | {name} ({route})\n  - {reason}")
        elif str(actual).startswith("2") and any(str(e).startswith("2") for e in expected):
            # Both are 2xx, but didn't match exactly
            health_score -= 1
            doc_mismatches.append(f"- 📝 **DOC MISMATCH** | {name} ({route})\n  - {reason}")
        else:
            health_score -= 3
            validation_failures.append(f"- ❌ **FAIL** | {name} ({route})\n  - {reason}")

    # Prevent score from going below 0
    health_score = max(0, health_score)

    # Build the Markdown Report
    report = [
        "# 🚀 API Test Agent Report\n",
        "## Executive Summary",
        f"**Total Tests:** {total} | **Passed:** {passed} ✅ | **Failed:** {total - passed} ❌",
        f"\n### 🏥 API Health Score: {health_score}/100\n",
        "---\n"
    ]
    
    if critical_failures:
        report.append("## 🚨 Critical Failures (Backend Bugs)")
        report.extend(critical_failures)
        report.append("")
        
    if doc_mismatches:
        report.append("## 📝 Documentation Mismatches")
        report.extend(doc_mismatches)
        report.append("")
        
    if validation_failures:
        report.append("## ❌ Validation Failures")
        report.extend(validation_failures)
        report.append("")
        
    if false_positives:
        report.append("## ❓ Potential False Positives (Resource Missing)")
        report.extend(false_positives)
        report.append("")
        
    if performance_warnings:
        report.append("## ⚠️ Performance Warnings")
        report.extend(performance_warnings)
        report.append("")
        
    if passed_tests:
        report.append("## ✅ Passed Tests")
        report.extend(passed_tests)
        report.append("")
        
    report.append("## 💡 Recommendations")
    if critical_failures:
        report.append("- **Immediate Action:** Investigate 500-level errors; these are backend crashes.")
    if doc_mismatches:
        report.append("- **Documentation:** Update your OpenAPI schema to match the actual 2xx success codes returned by the API.")
    if validation_failures:
        report.append("- **Analysis:** Use the `/api/analyze-failure` AI endpoint on your Validation Failures to discover payload issues.")
        
    return "\n".join(report)

