import pytest
from api import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture()
def example_api_response():
    return [
        {
            "alert": None,
            "cause_of_event": "earthquake",
            "cdi": None,
            "depth": 1.96,
            "dmin": 0.006074,
            "earthquake_id": "nc75025077",
            "felt": None,
            "gap": 165.0,
            "lat": "38.833332",
            "lon": "-122.878830",
            "magnitude": 0.78,
            "magtype": "md",
            "mmi": None,
            "network_name": "nc",
            "nst": 16,
            "significance": 9,
            "status": "automatic",
            "time": "Fri, 21 Jun 2024 20:18:40 GMT",
            "title": "M 0.8 - 12 km NW of The Geysers, CA"
        },
        {
            "alert": None,
            "cause_of_event": "earthquake",
            "cdi": None,
            "depth": 10.88,
            "dmin": 0.05398,
            "earthquake_id": "ci40806056",
            "felt": None,
            "gap": 63.0,
            "lat": "33.494499",
            "lon": "-116.480331",
            "magnitude": 1.04,
            "magtype": "ml",
            "mmi": None,
            "network_name": "ci",
            "nst": 26,
            "significance": 17,
            "status": "reviewed",
            "time": "Fri, 21 Jun 2024 20:16:06 GMT",
            "title": "M 1.0 - 19 km ESE of Anza, CA"
        },
        {
            "alert": None,
            "cause_of_event": "earthquake",
            "cdi": None,
            "depth": 2.02,
            "dmin": 0.008128,
            "earthquake_id": "nc75025072",
            "felt": None,
            "gap": 174.0,
            "lat": "38.821999",
            "lon": "-122.845337",
            "magnitude": 0.24,
            "magtype": "md",
            "mmi": None,
            "network_name": "nc",
            "nst": 8,
            "significance": 1,
            "status": "deleted",
            "time": "Fri, 21 Jun 2024 20:10:08 GMT",
            "title": "M 0.2 - 9 km NW of The Geysers, CA"
        }]
