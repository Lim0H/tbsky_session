__all__ = ["UserRepository"]


from ..models import User
from ..repository import BaseDbRepository


class UserRepository(BaseDbRepository[User]):
    model = User
