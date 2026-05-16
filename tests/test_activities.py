"""
Integration tests for the Mergington High School API.

These tests follow the AAA (Arrange, Act, Assert) pattern:
- Arrange: Set up test data and context
- Act: Execute the HTTP request
- Assert: Verify the response status code and content
"""

import pytest


class TestRootEndpoint:
    """Tests for the GET / endpoint (root redirect)."""

    def test_root_redirects_to_static_index(self, client):
        """
        Arrange: Client is ready
        Act: Make GET request to /
        Assert: Response redirects to /static/index.html with status 307
        """
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Client is ready
        Act: Make GET request to /activities
        Assert: Response contains all 9 activities with correct structure
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Drama Club" in activities

    def test_get_activities_includes_activity_details(self, client):
        """
        Arrange: Client is ready
        Act: Make GET request to /activities
        Assert: Each activity has required fields (description, schedule, max_participants, participants)
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        
        # Check structure of a sample activity
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestGetActivityParticipantsEndpoint:
    """Tests for the GET /activities/{activity_name}/participants endpoint."""

    def test_get_participants_for_existing_activity(self, client, sample_activity_name):
        """
        Arrange: Activity name "Chess Club" exists in database
        Act: Make GET request to /activities/Chess Club/participants
        Assert: Response returns 200 and list of participants
        """
        # Act
        response = client.get(f"/activities/{sample_activity_name}/participants")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "participants" in data
        assert isinstance(data["participants"], list)
        assert len(data["participants"]) > 0
        assert "michael@mergington.edu" in data["participants"]

    def test_get_participants_for_nonexistent_activity(self, client, non_existent_activity):
        """
        Arrange: Activity name does not exist in database
        Act: Make GET request to /activities/NonExistentActivity123/participants
        Assert: Response returns 404 with appropriate error message
        """
        # Act
        response = client.get(f"/activities/{non_existent_activity}/participants")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_get_participants_returns_correct_structure(self, client):
        """
        Arrange: Client is ready
        Act: Make GET request to /activities/Programming Class/participants
        Assert: Response has correct JSON structure with participants list
        """
        # Act
        response = client.get("/activities/Programming Class/participants")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "participants" in data
        participants = data["participants"]
        assert "emma@mergington.edu" in participants
        assert "sophia@mergington.edu" in participants


class TestDeleteActivityParticipantEndpoint:
    """Tests for the DELETE /activities/{activity_name}/participants endpoint."""

    def test_delete_existing_participant_from_activity(self, client, sample_activity_name, sample_participant_email):
        """
        Arrange: Participant exists in Chess Club activity
        Act: Make DELETE request to remove the participant
        Assert: Response returns 200 and participant is removed
        """
        # Arrange: Verify participant exists before deletion
        response_before = client.get(f"/activities/{sample_activity_name}/participants")
        assert sample_participant_email in response_before.json()["participants"]

        # Act
        response = client.delete(
            f"/activities/{sample_activity_name}/participants",
            params={"email": sample_participant_email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_participant_email in data["message"]
        assert sample_activity_name in data["message"]

        # Verify participant was actually removed
        response_after = client.get(f"/activities/{sample_activity_name}/participants")
        assert sample_participant_email not in response_after.json()["participants"]

    def test_delete_participant_from_nonexistent_activity(self, client, non_existent_activity, sample_participant_email):
        """
        Arrange: Activity does not exist
        Act: Make DELETE request to remove participant from nonexistent activity
        Assert: Response returns 404 with error message
        """
        # Act
        response = client.delete(
            f"/activities/{non_existent_activity}/participants",
            params={"email": sample_participant_email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_delete_nonexistent_participant_from_activity(self, client, sample_activity_name, non_existent_participant):
        """
        Arrange: Participant email does not exist in the activity
        Act: Make DELETE request to remove nonexistent participant
        Assert: Response returns 404 with error message
        """
        # Act
        response = client.delete(
            f"/activities/{sample_activity_name}/participants",
            params={"email": non_existent_participant}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Participant not found" in data["detail"]

    def test_delete_requires_email_parameter(self, client, sample_activity_name):
        """
        Arrange: No email parameter is provided
        Act: Make DELETE request without email query parameter
        Assert: Response returns 422 (validation error)
        """
        # Act
        response = client.delete(f"/activities/{sample_activity_name}/participants")

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestActivitySignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant_to_activity(self, client, sample_activity_name):
        """
        Arrange: New participant email not yet signed up for activity
        Act: Make POST request to sign up
        Assert: Response returns 200 and participant is added
        """
        # Arrange
        new_email = "newsignup@mergington.edu"
        
        # Verify participant is not in activity before signup
        response_before = client.get(f"/activities/{sample_activity_name}/participants")
        assert new_email not in response_before.json()["participants"]

        # Act
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": new_email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert new_email in data["message"]

        # Verify participant was actually added
        response_after = client.get(f"/activities/{sample_activity_name}/participants")
        assert new_email in response_after.json()["participants"]

    def test_signup_to_nonexistent_activity(self, client, non_existent_activity):
        """
        Arrange: Activity does not exist
        Act: Make POST request to sign up for nonexistent activity
        Assert: Response returns 404 with error message
        """
        # Act
        response = client.post(
            f"/activities/{non_existent_activity}/signup",
            params={"email": "student@mergington.edu"}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_already_signed_up_participant(self, client, sample_activity_name, sample_participant_email):
        """
        Arrange: Participant is already signed up for the activity
        Act: Make POST request to sign up again
        Assert: Response returns 400 with error message
        """
        # Act
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_participant_email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_signup_requires_email_parameter(self, client, sample_activity_name):
        """
        Arrange: No email parameter is provided
        Act: Make POST request without email query parameter
        Assert: Response returns 422 (validation error)
        """
        # Act
        response = client.post(f"/activities/{sample_activity_name}/signup")

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
