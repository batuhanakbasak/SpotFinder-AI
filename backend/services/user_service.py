from domain.entities.user_entity import UserEntity
from infrastructure.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def create_user(self, plate: str, country: str):
        
        existing = self.repo.get_user_by_plate(plate)
        if existing:
            return None  
        user_entity = UserEntity(plate=plate, country=country)
        return self.repo.add_user(user_entity)

    def get_user_by_plate(self, plate: str):
        return self.repo.get_user_by_plate(plate)