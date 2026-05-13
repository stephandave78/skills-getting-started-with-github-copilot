from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
initial_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(initial_activities))
    yield


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity_names = {"Chess Club", "Programming Class"}

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert expected_activity_names.issubset(data.keys())
    assert data["Chess Club"]["max_participants"] == 12


def test_signup_for_activity_adds_new_participant():
    # Arrange
    email = "newstudent@mergington.edu"
    activity_path = "/activities/Chess%20Club/signup"

    # Act
    response = client.post(activity_path, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_bad_request():
    # Arrange
    email = "emma@mergington.edu"
    activity_path = "/activities/Programming%20Class/signup"

    # Act
    response = client.post(activity_path, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_returns_success():
    # Arrange
    email = "john@mergington.edu"
    activity_path = "/activities/Gym%20Class/participants"

    # Act
    response = client.delete(activity_path, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Gym Class"}
    assert email not in activities["Gym Class"]["participants"]


def test_remove_missing_participant_returns_not_found():
    # Arrange
    activity_path = "/activities/Gym%20Class/participants"
    missing_email = "missing@mergington.edu"

    # Act
    response = client.delete(activity_path, params={"email": missing_email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_signup_unknown_activity_returns_not_found():
    # Arrange
    activity_path = "/activities/Unknown%20Club/signup"
    email = "test@mergington.edu"

    # Act
    response = client.post(activity_path, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_unknown_activity_returns_not_found():
    # Arrange
    activity_path = "/activities/Unknown%20Club/participants"
    email = "test@mergington.edu"

    # Act
    response = client.delete(activity_path, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
