from sqlalchemy import (
    Column,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from config.database import Base
from models.user import user_login_data_ext

class ExternalProvider(Base):
    __tablename__ = 'ExternalProvider'

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    ext_provider_name: str = Column(String(50), nullable = False)
    end_point_url: str = Column(String(100), nullable = False)

    user = relationship('UserAccount', back_populates = 'ext_provider', secondary = user_login_data_ext)