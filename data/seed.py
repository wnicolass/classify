from sqlalchemyseeder import ResolvingSeeder
from config.database import DbSession
from models.__all_models import (
    Category,
    Subcategory,
    User,
    Feature,
    Address,
    Admin,
    Ad,
    FieldDefinition,
    AdApproval,
    SubcategoryFieldDefinition,
    FieldValue
)

def seed_data() -> None:
    with DbSession() as db_session:
        seeder = ResolvingSeeder(db_session)
        for model in [Category, Subcategory, User, Feature, Address, Admin, Ad, FieldDefinition, AdApproval, SubcategoryFieldDefinition, FieldValue]:
            seeder.registry.register(model)
        inserted_data = seeder.load_entities_from_json_file('data/data.json')
        db_session.commit()
