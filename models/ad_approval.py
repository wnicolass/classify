from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from config.database import Base

class AdApproval(Base):
    __tablename__ = 'AdApproval'
    ad_id: int = Column(Integer, ForeignKey('Ad.ad_id'), primary_key = True, nullable = False)
    admin_id: int = Column(Integer, ForeignKey('Admin.admin_id'), primary_key = True, nullable = False)
    approved_at: datetime = Column(DateTime, default = datetime.now())

    admin = relationship('Admin', back_populates = "ads")
    ad = relationship('Ad', back_populates = 'admins')
