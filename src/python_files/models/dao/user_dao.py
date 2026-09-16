
from src.python_files.config.database import get_session
from src.python_files.models.user import User


def get_user(username: str) -> User | None:
    with get_session() as session:
        return session.get(User, username)


def add_user(user: User) -> None:
    with get_session() as session:
        session.add(user)
        session.commit()


def delete_user(username: str) -> None:
    with get_session() as session:
        user = session.get(User, username)

        if user:
            session.delete(user)
            session.commit()