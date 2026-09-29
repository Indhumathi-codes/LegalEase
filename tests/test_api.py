import os

os.environ["DEMO_MODE"] = "true"


from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_generate_demo():

    payload = {

        "document_type":
            "Freelance Work Contract",

        "parties":
            "Jane Doe (Freelancer), "
            "ABC Corp (Client)",

        "terms": [

            "Payment within 30 days",

            "Confidentiality must be maintained"
        ],

        "effective_date":
            "2026-09-28",

        "jurisdiction":
            "Not specified",

        "additional_instructions":
            ""
    }


    response = client.post(
        "/api/v1/generate",
        json=payload
    )


    assert response.status_code == 200


    body = response.json()


    assert body["content"]


    assert (
        "Payment within 30 days"
        in body["content"]
    )
