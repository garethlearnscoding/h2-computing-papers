#!/usr/bin/env python3
"""
Docker test runner that executes user code and test suites in isolated environment.
"""

import sys
import os
import tempfile
import subprocess
import json
import shutil
import re
from pathlib import Path

from notebook_parser import proc_file, FullPaper

def test_paper(full_paper: FullPaper, paper_name: str, timeout=10):
    """
    Run test suite with injected user code in Docker container.
    
    Args:
        full_paper: List of the tasks which are list of user's code cells to execute
        paper_name: Name of the paper (e.g. "2CZ_NJC_24")
        timeout: Maximum execution time in seconds        
    Returns:
        dict: Test results in JSON format
    """
    # Create temporary directory for our work
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        for i, task in enumerate(full_paper):
            for j, cell in enumerate(task):
                ( temp_path / f"outfile_{i}.{j}.py" ).write_text(cell)
        
        # Copy testcases directory into temp directory
        testcases_src = Path(f"nj67-papers/testcases/{paper_name}")
        testcases_dest = temp_path / "testcases"
        if testcases_src.exists() and testcases_src.is_dir():
            shutil.copytree(testcases_src, testcases_dest)
        else:
            raise NotImplementedError(f"Unknown paper name '{paper_name}'")

        shutil.copytree(
            Path('nj67-papers/testcases/python_testcase_functions'),
            Path(temp_path / 'python_testcase_functions')
        )
        
        # Change to temp directory
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Build command to run tests with timeout
            # Mount user code and test cases as volumes
            cmd = [
                "docker", "run",
                "--cpus", "1", 
                "--memory", "256m", 
                "--pids-limit", "50",
                "--read-only",
                "--tmpfs",
                "/tmp:size=64m", 
                "--security-opt", "no-new-privileges", 
                "--cap-drop=ALL", 
                "--user", "appuser",
                "-v", f"{temp_path}:/testcases/usercode:ro",
                "-v", f"{testcases_dest}:/testcases/testcases:ro",
                "nj67-testcases:latest",
                "/testcases/testcases",
                "/testcases/testcases"
            ]
            print(' '.join(cmd))
            # Run with timeout using a wrapper
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Parse unittest output
            output = result.stdout + result.stderr
            print(output)
            
            # Parse test results from unittest output
            # Look for patterns like "Ran X tests" and "OK" or "FAILED"
            test_count_match = re.search(r'Ran (\d+) test', output)
            total = int(test_count_match.group(1)) if test_count_match else 0
            
            # Determine success based on exit code and output
            success = result.returncode == 0 and "OK" in output
            
            # Parse failures and errors
            failures = []
            errors = []
            
            # Look for failure patterns
            fail_match = re.search(r'failures=(\d+)', output)
            if fail_match:
                failures = [f"failures={fail_match.group(1)}"]
            
            # Look for error patterns
            error_match = re.search(r'errors=(\d+)', output)
            if error_match:
                errors = [f"errors={error_match.group(1)}"]
            
            return {
                "success": success,
                "total": total,
                "passed": total if success else 0,
                "failures": failures,
                "errors": errors
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Code timed out - possible infinite loop",
                "timeout": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            os.chdir(old_cwd)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Usage: docker_test_runner.py <paper_name> <user_code_directory>"
        }), file=sys.stderr)
        sys.exit(1)
    paper_name = sys.argv[1]
    user_dir = Path(sys.argv[2])
    result = test_paper(
        [proc_file(f) for f in sorted(list(user_dir.iterdir()), key=lambda f: f.name) if f.is_file()],
        paper_name,
    )
    print(json.dumps(result))