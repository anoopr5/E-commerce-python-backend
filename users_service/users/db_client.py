from django.conf import settings
from azure.cosmos import CosmosClient, PartitionKey, exceptions

class CosmosDBClient:
    def __init__(self,container_name):
        self.client = CosmosClient(settings.COSMOS_DB['ENDPOINT'], settings.COSMOS_DB['PRIMARY_KEY'])
        self.database = self.client.create_database_if_not_exists(id=settings.COSMOS_DB['DATABASE_ID'])
        self.container = self.database.create_container_if_not_exists(
            id=container_name,
            partition_key=PartitionKey(path="/email"),
            offer_throughput=400
            )

    def create_user(self, item):
        try:
            return self.container.create_item(body=item)
        except exceptions.CosmosResourceExistsError:
            return None
    
    def read_item(self, item_key, item_value):
        query = f"SELECT * FROM c WHERE c.{item_key} = '{item_value}'"
        items = list(self.container.query_items(query=query, enable_cross_partition_query=True))
        if items:
            return items[0]
        return None
    
    def get_user(self, user_id):
        try:
            return self.container.read_item(item=user_id, partition_key=user_id)
        except exceptions.CosmosResourceNotFoundError:
            return None


    def update_user(self, user):
        self.container.upsert_item(body=user)

    def delete_user(self, user_id):
        self.container.delete_item(item=user_id, partition_key=user_id)