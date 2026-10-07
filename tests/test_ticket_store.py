from mcp_server.store import create_ticket, get_ticket, list_tickets


def test_create_returns_ticket_with_fields(tmp_path):
    path = tmp_path / "tickets.json"
    ticket = create_ticket(path, "Laptop will not boot", "hardware", "employee")
    assert ticket["id"] == "T-0001"
    assert ticket["title"] == "Laptop will not boot"
    assert ticket["category"] == "hardware"
    assert ticket["status"] == "open"
    assert ticket["requester"] == "employee"
    assert ticket["created"]


def test_ids_are_sequential_and_persisted(tmp_path):
    path = tmp_path / "tickets.json"
    create_ticket(path, "First", "software", "employee")
    second = create_ticket(path, "Second", "access", "employee")
    assert second["id"] == "T-0002"
    assert path.exists()


def test_get_returns_ticket_or_none(tmp_path):
    path = tmp_path / "tickets.json"
    created = create_ticket(path, "VPN broken", "access", "alice")
    assert get_ticket(path, created["id"]) == created
    assert get_ticket(path, "T-9999") is None


def test_get_on_missing_file_returns_none(tmp_path):
    assert get_ticket(tmp_path / "nope.json", "T-0001") is None


def test_list_all_and_filtered_by_requester(tmp_path):
    path = tmp_path / "tickets.json"
    assert list_tickets(path) == []
    create_ticket(path, "A", "hardware", "alice")
    create_ticket(path, "B", "software", "bob")
    create_ticket(path, "C", "other", "alice")
    assert [t["id"] for t in list_tickets(path)] == ["T-0001", "T-0002", "T-0003"]
    assert [t["title"] for t in list_tickets(path, requester="alice")] == ["A", "C"]
