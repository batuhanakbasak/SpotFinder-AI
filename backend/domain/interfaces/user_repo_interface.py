from abc import ABC, abstractmethod
from domain.entities.user_entity import UserEntity
class IUserRepository(ABC):
    @abstractmethod
    def add_user(self, user: UserEntity):
        pass

    @abstractmethod
    def get_user_by_plate(self, plate: str):
        pass