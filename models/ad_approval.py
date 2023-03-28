from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    ForeignKey,
    Table,
    text
)
from config.database import Base

ad_approval = Table(
    'AdApproval',
    Base.metadata,
    Column('ad_id', Integer, ForeignKey('Ad.ad_id'), primary_key = True, nullable = False),
    Column('admin_id', Integer, ForeignKey('Admin.admin_id'), primary_key = True, nullable = False),
    Column('approved_at', DateTime, server_default = text('NOW()'))
)
