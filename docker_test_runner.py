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
        
        # uhh i have no idea what AI is doing here

        # # Write code to a file that can be imported/tested
        # main_test_file = temp_path / "main_test.py"
        # main_test_file.write_text(code_string)
        
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
                    "nj67-testcases",
                # "python -c print('hello')"
                # "python", "-m", "unittest",
                # "discover",
                "-s", str(testcases_dest),
                # "-v"
            ]
            print(' '.join(cmd))
            # Run with timeout using a wrapper
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Parse unittest output (this is simplified)
            # In reality, we'd want to capture the actual test results
            output = result.stdout + result.stderr
            print(output)
            # Determine success based on exit code
            success = result.returncode == 0
            
            return {
                "success": success,
                "total": 0,  # Would need to count tests
                "passed": 0 if not success else 0,  # Simplified
                "failures": [],
                "errors": []
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

# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print(json.dumps({
#             "error": "Usage: docker_test_runner.py <code_string> <test_pattern>"
#         }), file=sys.stderr)
#         sys.exit(1)
#     code_string = sys.argv[1]
#     test_pattern = sys.argv[2]
#     result = run_tests_in_docker(code_string, test_pattern)
#     print(json.dumps(result))

# Add the following lines to the end of the file
# This will run the test_paper function in a Docker environment
# with the test cases from the nj67-papers/testcases directory
# and the paper name as the first argument
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