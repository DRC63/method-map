from tests.conftest import ADMIN


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_list_frameworks(client):
    data = client.get("/api/frameworks").json()
    assert len(data) == 1
    fw = data[0]
    assert fw["key"] == "prince2-7"
    assert fw["entity_counts"]["activity"] == 41
    assert fw["entity_counts"]["role"] == 7


def test_full_graph_has_all_link_kinds(client):
    g = client.get("/api/frameworks/prince2-7/graph").json()
    assert len(g["nodes"]) == 91
    kinds = {l["kind"] for l in g["links"]}
    assert kinds == {"contains", "direct", "derived"}
    # every direct link carries a code + label
    direct = [l for l in g["links"] if l["kind"] == "direct"]
    assert all(l.get("code") and l.get("code_label") for l in direct)


def test_layer_filter_roles_and_practices(client):
    g = client.get(
        "/api/frameworks/prince2-7/graph?types=role,practice&derived=true"
    ).json()
    node_types = {n["type"] for n in g["nodes"]}
    assert node_types == {"role", "practice"}
    # with activities hidden, only derived (co-occurrence) links remain
    assert {l["kind"] for l in g["links"]} == {"derived"}


def test_layer_filter_no_derived(client):
    g = client.get(
        "/api/frameworks/prince2-7/graph?types=role,practice&derived=false"
    ).json()
    # no activities, no derived -> isolated nodes, zero links
    assert g["links"] == []
    assert {n["type"] for n in g["nodes"]} == {"role", "practice"}


def test_entity_detail_incoming(client):
    roles = client.get("/api/frameworks/prince2-7/entities?type=role").json()
    pm = next(r for r in roles if r["name"] == "Project Manager")
    detail = client.get(f"/api/entities/{pm['id']}").json()
    incoming = [r for r in detail["related"] if r["direction"] == "in"]
    assert len(incoming) > 10
    sample = incoming[0]
    assert sample["type"] == "activity"
    assert sample["code"] in {"C", "P", "N"}
    assert sample["via_process"]  # activity's owning process surfaced


def test_lifecycle(client):
    lc = client.get("/api/frameworks/prince2-7/lifecycle").json()
    assert lc["level_order"] == ["directing", "managing", "delivering"]
    procs = lc["processes"]
    assert [p["code"] for p in procs] == ["SU", "DP", "IP", "CS", "MP", "SB", "CP"]
    dp = next(p for p in procs if p["code"] == "DP")
    assert dp["lifecycle_level"] == "directing"
    assert dp["lifecycle_phase"] == "throughout"
    cs = next(p for p in procs if p["code"] == "CS")
    assert cs["repeats"] is True
    # activities are sequenced 1..n in process order
    su = next(p for p in procs if p["code"] == "SU")
    assert [a["sequence"] for a in su["activities"]] == list(
        range(1, len(su["activities"]) + 1)
    )
    assert su["activities"][0]["name"] == "Appoint the Executive and the Project Manager"


def test_process_detail_lists_activities_in_sequence(client):
    procs = client.get("/api/frameworks/prince2-7/entities?type=process").json()
    su = next(p for p in procs if p["code"] == "SU")
    detail = client.get(f"/api/entities/{su['id']}").json()
    steps = [r for r in detail["related"] if r["direction"] == "out"]
    assert len(steps) == 6
    assert all(r["type"] == "activity" for r in steps)
    assert [r["code"] for r in steps] == ["1", "2", "3", "4", "5", "6"]
    assert steps[0]["name"] == "Appoint the Executive and the Project Manager"


def test_write_requires_admin_password(client):
    payload = {"framework_id": 1, "type": "role", "name": "QA Lead"}
    assert client.post("/api/entities", json=payload).status_code == 401
    ok = client.post("/api/entities", json=payload, headers=ADMIN)
    assert ok.status_code == 201
    assert ok.json()["name"] == "QA Lead"


def test_authoring_fails_closed_without_password(client, monkeypatch):
    """With ADMIN_PASSWORD unset, writes are rejected even with the old default
    'change-me' - an unconfigured deployment is read-only, not wide open. This
    guards the fix for the live services that accepted 'change-me' (SEC-05)."""
    monkeypatch.setenv("ADMIN_PASSWORD", "")
    payload = {"framework_id": 1, "type": "role", "name": "Should Not Persist"}
    assert client.post("/api/entities", json=payload, headers=ADMIN).status_code == 401
    assert client.post("/api/entities", json=payload).status_code == 401
    # And with the env var absent entirely (not just blank).
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    assert client.post("/api/entities", json=payload, headers=ADMIN).status_code == 401


def test_create_relationship_and_appears_in_detail(client):
    ents = client.get("/api/frameworks/prince2-7/entities").json()
    activity = next(e for e in ents if e["type"] == "activity")
    role = next(e for e in ents if e["type"] == "role")
    rel = client.post(
        "/api/relationships",
        json={
            "framework_id": 1,
            "from_entity_id": activity["id"],
            "to_entity_id": role["id"],
            "code": "P",
        },
        headers=ADMIN,
    )
    assert rel.status_code == 201
    detail = client.get(f"/api/entities/{activity['id']}").json()
    assert any(r["entity_id"] == role["id"] for r in detail["related"])


def test_exports(client):
    csv = client.get("/api/frameworks/prince2-7/export.csv")
    assert csv.status_code == 200
    assert "text/csv" in csv.headers["content-type"]
    assert b"Process" in csv.content

    xlsx = client.get("/api/frameworks/prince2-7/export.xlsx")
    assert xlsx.status_code == 200
    assert "spreadsheet" in xlsx.headers["content-type"]

    ents = client.get("/api/frameworks/prince2-7/entities?type=role").json()
    pdf = client.get(
        f"/api/frameworks/prince2-7/entities/{ents[0]['id']}/report.pdf"
    )
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content[:4] == b"%PDF"
