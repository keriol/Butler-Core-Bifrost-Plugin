from pathlib import Path


def test_package_contains_no_alfred_specific_imports():
    root = Path(__file__).resolve().parents[1] / "src"
    sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in root.rglob("*.py")
    ).casefold()
    assert "from alfred" not in sources
    assert "import alfred" not in sources


def test_midgard_ingress_contains_no_asgard_dependency():
    path = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "butler_bifrost"
        / "ingress.py"
    )
    assert "asgard" not in path.read_text(encoding="utf-8").casefold()


def test_public_sources_contain_no_household_specific_entity_ids():
    root = Path(__file__).resolve().parents[1]
    sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in list((root / "src").rglob("*.py"))
        + list((root / "docs").rglob("*.md"))
    ).casefold()
    assert "entity_id" not in sources
    assert "homeassistant.local" not in sources
