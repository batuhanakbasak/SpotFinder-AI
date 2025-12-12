from core.db import Base, engine
from core.models import Zone, ParkingSession, User, UserLocation

Base.metadata.create_all(bind=engine)
print("✅ Tablolar başarılı bir şekilde oluşturuldu veya zaten mevcut.")