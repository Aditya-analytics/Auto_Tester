from models import ValidationResult

def generate_markdown_report(validations: list[ValidationResult]) -> str:
    """
    Takes a list of ValidationResults and formats them into a beautiful,
    human-readable Markdown report.
    """
    # 1. Calculate totals
    total = len(validations)
    passed = sum(1 for v in validations if v.passed)
    failed = total - passed
    
    # 2. Build the Header
    report = [
        "# 🚀 API Test Agent Report\n",
        f"**Total Tests:** {total} | **Passed:** {passed} ✅ | **Failed:** {failed} ❌",
        "\n---\n",
        "## 📝 Detailed Results\n"
    ]
    
    # 3. Loop through every test and build the body
    for val in validations:
        endpoint_name = val.test_result.test_case.name
        method = val.test_result.test_case.endpoint.method
        path = val.test_result.test_case.endpoint.path
        
        if val.passed:
            report.append(f"- ✅ **PASS** | {endpoint_name} (`{method} {path}`)")
        else:
            report.append(f"- ❌ **FAIL** | {endpoint_name} (`{method} {path}`)")
            report.append(f"  - **Reason:** {val.failure_reason}")
            
            # If the AI provided advice, format it beautifully as a blockquote
            if val.ai_explanation:
                report.append(f"  > 💡 **AI Insight:** {val.ai_explanation}")
        
        # Add a little spacing between tests
        report.append("")
        
    # 4. Join the list of strings into one giant string separated by newlines
    return "\n".join(report)

# ==========================================
# MANUAL TESTING
# ==========================================
