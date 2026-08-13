"""
Testing Agent Tools - QA, test execution, and quality assurance.
"""
import os
import re
import subprocess
import tempfile
from typing import Optional


def run_pytest(test_path: str = ".", args: str = "", timeout: int = 120) -> dict:
    """
    Run pytest tests.

    Args:
        test_path: Path to test file or directory
        args: Additional pytest arguments (e.g., "-v", "--cov")
        timeout: Maximum execution time in seconds

    Returns:
        dict: Test results including passed, failed, and output
    """
    try:
        cmd = f"pytest {test_path} {args} --tb=short"
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        output = result.stdout + result.stderr

        # Parse results
        passed = len(re.findall(r' PASSED', output))
        failed = len(re.findall(r' FAILED', output))
        errors = len(re.findall(r' ERROR', output))
        skipped = len(re.findall(r' SKIPPED', output))

        return {
            "success": result.returncode == 0,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "skipped": skipped,
            "total": passed + failed + errors + skipped,
            "output": output[:10000],  # Limit output size
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Tests timed out after {timeout} seconds"}
    except Exception as e:
        return {"error": str(e)}


def run_unittest(test_path: str, timeout: int = 120) -> dict:
    """
    Run unittest tests.

    Args:
        test_path: Path to test file or module
        timeout: Maximum execution time in seconds

    Returns:
        dict: Test results
    """
    try:
        cmd = f"python -m unittest {test_path} -v"
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        output = result.stdout + result.stderr

        # Parse results
        ok_match = re.search(r'OK \(tests?=(\d+)\)', output)
        fail_match = re.search(r'FAILED \(.*?failures?=(\d+)', output)
        error_match = re.search(r'FAILED \(.*?errors?=(\d+)', output)

        passed = int(ok_match.group(1)) if ok_match else 0
        failed = int(fail_match.group(1)) if fail_match else 0
        errors = int(error_match.group(1)) if error_match else 0

        return {
            "success": result.returncode == 0,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "output": output[:10000],
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Tests timed out after {timeout} seconds"}
    except Exception as e:
        return {"error": str(e)}


def run_jest(test_path: str = ".", args: str = "", timeout: int = 120) -> dict:
    """
    Run Jest tests for JavaScript/TypeScript.

    Args:
        test_path: Path to test file or directory
        args: Additional Jest arguments
        timeout: Maximum execution time in seconds

    Returns:
        dict: Test results
    """
    try:
        cmd = f"npx jest {test_path} {args} --no-coverage"
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        output = result.stdout + result.stderr

        # Parse Jest output
        tests_match = re.search(r'Tests:\s+(\d+) passed', output)
        failed_match = re.search(r'(\d+) failed', output)
        suites_match = re.search(r'Test Suites:\s+(\d+) passed', output)

        return {
            "success": result.returncode == 0,
            "passed": int(tests_match.group(1)) if tests_match else 0,
            "failed": int(failed_match.group(1)) if failed_match else 0,
            "suites": int(suites_match.group(1)) if suites_match else 0,
            "output": output[:10000],
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Tests timed out after {timeout} seconds"}
    except Exception as e:
        return {"error": str(e)}


def check_test_coverage(source_path: str = ".", timeout: int = 180) -> dict:
    """
    Run pytest with coverage analysis.

    Args:
        source_path: Path to source code to measure coverage
        timeout: Maximum execution time in seconds

    Returns:
        dict: Coverage report
    """
    try:
        cmd = f"pytest --cov={source_path} --cov-report=term-missing"
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        output = result.stdout + result.stderr

        # Parse coverage percentage
        coverage_match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', output)
        total_coverage = int(coverage_match.group(1)) if coverage_match else None

        # Parse file-level coverage
        file_coverages = []
        file_pattern = r'(\S+\.py)\s+(\d+)\s+(\d+)\s+(\d+)%'
        for match in re.finditer(file_pattern, output):
            file_coverages.append({
                "file": match.group(1),
                "statements": int(match.group(2)),
                "missing": int(match.group(3)),
                "coverage": int(match.group(4))
            })

        return {
            "success": result.returncode == 0,
            "total_coverage": total_coverage,
            "files": file_coverages,
            "output": output[:10000],
            "recommendation": "Aim for >80% coverage" if total_coverage and total_coverage < 80 else "Good coverage!"
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Coverage check timed out after {timeout} seconds"}
    except Exception as e:
        return {"error": str(e)}


def generate_test_template(
    function_name: str,
    function_code: str,
    framework: str = "pytest"
) -> dict:
    """
    Generate a test template for a given function.

    Args:
        function_name: Name of the function to test
        function_code: The function's source code
        framework: Test framework (pytest, unittest)

    Returns:
        dict: Generated test template
    """
    # Extract function signature
    sig_match = re.search(r'def\s+' + function_name + r'\s*\(([^)]*)\)', function_code)
    params = sig_match.group(1) if sig_match else ""

    # Parse parameters
    param_list = [p.strip().split(':')[0].split('=')[0].strip()
                  for p in params.split(',') if p.strip() and p.strip() != 'self']

    if framework == "pytest":
        template = f'''import pytest
from your_module import {function_name}


class Test{function_name.title().replace("_", "")}:
    """Tests for {function_name} function."""

    def test_{function_name}_basic(self):
        """Test basic functionality."""
        # Arrange
        {chr(10).join(f"        {p} = None  # TODO: Set test value" for p in param_list) if param_list else "        # No parameters"}

        # Act
        result = {function_name}({", ".join(param_list)})

        # Assert
        assert result is not None  # TODO: Add specific assertions

    def test_{function_name}_edge_case(self):
        """Test edge cases."""
        # TODO: Add edge case tests
        pass

    def test_{function_name}_invalid_input(self):
        """Test invalid input handling."""
        with pytest.raises(Exception):  # TODO: Specify exception type
            {function_name}(None)  # TODO: Add invalid input


# Parametrized tests
@pytest.mark.parametrize("input_val,expected", [
    # TODO: Add test cases
    # (input1, expected1),
    # (input2, expected2),
])
def test_{function_name}_parametrized(input_val, expected):
    """Parametrized tests for various inputs."""
    result = {function_name}(input_val)
    assert result == expected
'''
    else:  # unittest
        template = f'''import unittest
from your_module import {function_name}


class Test{function_name.title().replace("_", "")}(unittest.TestCase):
    """Tests for {function_name} function."""

    def setUp(self):
        """Set up test fixtures."""
        pass

    def tearDown(self):
        """Clean up after tests."""
        pass

    def test_{function_name}_basic(self):
        """Test basic functionality."""
        # Arrange
        {chr(10).join(f"        {p} = None  # TODO: Set test value" for p in param_list) if param_list else "        # No parameters"}

        # Act
        result = {function_name}({", ".join(param_list)})

        # Assert
        self.assertIsNotNone(result)  # TODO: Add specific assertions

    def test_{function_name}_edge_case(self):
        """Test edge cases."""
        # TODO: Add edge case tests
        pass

    def test_{function_name}_invalid_input(self):
        """Test invalid input handling."""
        with self.assertRaises(Exception):  # TODO: Specify exception type
            {function_name}(None)


if __name__ == "__main__":
    unittest.main()
'''

    return {
        "function_name": function_name,
        "framework": framework,
        "template": template,
        "parameters_detected": param_list,
        "tip": "Replace 'your_module' with actual module name and fill in TODO items"
    }


def analyze_test_quality(test_code: str) -> dict:
    """
    Analyze test code quality and provide recommendations.

    Args:
        test_code: The test code to analyze

    Returns:
        dict: Analysis results and recommendations
    """
    issues = []
    good_practices = []
    score = 100

    lines = test_code.split('\n')

    # Check for test count
    test_count = len(re.findall(r'def test_', test_code))
    if test_count == 0:
        issues.append("No test functions found (should start with 'test_')")
        score -= 30

    # Check for assertions
    assert_count = len(re.findall(r'assert\s|self\.assert|pytest\.raises|self\.assertRaises', test_code))
    if assert_count == 0:
        issues.append("No assertions found - tests need assertions to be meaningful")
        score -= 25
    elif assert_count < test_count:
        issues.append(f"Low assertion density: {assert_count} assertions for {test_count} tests")
        score -= 10
    else:
        good_practices.append(f"Good assertion coverage: {assert_count} assertions")

    # Check for docstrings
    docstring_count = len(re.findall(r'"""[^"]+"""', test_code))
    if docstring_count >= test_count:
        good_practices.append("Tests are well documented with docstrings")
    else:
        issues.append("Some tests lack docstrings - add descriptions for clarity")
        score -= 5

    # Check for setup/teardown
    has_setup = 'setUp' in test_code or 'setup' in test_code or '@pytest.fixture' in test_code
    if has_setup:
        good_practices.append("Uses setup/fixtures for test preparation")

    # Check for parametrized tests
    if '@pytest.mark.parametrize' in test_code or 'subTest' in test_code:
        good_practices.append("Uses parametrized tests for thorough coverage")

    # Check for edge case tests
    edge_case_patterns = ['edge', 'boundary', 'empty', 'null', 'none', 'invalid', 'error', 'exception']
    has_edge_cases = any(p in test_code.lower() for p in edge_case_patterns)
    if has_edge_cases:
        good_practices.append("Includes edge case/error testing")
    else:
        issues.append("Consider adding edge case and error handling tests")
        score -= 10

    # Check for magic numbers
    magic_numbers = re.findall(r'assert.*==\s*\d{2,}', test_code)
    if magic_numbers:
        issues.append("Consider using named constants instead of magic numbers in assertions")
        score -= 5

    # Determine rating
    if score >= 90:
        rating = "Excellent"
    elif score >= 75:
        rating = "Good"
    elif score >= 60:
        rating = "Acceptable"
    else:
        rating = "Needs Improvement"

    return {
        "score": max(0, score),
        "rating": rating,
        "test_count": test_count,
        "assertion_count": assert_count,
        "good_practices": good_practices,
        "issues": issues,
        "recommendations": [
            "Add more edge case tests" if not has_edge_cases else None,
            "Add docstrings to all tests" if docstring_count < test_count else None,
            "Use fixtures for shared setup" if not has_setup else None,
            "Consider parametrized tests for multiple inputs" if '@pytest.mark.parametrize' not in test_code else None
        ]
    }


def create_mock_template(class_name: str, methods: list) -> dict:
    """
    Generate mock/stub templates for testing.

    Args:
        class_name: Name of the class to mock
        methods: List of method names to mock

    Returns:
        dict: Mock template code
    """
    method_mocks = []
    for method in methods:
        method_mocks.append(f'''    @patch.object({class_name}, '{method}')
    def test_with_mocked_{method}(self, mock_{method}):
        """Test with mocked {method}."""
        mock_{method}.return_value = None  # TODO: Set return value

        # Act
        instance = {class_name}()
        result = instance.{method}()

        # Assert
        mock_{method}.assert_called_once()
        # TODO: Add more assertions
''')

    template = f'''from unittest.mock import Mock, patch, MagicMock
import pytest


# Pytest style mocking
@pytest.fixture
def mock_{class_name.lower()}():
    """Fixture providing a mocked {class_name}."""
    with patch('{class_name}') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance


def test_with_mock_{class_name.lower()}(mock_{class_name.lower()}):
    """Test using mocked {class_name}."""
    # Configure mock
    {chr(10).join(f"    mock_{class_name.lower()}.{m}.return_value = None  # TODO" for m in methods)}

    # Act & Assert
    # TODO: Add test logic


# Unittest style mocking
class Test{class_name}Mocked:
    """Tests using mocked {class_name}."""

{chr(10).join(method_mocks)}

# Context manager style
def test_with_context_mock():
    """Test using context manager mock."""
    with patch('{class_name}') as mock_{class_name.lower()}:
        mock_{class_name.lower()}.return_value.some_method.return_value = "value"
        # TODO: Add test logic
'''

    return {
        "class_name": class_name,
        "methods": methods,
        "template": template,
        "tip": "Replace TODO items and adjust return values for your use case"
    }


def lint_code(code: str, language: str = "python") -> dict:
    """
    Run linting on code and return issues.

    Args:
        code: Source code to lint
        language: Programming language

    Returns:
        dict: Linting results
    """
    issues = []

    if language == "python":
        # Basic Python linting rules
        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            # Line length
            if len(line) > 100:
                issues.append({
                    "line": i,
                    "type": "warning",
                    "message": f"Line too long ({len(line)} > 100 characters)"
                })

            # Trailing whitespace
            if line.rstrip() != line and line.strip():
                issues.append({
                    "line": i,
                    "type": "warning",
                    "message": "Trailing whitespace"
                })

            # Multiple imports on one line
            if re.match(r'^import\s+\w+,', line):
                issues.append({
                    "line": i,
                    "type": "warning",
                    "message": "Multiple imports on one line"
                })

        # Global issues
        if re.search(r'except\s*:', code):
            issues.append({
                "line": None,
                "type": "error",
                "message": "Bare 'except:' clause - specify exception type"
            })

        if re.search(r'\beval\s*\(', code):
            issues.append({
                "line": None,
                "type": "error",
                "message": "Use of eval() - security risk"
            })

        if re.search(r'\bexec\s*\(', code):
            issues.append({
                "line": None,
                "type": "error",
                "message": "Use of exec() - security risk"
            })

        # Missing docstrings
        functions_without_docs = re.findall(
            r'def\s+(\w+)\s*\([^)]*\)\s*:\s*\n\s*[^"\']',
            code
        )
        for func in functions_without_docs:
            if not func.startswith('_'):
                issues.append({
                    "line": None,
                    "type": "warning",
                    "message": f"Function '{func}' missing docstring"
                })

    error_count = len([i for i in issues if i["type"] == "error"])
    warning_count = len([i for i in issues if i["type"] == "warning"])

    return {
        "language": language,
        "issues": issues,
        "error_count": error_count,
        "warning_count": warning_count,
        "clean": len(issues) == 0,
        "summary": f"{error_count} errors, {warning_count} warnings"
    }


def generate_test_report(test_results: dict, project_name: str = "Project") -> dict:
    """
    Generate a formatted test report.

    Args:
        test_results: Results from running tests
        project_name: Name of the project

    Returns:
        dict: Formatted test report
    """
    from datetime import datetime

    passed = test_results.get("passed", 0)
    failed = test_results.get("failed", 0)
    errors = test_results.get("errors", 0)
    total = passed + failed + errors
    pass_rate = (passed / total * 100) if total > 0 else 0

    status = "✅ PASSED" if failed == 0 and errors == 0 else "❌ FAILED"

    report = f"""# Test Report: {project_name}

**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Status:** {status}

## Summary

| Metric | Count |
|--------|-------|
| Total Tests | {total} |
| Passed | {passed} |
| Failed | {failed} |
| Errors | {errors} |
| Pass Rate | {pass_rate:.1f}% |

## Details

```
{test_results.get("output", "No output available")[:5000]}
```

## Recommendations

"""
    recommendations = []
    if failed > 0:
        recommendations.append(f"- Fix {failed} failing test(s)")
    if errors > 0:
        recommendations.append(f"- Investigate {errors} error(s)")
    if pass_rate < 80:
        recommendations.append("- Improve test coverage (aim for >80%)")
    if pass_rate == 100:
        recommendations.append("- All tests passing! Consider adding more edge cases.")

    report += "\n".join(recommendations) if recommendations else "- All good! Keep up the quality."

    return {
        "report": report,
        "status": "passed" if failed == 0 and errors == 0 else "failed",
        "pass_rate": pass_rate,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": errors
        }
    }
