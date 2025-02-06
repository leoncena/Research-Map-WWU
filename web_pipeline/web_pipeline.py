from organisation_pipeline import OrganisationPipeline
from person_pipeline import PersonPipeline
import os

MONGODB_FROM_URI = os.getenv('PIPELINE_ENV_MONGODB_FROM_URI', "mongodb://localhost:27017/")
MONGODB_TO_URI = os.getenv('PIPELINE_ENV_MONGODB_TO_URI', "mongodb://localhost:27017/")
MONGODB_FROM_DB = "FLK_Data_Lake"
MONGODB_TO_DB = "FLK_Web"

organisation_pipeline = OrganisationPipeline(mongodb_from_uri=MONGODB_FROM_URI, mongodb_from_database=MONGODB_FROM_DB, mongodb_to_uri=MONGODB_TO_URI, mongodb_to_database=MONGODB_TO_DB)
organisation_pipeline.export_organisations(organisation_id=31923392)

person_pipeline = PersonPipeline(mongodb_from_uri=MONGODB_FROM_URI, mongodb_from_database=MONGODB_FROM_DB, mongodb_to_uri=MONGODB_TO_URI, mongodb_to_database=MONGODB_TO_DB)
person_pipeline.export_persons(organisation_id=31923392)