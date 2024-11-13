import os
import subprocess
import webbrowser
import sys

def run_tests():
    os.environ['PYTHONPATH'] = os.getcwd()

    # Kør pytest med alle dækningsindstillinger direkte i kommandoen
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest", "test",
            "--cov=routes",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"  # Genererer HTML-rapport i htmlcov-mappen
        ],
        capture_output=True, text=True
    )

    # Udskriv resultatet fra pytest
    print(result.stdout)

    # Udskriv fejloutput, hvis der var fejl
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
