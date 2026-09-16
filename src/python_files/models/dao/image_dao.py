from sqlalchemy import select

from src.python_files.config.database import get_session
from src.python_files.models.image import Image


def get_image(image_id: int) -> Image | None:
    with get_session() as session:
        return session.get(Image, image_id)


def add_image(image: Image) -> None:
    with get_session() as session:
        session.add(image)
        session.commit()


def get_images_by_user(username: str) -> list[Image]:
    with get_session() as session:
        return list(
            session.scalars(
                select(Image)
                .where(Image.username == username)
            )
        )


def delete_image(image_id: int) -> None:
    with get_session() as session:
        image = session.get(Image, image_id)

        if image is not None:
            session.delete(image)
            session.commit()