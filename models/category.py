from sqlalchemy import (
    Column,
    Integer,
    String
)
from sqlalchemy.orm import relationship
from config.database import Base

class Category(Base):
    __tablename__ = "Category"

    id: int = Column(Integer, primary_key = True, autoincrement = True)
    category_name: str = Column(String(30), nullable = False, index = True)
    category_icon: str = Column(String(100), nullable = False)

    subcategories = relationship('Subcategory', back_populates = 'category', cascade = 'delete', lazy = 'joined')

    @property
    def count_total_ads(self) -> int:
        total_ads = []
        for subcategory in self.subcategories:
            for ad in subcategory.ads:
                if ad.status_id == 1:
                    total_ads.append(ad)
        return len(total_ads)