import re
from decimal import Decimal


def post(client, path, body, headers, expect=(200, 201)):
    r = client.post(path, json=body, headers=headers)
    assert r.status_code in expect, r.text
    return r.json()


def test_peehu_journey(client, login):
    admin = login(client, "admin", "admin123")

    # ---- Setup (admin) -------------------------------------------------
    dept_ids = {}
    for name in ["Cardiology", "Front Desk", "Laboratory", "Inpatient Care"]:
        dept_ids[name] = post(client, "/departments", {"name": name}, admin)["id"]
    cardiology = dept_ids["Cardiology"]
    front_desk = dept_ids["Front Desk"]
    laboratory = dept_ids["Laboratory"]
    inpatient = dept_ids["Inpatient Care"]

    def add_staff(department_id, first, last, role, username, password):
        r = post(
            client,
            "/staff",
            {
                "department_id": department_id,
                "first_name": first,
                "last_name": last,
                "role": role,
                "hire_date": "2026-01-01",
                "username": username,
                "password": password,
                "login_enabled": True,
            },
            admin,
        )
        assert "password_hash" not in r
        return r["id"]

    rao_staff = add_staff(cardiology, "Dr.", "Rao", "doctor", "rao", "rao-pass")
    add_staff(cardiology, "Anita", "Nair", "nurse", "anita", "anita-pass")
    add_staff(front_desk, "Meera", "Iyer", "receptionist", "meera", "meera-pass")
    add_staff(laboratory, "Ravi", "Kumar", "lab", "ravi", "ravi-pass")

    doctor_id = post(
        client,
        "/doctors",
        {
            "staff_id": rao_staff,
            "license_number": "LIC-1001",
            "specialty": "Cardiology",
            "consultation_fee": "800.00",
        },
        admin,
    )["id"]

    icu_ward = post(client, "/wards", {"department_id": inpatient, "name": "ICU"}, admin)["id"]
    ward_a = post(
        client, "/wards", {"department_id": inpatient, "name": "General Ward A"}, admin
    )["id"]
    icu_room = post(
        client,
        "/rooms",
        {"ward_id": icu_ward, "room_number": "1", "room_type": "shared", "daily_rate": "5000.00"},
        admin,
    )["id"]
    ward_room = post(
        client,
        "/rooms",
        {"ward_id": ward_a, "room_number": "3", "room_type": "shared", "daily_rate": "1500.00"},
        admin,
    )["id"]
    icu_bed = post(client, "/beds", {"room_id": icu_room, "bed_number": "1"}, admin)["id"]
    ward_bed = post(client, "/beds", {"room_id": ward_room, "bed_number": "3"}, admin)["id"]

    ecg_id = post(client, "/procedures", {"name": "ECG", "price": "500.00"}, admin)["id"]
    troponin_id = post(client, "/lab-tests", {"name": "Troponin", "price": "1200.00"}, admin)["id"]
    aspirin_id = post(
        client,
        "/medications",
        {"name": "Aspirin", "form": "tablet", "strength": "75 mg", "price": "2.00"},
        admin,
    )["id"]
    atorvastatin_id = post(
        client,
        "/medications",
        {"name": "Atorvastatin", "form": "tablet", "strength": "40 mg", "price": "10.00"},
        admin,
    )["id"]
    electrodes_id = post(
        client,
        "/consumables",
        {"name": "ECG electrode pack", "unit": "pack", "price": "150.00"},
        admin,
    )["id"]
    iv_set_id = post(
        client, "/consumables", {"name": "IV set", "unit": "piece", "price": "250.00"}, admin
    )["id"]
    provider_id = post(client, "/insurance-providers", {"name": "HealthFirst"}, admin)["id"]

    # Denial check: a nurse cannot create a department.
    anita = login(client, "anita", "anita-pass")
    r = client.post("/departments", json={"name": "Pharmacy"}, headers=anita)
    assert r.status_code == 403, r.text

    # ---- Stage 1: registration and booking (Meera) ---------------------
    meera = login(client, "meera", "meera-pass")

    patient = post(
        client,
        "/patients",
        {
            "first_name": "Peehu",
            "last_name": "Sharma",
            "age": 30,
            "sex": "female",
            "phone": "9000000001",
            "emergency_contact_name": "Raj Sharma",
            "emergency_contact_phone": "9000000002",
            "emergency_contact_relationship": "Father",
        },
        meera,
    )
    assert "date_of_birth" in patient
    patient_id = patient["id"]

    policy_id = post(
        client,
        "/insurance-policies",
        {
            "patient_id": patient_id,
            "provider_id": provider_id,
            "policy_number": "HF-12345",
            "valid_from": "2026-01-01",
            "valid_to": "2026-12-31",
        },
        meera,
    )["id"]

    visit = post(
        client,
        "/visits",
        {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "department_id": cardiology,
            "visit_type": "outpatient",
            "planned_start": "2026-10-20T09:00:00",
            "chief_complaint": "Chest pain",
        },
        meera,
    )
    assert visit["status"] == "booked"
    visit_id = visit["id"]

    # ---- Stage 2: arrival and consultation -----------------------------
    rao = login(client, "rao", "rao-pass")
    ravi = login(client, "ravi", "ravi-pass")

    visit = post(client, f"/visits/{visit_id}/check-in", {"at": "2026-10-20T09:15:00"}, anita)
    assert visit["status"] == "in progress"

    post(
        client,
        "/vital-signs",
        {
            "visit_id": visit_id,
            "systolic_bp": 150,
            "diastolic_bp": 95,
            "pulse_bpm": 104,
            "recorded_at": "2026-10-20T09:20:00",
        },
        anita,
    )

    r = client.patch(
        f"/visits/{visit_id}",
        json={"notes": "Chest pain on exertion. ECG and troponin ordered."},
        headers=rao,
    )
    assert r.status_code == 200, r.text
    assert r.json()["notes"] == "Chest pain on exertion. ECG and troponin ordered."

    lab_order = post(
        client,
        "/lab-orders",
        {"visit_id": visit_id, "lab_test_id": troponin_id, "ordered_at": "2026-10-20T09:40:00"},
        rao,
    )
    assert lab_order["status"] == "ordered"
    lab_order_id = lab_order["id"]

    # Denial check: a nurse cannot enter lab results.
    r = client.post(
        "/lab-results",
        json={
            "lab_order_id": lab_order_id,
            "result_text": "Elevated",
            "resulted_at": "2026-10-20T10:30:00",
        },
        headers=anita,
    )
    assert r.status_code == 403, r.text

    post(
        client,
        "/lab-results",
        {
            "lab_order_id": lab_order_id,
            "result_text": "Elevated",
            "resulted_at": "2026-10-20T10:30:00",
        },
        ravi,
    )
    r = client.get(f"/lab-orders/{lab_order_id}", headers=rao)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "completed"

    procedure_history_id = post(
        client,
        "/procedure-history",
        {"visit_id": visit_id, "procedure_id": ecg_id, "performed_at": "2026-10-20T10:45:00"},
        rao,
    )["id"]

    electrode_usage = post(
        client,
        "/consumable-usage",
        {
            "visit_id": visit_id,
            "consumable_id": electrodes_id,
            "quantity": 1,
            "used_at": "2026-10-20T10:45:00",
            "procedure_history_id": procedure_history_id,
        },
        anita,
    )
    assert electrode_usage["quantity"] == 1

    diagnosis = post(
        client,
        "/diagnoses",
        {"visit_id": visit_id, "description": "Unstable angina", "is_primary": True},
        rao,
    )
    assert diagnosis["is_primary"] is True

    # ---- Stage 3: admission (Dr. Rao, Meera, Anita) --------------------
    r = client.patch(f"/visits/{visit_id}", json={"visit_type": "inpatient"}, headers=rao)
    assert r.status_code == 200, r.text
    assert r.json()["visit_type"] == "inpatient"

    icu_stay = post(
        client,
        "/bed-assignments",
        {"visit_id": visit_id, "bed_id": icu_bed, "start_time": "2026-10-20T12:00:00"},
        meera,
    )
    icu_stay_id = icu_stay["id"]

    r = client.get("/beds/free", headers=meera)
    assert r.status_code == 200, r.text
    assert icu_bed not in [bed["id"] for bed in r.json()]

    post(
        client,
        "/vital-signs",
        {
            "visit_id": visit_id,
            "systolic_bp": 150,
            "diastolic_bp": 95,
            "pulse_bpm": 92,
            "recorded_at": "2026-10-20T16:00:00",
        },
        anita,
    )

    iv_usage = post(
        client,
        "/consumable-usage",
        {
            "visit_id": visit_id,
            "consumable_id": iv_set_id,
            "quantity": 1,
            "used_at": "2026-10-20T12:30:00",
        },
        anita,
    )
    assert iv_usage["quantity"] == 1

    ward_stay = post(
        client,
        f"/bed-assignments/{icu_stay_id}/transfer",
        {"bed_id": ward_bed, "at": "2026-10-21T10:00:00"},
        anita,
    )
    ward_stay_id = ward_stay["id"]
    assert ward_stay_id != icu_stay_id

    r = client.get(f"/bed-assignments/{icu_stay_id}", headers=anita)
    assert r.status_code == 200, r.text
    assert r.json()["end_time"] is not None

    # ---- Stage 4: treatment and discharge (Dr. Rao) --------------------
    for medication_id in [aspirin_id, atorvastatin_id]:
        post(
            client,
            "/prescriptions",
            {
                "visit_id": visit_id,
                "medication_id": medication_id,
                "dose": "1 tablet",
                "frequency": "once a day",
                "duration_days": 30,
                "quantity": 30,
            },
            rao,
        )

    visit = post(client, f"/visits/{visit_id}/discharge", {"at": "2026-10-22T11:00:00"}, rao)
    assert visit["status"] == "completed"

    r = client.get(f"/bed-assignments/{ward_stay_id}", headers=rao)
    assert r.status_code == 200, r.text
    assert r.json()["end_time"] is not None

    # ---- Stage 5: billing and payment (Meera) --------------------------
    # Denial check: a nurse cannot create an invoice.
    r = client.post("/invoices", json={"visit_id": visit_id}, headers=anita)
    assert r.status_code == 403, r.text

    invoice = post(client, "/invoices", {"visit_id": visit_id}, meera)
    assert invoice["status"] == "draft"
    assert re.match(r"^INV-\d{4}-\d{6}$", invoice["invoice_number"])
    invoice_id = invoice["id"]

    # Lines with no source: consultation, procedure, medication.
    for description, quantity, unit_price in [
        ("Consultation - Dr. Rao", 1, "800.00"),
        ("ECG", 1, "500.00"),
        ("Aspirin 75 mg", 30, "2.00"),
        ("Atorvastatin 40 mg", 30, "10.00"),
    ]:
        post(
            client,
            "/invoice-lines",
            {
                "invoice_id": invoice_id,
                "description": description,
                "quantity": quantity,
                "unit_price": unit_price,
            },
            meera,
        )

    # Lines with a source: lab order, bed stays, consumable usages.
    lab_line = post(
        client,
        "/invoice-lines",
        {
            "invoice_id": invoice_id,
            "source_type": "lab_order",
            "source_id": lab_order_id,
        },
        meera,
    )
    assert lab_line["quantity"] == 1
    assert Decimal(str(lab_line["unit_price"])) == Decimal("1200")

    icu_line = post(
        client,
        "/invoice-lines",
        {
            "invoice_id": invoice_id,
            "source_type": "bed_assignment",
            "source_id": icu_stay_id,
        },
        meera,
    )
    assert icu_line["quantity"] == 1
    assert Decimal(str(icu_line["unit_price"])) == Decimal("5000")

    ward_line = post(
        client,
        "/invoice-lines",
        {
            "invoice_id": invoice_id,
            "source_type": "bed_assignment",
            "source_id": ward_stay_id,
        },
        meera,
    )
    assert ward_line["quantity"] == 2
    assert Decimal(str(ward_line["unit_price"])) == Decimal("1500")

    electrode_line = post(
        client,
        "/invoice-lines",
        {
            "invoice_id": invoice_id,
            "source_type": "consumable_usage",
            "source_id": electrode_usage["id"],
        },
        meera,
    )
    assert Decimal(str(electrode_line["unit_price"])) == Decimal("150")

    iv_line = post(
        client,
        "/invoice-lines",
        {
            "invoice_id": invoice_id,
            "source_type": "consumable_usage",
            "source_id": iv_usage["id"],
        },
        meera,
    )
    assert Decimal(str(iv_line["unit_price"])) == Decimal("250")

    # The same lab order cannot be billed twice.
    r = client.post(
        "/invoice-lines",
        json={"invoice_id": invoice_id, "source_type": "lab_order", "source_id": lab_order_id},
        headers=meera,
    )
    assert r.status_code == 400, r.text

    invoice = post(client, f"/invoices/{invoice_id}/issue", {}, meera)
    assert invoice["status"] == "issued"

    r = client.get(f"/invoices/{invoice_id}", headers=meera)
    assert r.status_code == 200, r.text
    invoice = r.json()
    assert Decimal(str(invoice["total"])) == Decimal("11260.00")
    assert Decimal(str(invoice["balance"])) == Decimal("11260.00")

    # Insurer pays 10000.00 through the claim: submitted, approved, paid.
    claim = post(
        client,
        "/insurance-claims",
        {
            "invoice_id": invoice_id,
            "policy_id": policy_id,
            "amount_claimed": "10000.00",
            "submitted_date": "2026-10-22",
        },
        meera,
    )
    assert claim["status"] == "submitted"
    claim_id = claim["id"]

    claim = post(
        client,
        f"/insurance-claims/{claim_id}/approve",
        {"approved_date": "2026-10-25"},
        meera,
    )
    assert claim["status"] == "approved"

    claim = post(client, f"/insurance-claims/{claim_id}/pay", {"paid_date": "2026-10-30"}, meera)
    assert claim["status"] == "paid"

    r = client.get(f"/invoices/{invoice_id}", headers=meera)
    assert r.status_code == 200, r.text
    invoice = r.json()
    assert Decimal(str(invoice["balance"])) == Decimal("1260.00")
    assert invoice["status"] == "issued"

    # Peehu pays the remaining 1260.00 by UPI.
    payment = post(
        client,
        "/payments",
        {
            "invoice_id": invoice_id,
            "amount": "1260.00",
            "paid_at": "2026-10-31",
            "method": "UPI",
            "reference": "UPI-998877",
        },
        meera,
    )
    assert payment["invoice_id"] == invoice_id

    r = client.get(f"/invoices/{invoice_id}", headers=meera)
    assert r.status_code == 200, r.text
    invoice = r.json()
    assert Decimal(str(invoice["balance"])) == Decimal("0")
    assert invoice["status"] == "paid"
