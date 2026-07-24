from core.models import TestResult, ValidationResult

def validate_results(results: list[TestResult]) -> list[ValidationResult]:
    """
    Acts as the Referee. Analyzes raw test results and determines Pass/Fail.
    """
    validations = []
    
    for res in results:
        passed = True
        failure_reason = None
        
        # Rule 1: Status Code Check (Functional correctness)
        if res.actual_status not in res.test_case.expected_status:
            passed = False
            failure_reason = f"Status Mismatch: Expected one of {res.test_case.expected_status}, got {res.actual_status}."
            
        # Rule 2: Performance SLA Check (Speed)
        # Even if the status was correct, if it took more than 2 seconds, we flag it.
        elif res.response_time_ms > 2000:
            passed = False
            failure_reason = f"Performance SLA Breached: Took {res.response_time_ms} ms (Limit: 2000 ms)."
            
        validations.append(
            ValidationResult(
                test_result=res,
                passed=passed,
                failure_reason=failure_reason
            )
        )
        
    return validations

# ==========================================
# MANUAL TESTING (Integration with Executor)
# ==========================================
