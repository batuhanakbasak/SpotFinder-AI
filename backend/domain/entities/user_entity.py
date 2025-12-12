from datetime import datetime
class UserEntity:
    def __init__(self, plate: str, country: str):
        self.plate = plate
        self.country = country
        self.created_at = datetime.utcnow()