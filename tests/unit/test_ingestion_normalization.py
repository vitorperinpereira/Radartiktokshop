from services.ingestion.normalization import build_canonical_key, build_title_alias, normalize_text


def test_normalize_text_collapses_spacing_and_symbols() -> None:
    assert normalize_text("  Viral   Lamp !!! ") == "viral-lamp"


def test_build_canonical_key_joins_normalized_segments() -> None:
    assert build_canonical_key("Magic Brush", "Acme", "Beauty") == "magic-brush::acme::beauty"


def test_build_title_alias_reuses_normalized_title() -> None:
    assert build_title_alias("  Portable   Blender Cup!!! ") == "portable-blender-cup"
