import subprocess

def run_lint_strict():
    subprocess.run(["ruff", "check", ".", "--select", "ALL"])

def run_lint_fix():
    subprocess.run(["ruff", "check", ".", "--fix"])

def run_format_check():
    subprocess.run(["ruff", "format", ".", "--check"])

def run_format_fix():
    subprocess.run(["ruff", "format", "."]) 