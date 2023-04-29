from sqlalchemy import Column, ForeignKey, Integer, String, Table

from config.database import Base


field_value = Table(
    'FieldValue',
    Base.metadata,
    Column(
        'field_definition_id', 
        Integer, 
        ForeignKey('FieldDefinition.id'), 
        primary_key = True
    ),
    Column('ad_id', Integer, ForeignKey('Ad.id'), primary_key = True),
    Column('f_value', String(100), nullable = False),
)