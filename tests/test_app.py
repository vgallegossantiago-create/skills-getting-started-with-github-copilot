from copy import deepcopy
from urllib.parse import quote

from fastapi.testclient import TestClient
import pytest

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = deepcopy(app_module.activities)
    yield
    app_module.activities = deepcopy(original)


def test_get_activities_returns_activities():
    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    email = "emma@mergington.edu"
    client.post("/activities/Programming Class/signup", params={"email": email})

    # Act
    response = client.post("/activities/Programming Class/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_removes_participant():
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"
    path = f"/activities/{quote(activity)}/participants/{quote(email)}"

    # Act
    response = client.delete(path)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity}"
    assert email not in app_module.activities[activity]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    email = "missing@mergington.edu"
    activity = "Chess Club"
    path = f"/activities/{quote(activity)}/participants/{quote(email)}"

    # Act
    response = client.delete(path)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
