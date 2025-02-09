import pytest
from fastapi.testclient import TestClient

from tbsky_session.core import User
from tbsky_session.core.repository.users_repository import UserRepository
from tbsky_session.schemas import UserCreate, UserLogin


class TestAuthResource:

    def test_register(self, client: TestClient):
        # given
        user_data = {
            "first_name": "Test",
            "last_name": "Test",
            "email": "test@example.com",
            "password": "A_Bdv7`82T+t",
        }
        # when
        response = client.post(
            "api/v1/security/register",
            json=user_data,
        )
        # then
        assert response.status_code == 200
        assert response.json() is None

    async def test_login(self, client: TestClient):
        # given
        user_data = {
            "email": "test@example.com",
            "password": "A_Bdv7`82T+t",
        }
        user_repo = UserRepository()
        await user_repo.add(
            User(
                first_name="Test",
                last_name="Test",
                email="test@example.com",
                hashed_password="A_Bdv7`82T+t",
            )
        )
        # when
        response = client.post(
            "api/v1/security/login",
            json=user_data,
        )
        # then
        assert response.status_code == 200
        assert response.json() is None
