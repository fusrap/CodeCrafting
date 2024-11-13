import os
import subprocess
import webbrowser
import sys

def run_tests():
    os.environ['PYTHONPATH'] = os.getcwd()

    # Tving pytest til at bruge .coveragerc ved at specificere --cov-config
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest", "test"
        ],
        capture_output=True, text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print("Error running tests:")
        print(result.stderr)
        raise subprocess.CalledProcessError(result.returncode, result.args)

def open_html_report():
    report_path = os.path.join(os.getcwd(), "htmlcov", "index.html")
    
    if os.path.exists(report_path):
        print(f"Opening HTML report: {report_path}")
        webbrowser.open(report_path)
    else:
        print("HTML coverage report not found!")

if __name__ == "__main__":
    try:
        run_tests()
        open_html_report()
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with return code: {e.returncode}")
