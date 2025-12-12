from core.db import SessionLocal
from core.models import User
from domain.interfaces.user_repo_interface import IUserRepository
from domain.entities.user_entity import UserEntity
from sqlalchemy.orm import Session

class UserRepository(IUserRepository):
    def __init__(self, db_session: Session) -> None:
        self.db = db_session

    def add_user(self, user: UserEntity) -> User:
        db_obj = User(
            plate=user.plate,
            country=user.country
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_user_by_plate(self, plate: str) -> User | None:
        return self.db.query(User).filter(User.plate == plate).first()