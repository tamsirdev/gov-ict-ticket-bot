def test_homepage(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"ICT Support Ticket" in r.data


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.is_json
    assert r.json["status"] == "ok"


def test_submit_ticket(client):
    r = client.post(
        "/submit",
        data={
            "name": "Fatou",
            "phone": "+2205551234",
            "description": "WiFi keeps dropping",
        },
        follow_redirects=True,
    )
    assert r.status_code == 200
    assert b"Ticket Created" in r.data or b"#1" in r.data


def test_submit_empty_description(client):
    r = client.post(
        "/submit",
        data={
            "name": "Fatou",
            "phone": "+2205551234",
            "description": "",
        },
        follow_redirects=True,
    )
    assert r.status_code == 200
    assert b"describe" in r.data.lower()


def test_status_form(client):
    r = client.get("/status")
    assert r.status_code == 200
    assert b"Check Ticket Status" in r.data


def test_user_tickets(client, sample_tickets):
    r = client.get("/status/+220Fatou")
    assert r.status_code == 200
    assert b"#1" in r.data or b"#Fatou" in r.data or b"WiFi" in r.data


def test_admin_login_page(client):
    r = client.get("/admin/login")
    assert r.status_code == 200
    assert b"Admin Login" in r.data


def test_admin_login_success(client):
    r = client.post("/admin/login", data={"password": "admin"}, follow_redirects=True)
    assert r.status_code == 200
    assert b"Ticket Dashboard" in r.data


def test_admin_login_failure(client):
    r = client.post("/admin/login", data={"password": "wrong"}, follow_redirects=True)
    assert r.status_code == 200
    assert b"Wrong password" in r.data


def test_admin_dashboard_requires_login(client):
    r = client.get("/admin", follow_redirects=True)
    assert b"Admin Login" in r.data


def test_admin_dashboard_shows_tickets(client, sample_tickets):
    client.post("/admin/login", data={"password": "admin"})
    r = client.get("/admin")
    assert b"WiFi" in r.data
    assert b"Monitor" in r.data
    assert b"email" in r.data


def test_admin_update_status(client, sample_tickets):
    client.post("/admin/login", data={"password": "admin"})
    r = client.post(
        "/admin/update/1", data={"status": "In Progress"}, follow_redirects=True
    )
    assert r.status_code == 200
    assert b"In Progress" in r.data
