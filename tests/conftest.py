from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
GOLDEN_DIR = REPO_ROOT / "tests" / "golden"


@pytest.fixture
def golden():
    def read(name: str) -> str:
        return (GOLDEN_DIR / name).read_text()

    return read


@pytest.fixture
def test_csv() -> str:
    return str(REPO_ROOT / "test.csv")
