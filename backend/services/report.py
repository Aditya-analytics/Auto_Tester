from typing import List
from core.models import TestResult, ReportMetrics

def generate_report(results: List[TestResult]) -> ReportMetrics:
    """
    Module 11: Generates HTML and Markdown reports from execution results.
    """
    total_tests = len(results)
    
    if total_tests == 0:
        return ReportMetrics(
            total_tests=0, passed_tests=0, failed_tests=0, slow_tests=0,
            health_score=0.0, pass_rate=0.0, html_content="<h1>No tests executed.</h1>"
        )
        
    passed_tests = sum(1 for r in results if r.success)
    failed_tests = total_tests - passed_tests
    slow_tests = sum(1 for r in results if r.is_slow)
    
    pass_rate = round((passed_tests / total_tests) * 100, 2)
    
    # Calculate an arbitrary health score out of 100
    # Every failure deducts heavily, every slow test deducts slightly
    health_score = 100.0 - (failed_tests * (100 / max(1, total_tests))) - (slow_tests * 5)
    health_score = max(0.0, round(health_score, 2))
    
    # Generate HTML Table Rows
    table_rows = ""
    for r in results:
        status_color = "green" if r.success else "red"
        speed_color = "orange" if r.is_slow else "green"
        # Truncate request body if it exists
        body_snippet = "None"
        if r.test_case.request_body_json and r.test_case.request_body_json != "null":
            body_snippet = str(r.test_case.request_body_json)
            if len(body_snippet) > 100:
                body_snippet = body_snippet[:100] + "..."
                
        table_rows += f"""
        <tr>
            <td style="padding:8px; border:1px solid #ddd; font-weight:bold;">{r.test_case.name}</td>
            <td style="padding:8px; border:1px solid #ddd;">{r.test_case.method} <br/> <small>{r.test_case.url}</small></td>
            <td style="padding:8px; border:1px solid #ddd;"><code>{body_snippet}</code></td>
            <td style="padding:8px; border:1px solid #ddd;">{r.test_case.expected_status}</td>
            <td style="padding:8px; border:1px solid #ddd; color:{status_color}; font-weight:bold;">{r.status_code} ({"Pass" if r.success else "Fail"})</td>
            <td style="padding:8px; border:1px solid #ddd; color:{speed_color};">{r.response_time_ms} ms</td>
        </tr>
        """
        
    # Generate simple HTML layout
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Test Execution Report</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; padding: 2rem; color: #333; }}
            .card {{ background: #f9f9f9; border-radius: 8px; padding: 20px; margin-bottom: 20px; border: 1px solid #ddd; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th {{ background: #eee; padding: 10px; text-align: left; border: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <h1>API Health Report</h1>
        <div class="card" style="display:flex; gap: 40px;">
            <div>
                <p><strong>Health Score</strong></p>
                <h2 style="color: {'green' if health_score > 80 else 'red'}; margin:0;">{health_score}/100</h2>
            </div>
            <div>
                <p><strong>Pass Rate</strong></p>
                <h2 style="margin:0;">{pass_rate}%</h2>
            </div>
            <div>
                <p><strong>Failed Tests</strong></p>
                <h2 style="color:red; margin:0;">{failed_tests}</h2>
            </div>
            <div>
                <p><strong>Slow APIs</strong></p>
                <h2 style="color:orange; margin:0;">{slow_tests}</h2>
            </div>
        </div>
        
        <h2>Endpoint Summary</h2>
        <table>
            <tr>
                <th>Test Case Name</th>
                <th>Endpoint</th>
                <th>Request Body</th>
                <th>Expected Status</th>
                <th>Actual Status</th>
                <th>Response Time</th>
            </tr>
            {table_rows}
        </table>
    </body>
    </html>
    """
    
    return ReportMetrics(
        total_tests=total_tests,
        passed_tests=passed_tests,
        failed_tests=failed_tests,
        slow_tests=slow_tests,
        health_score=health_score,
        pass_rate=pass_rate,
        html_content=html
    )
