from app.core.db import Base, engine


# from app.model.models import Chat, File, Message, User


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()
