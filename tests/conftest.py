"""
Pytest configuration and fixtures for FastAPI application tests.

This module provides common fixtures used across all test modules,
including the TestClient for making HTTP requests to the FastAPI app.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


@pytest.fixture(autouse=True)
def reset_activities_state():
    """
    Fixture that automatically resets the in-memory activities database
    to its initial state before each test runs.
    
    This ensures that modifications made by one test (e.g., adding or removing
    participants) don't affect subsequent tests.
    """
    # Store initial state before this fixture runs (on first call)
    initial_state = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Team-based basketball practice and competitive games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu", "nina@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Swim training and fitness sessions for all levels",
            "schedule": "Mondays and Wednesdays, 5:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": ["ryan@mergington.edu", "zoe@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media art projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu", "lucas@mergington.edu"]
        },
        "Drama Club": {
            "description": "Practice acting, stagecraft, and produce school performances",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Study advanced math topics and prepare for competitions",
            "schedule": "Tuesdays, 4:30 PM - 5:30 PM",
            "max_participants": 12,
            "participants": ["sophia@mergington.edu", "noah@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments and science exploration projects",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu", "mason@mergington.edu"]
        }
    }
    
    # Reset activities to initial state before test
    activities.clear()
    activities.update(copy.deepcopy(initial_state))
    
    yield  # Run the test


@pytest.fixture
def sample_activity_name():
    """
    Fixture that provides a valid activity name from the pre-loaded database.
    
    Returns:
        str: A valid activity name that exists in the database.
    """
    return "Chess Club"


@pytest.fixture
def sample_participant_email():
    """
    Fixture that provides a valid participant email that exists in the database.
    
    Returns:
        str: A valid email of a participant in the sample activity.
    """
    return "michael@mergington.edu"


@pytest.fixture
def non_existent_activity():
    """
    Fixture that provides an activity name that does not exist.
    
    Returns:
        str: An activity name that is not in the database.
    """
    return "NonExistentActivity123"


@pytest.fixture
def non_existent_participant():
    """
    Fixture that provides a participant email that does not exist in any activity.
    
    Returns:
        str: An email address not in the database.
    """
    return "nonexistent@mergington.edu"


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient instance for making HTTP requests
    to the FastAPI application without needing a running server.
    
    Returns:
        TestClient: A test client connected to the FastAPI app.
    """
    return TestClient(app)
