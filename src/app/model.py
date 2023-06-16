from pynamodb.models import Model
from pynamodb.attributes import NumberAttribute
import os


class BotUsers(Model):
    class Meta:
        table_name = os.getenv(
            "USERS_DB_TABLE_NAME",
        )
        host = os.getenv("DYNAMODB_HOST", None)
        # Specifies the region
        region = os.getenv("AWS_REGION", None)
        # Specifies the write capacity
        write_capacity_units = 1
        # Specifies the read capacity
        read_capacity_units = 1

    id = NumberAttribute(hash_key=True)
