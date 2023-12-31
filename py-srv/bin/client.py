from surrealdb import Surreal
import logging

logging.basicConfig(level=logging.INFO)

class SurrealClient:
    
    def __init__(self) -> None:
        self.isSeeded = False

    async def query(self, sql):
        host = "db"
        port = 8000
        async with Surreal(f"ws://{host}:{port}/rpc") as db:
            await db.signin({"user": "root", "pass": "pass"})
            await db.use("test", "test")
            x = await db.query(sql)
            return x[0]['result']
            

    async def seed(self):
        if self.isSeeded == True:
            return
        
        results = []
        records = [
            { "name": "Fiz", "color": "White", "my_id": '1' },
            { "name": "Blueberry", "color": "Blue", "my_id": '2' },
            { "name": "Grape", "color": "Black", "my_id": '3' },
            { "name": "Cola", "color": "Brown", "my_id": '4' }
        ]
        for record in records:
            sql = "insert into pop {"
            for k, v in record.items():
                sql += f"{k}: '{v}',"
            sql += "};"
            results.append(await self.query(sql))

        self.isSeeded = True

        return results

class Endpoint:
    """Create singleton"""
    def __new__(cls):
         if not hasattr(cls, 'instance'):
             cls.instance = super(Endpoint, cls).__new__(cls)
         return cls.instance
    
    def __init__(self) -> None:
        self.client = SurrealClient()

    async def get_all(self):
        await self.client.seed()
        sql = 'select * from pop'
        return await self.client.query(sql)
    
    async def filter_by(self, filter, filter_val):
        await self.client.seed()
        sql = f'select * from pop where {filter} = "{filter_val}"'
        return await self.client.query(sql)
    
    async def delete(self, filter, filter_val):
        await self.client.seed()
        sql = f'delete from pop where {filter} = "{filter_val}"'
        await self.client.query(sql)
        return await self.get_all()
    
    async def insert(self, new_name, new_color):
        await self.client.seed()
        records = [
            { "name": new_name, "color": new_color, "my_id": '0' }
        ]

        sql = ''
        for record in records:
            sql = "insert into pop {"
            for k, v in record.items():
                sql += f"{k}: '{v}',"
            sql += "};"
            await self.client.query(sql)
        return await self.get_all()
    
    async def update(self, filter, filter_val):
        await self.client.seed()
        logging.info(f"filter: {filter}, value: {filter_val}")
        sql = f"update pop set name='updated', color='updated', my_id='99' where {filter} = '{filter_val}';"
        await self.client.query(sql)
        return await self.get_all()