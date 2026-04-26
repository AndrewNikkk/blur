from app.core.db import Base, engine


# from app.model.models import Chat, File, Message, User


def init_db():
    # Импорт моделей нужен, чтобы таблицы зарегистрировались в Base.metadata.
    # Без него create_all будет работать с пустым набором таблиц.
    from app.model import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()
