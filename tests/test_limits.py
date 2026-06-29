from pathlib import Path


def test_python_files_stay_under_100_lines():
    root = Path(__file__).parents[1]
    files = [*root.glob("src/**/*.py"), *root.glob("examples/**/*.py")]
    too_long = {str(path): len(path.read_text().splitlines()) for path in files
                if len(path.read_text().splitlines()) >= 100}

    assert not too_long, f"Python files must be under 100 lines: {too_long}"

