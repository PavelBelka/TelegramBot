from psycopg import sql

class Database:
    def create_pool(self, pool):
        self._pool = pool

    async def delete_pool(self):
        await self._pool.close()

    async def create_connection(self):
        return await self._pool.getconn()

    async def delete_connection(self, connect):
        return await self._pool.putconn(connect)

    @staticmethod
    def create_cursor(connection):
        cursor = connection.cursor()
        return cursor

    @staticmethod
    async def create_table(cur, name):
        create = "CREATE TABLE {} (id serial PRIMARY KEY, " \
                 "date timestamp, " \
                 "income boolean DEFAULT FALSE, " \
                 "category VARCHAR(18), " \
                 "amount BIGINT DEFAULT 0);"
        create = sql.SQL(create).format(sql.Identifier('fin', name))
        await cur.execute(create)

    @staticmethod
    async def verify_table(cur, name):
        check = '''SELECT EXISTS(SELECT 1 FROM information_schema.tables
                                 WHERE table_name = %s AND
                                 table_schema = 'fin');'''
        await cur.execute(check, (name,))
        return (await cur.fetchone())[0]

    @staticmethod
    async def delete_table(cursor, name):
        delete = "DROP TABLE {}"
        query_delete = sql.SQL(delete).format(sql.Identifier('fin', name))
        await cursor.execute(query_delete)

    @staticmethod
    async def insert_record(cursor, name, date, income, category, amount):
        insert = '''INSERT INTO {} (date, income, category, amount) VALUES(%s, %s, %s, %s);'''
        query_insert = sql.SQL(insert).format(sql.Identifier('fin', name))
        await cursor.execute(query_insert, (date, income, category, amount))

    @staticmethod
    async def select_records_date(cursor, name, before, after):
        select = '''SELECT * FROM {} WHERE date >= %s and date < %s;'''
        query_select = sql.SQL(select).format(sql.Identifier('fin', name))
        await cursor.execute(query_select, (before, after))
        return await cursor.fetchall()

    @staticmethod
    async def delete_record(cursor, name, id_record):
        delete = '''DELETE FROM {} WHERE id = %s;'''
        query_delete = sql.SQL(delete).format(sql.Identifier('fin', name))
        await cursor.execute(query_delete, (id_record,))

    @staticmethod
    async def update_record(cursor, name, dat, income, category, amount, id_row):
        update = '''UPDATE {} SET date=(%s), income=(%s), category=(%s), amount=(%s) WHERE id=(%s);'''
        query_update = sql.SQL(update).format(sql.Identifier('fin', name))
        await cursor.execute(query_update, (dat, income, category, amount, id_row))

    @staticmethod
    async def select_last_record(cursor, name):
        order = '''SELECT * FROM {} ORDER BY id DESC LIMIT 1'''
        query_order = sql.SQL(order).format(sql.Identifier('fin', name))
        await cursor.execute(query_order)
        return await cursor.fetchall()
