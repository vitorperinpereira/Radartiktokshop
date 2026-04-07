from services.ingestion.adapters.mock_adapter import load_mock_records


def test_mock_profiles_return_expected_seed_sets() -> None:
    smoke_records = load_mock_records(profile="smoke")
    weekly_records = load_mock_records(profile="demo_weekly")
    edge_records = load_mock_records(profile="edge_cases")

    assert len(smoke_records) == 3
    assert len(weekly_records) == 5
    assert len(edge_records) == 4
    assert all(record.raw_payload["profile"] == "demo_weekly" for record in weekly_records)
    assert any(record.brand is None for record in edge_records)
    assert any(record.category is None for record in edge_records)


def test_mock_profile_count_override_cycles_records() -> None:
    records = load_mock_records(profile="smoke", count=4)

    assert len(records) == 4
    assert records[0].source_record_id == "smoke-1"
    assert records[3].source_record_id == "smoke-4"
