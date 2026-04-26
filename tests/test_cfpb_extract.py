from unittest.mock import MagicMock, patch


def test_parse_complaint_maps_all_fields():
    from extract.cfpb_extract import parse_complaint
    raw = {
        "complaint_id": "12345",
        "date_received": "2024-01-15",
        "product": "Checking or savings account",
        "sub_product": "Checking account",
        "issue": "Managing an account",
        "sub_issue": "Deposits and withdrawals",
        "company": "BANK OF AMERICA",
        "state": "CA",
        "zip_code": "90210",
        "submitted_via": "Web",
        "date_sent_to_company": "2024-01-16",
        "company_response_to_consumer": "Closed with explanation",
        "timely": "Yes",
        "consumer_disputed": "No",
        "consumer_consent_provided": "Consent provided",
    }
    result = parse_complaint(raw)
    assert result[0] == "12345"
    assert result[2] == "Checking or savings account"
    assert result[12] == "Yes"
    assert len(result) == 16


def test_parse_complaint_handles_missing_fields():
    from extract.cfpb_extract import parse_complaint
    raw = {"complaint_id": "99999"}
    result = parse_complaint(raw)
    assert result[0] == "99999"
    assert result[1] is None
    assert result[12] is None
    assert len(result) == 16


def test_dedup_filters_existing_ids():
    existing_ids = {"AAA", "BBB", "CCC"}
    raw_complaints = [
        {"complaint_id": "AAA"},
        {"complaint_id": "DDD"},
        {"complaint_id": "BBB"},
        {"complaint_id": "EEE"},
    ]
    new = [c for c in raw_complaints if c.get("complaint_id") not in existing_ids]
    assert len(new) == 2
    assert new[0]["complaint_id"] == "DDD"
    assert new[1]["complaint_id"] == "EEE"


@patch("extract.cfpb_extract.requests.get")
def test_fetch_stops_when_no_hits(mock_get):
    from extract.cfpb_extract import fetch_complaints
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_get.return_value = mock_response
    result = fetch_complaints("2024-01-01", "2024-01-31")
    assert result == []
