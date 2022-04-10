import asyncpg
from dataclasses import dataclass

from work_vs_db.db_buttons import buttons_db


@dataclass()
class GroupButtons:
    name: str
    users: str = None
    hidden: int = 0
    specification: str = 'Описание группы кнопок'



class GroupsButtonsDatabase:
    pool: asyncpg.Pool
    groups: dict

    #
    # __________CREATE__________
    async def create(self, pool: asyncpg.Pool):
        if pool: self.pool = pool
        # await self.dell()
        query = """CREATE TABLE IF NOT EXISTS public.groups_buttons
                (
                    name varchar(30) COLLATE pg_catalog."default" NOT NULL,
                    hidden smallint NOT NULL DEFAULT 0,
                    users varchar DEFAULT NULL,                    
                    specification varchar DEFAULT 'Описание группы кнопок',
                    CONSTRAINT groups_buttons_pkey PRIMARY KEY (name)
                );
                    """
        async with self.pool.acquire(): await self.pool.execute(query)

        for i in buttons_db.buttons_groups:
            query = """INSERT INTO groups_buttons (name) VALUES ($1) ON CONFLICT (name) DO NOTHING;"""
            async with self.pool.acquire(): await self.pool.execute(query, i)

        self.groups = {i: await self.read(i) for i in buttons_db.buttons_groups}

    #
    # __________READ__________
    async def read(self, group_name: str):

        # 'name, work_file, num_block, size_blok, shablon_file, active'
        query = """SELECT * FROM groups_buttons WHERE name = $1;"""
        async with self.pool.acquire():
            gr = await self.pool.fetch(query, group_name)
        group = None
        if gr:
            gr = gr[0]
            group = GroupButtons(
                        name=group_name,
                        users=gr['users'],
                        specification=gr['specification'],
                        hidden=gr['hidden']
                        )
        return group

    #
    # __________WRITE__________
    async def write(self, group_name: str, specification):

        query = """INSERT INTO groups_buttons (name) VALUES ($1) ON CONFLICT (name) DO NOTHING;"""
        async with self.pool.acquire(): await self.pool.execute(query, group_name)

        query = f"""UPDATE groups_buttons SET specification = ({specification}) WHERE name = $1;"""
        async with self.pool.acquire(): await self.pool.execute(query, group_name)

        group = await self.read(group_name)
        self.groups.update({group_name: group})

    #
    # __________DELETE TABLE__________
    async def dell(self):

        query = 'DROP TABLE public.groups_buttons;'
        async with self.pool.acquire(): await self.pool.execute(query)


groups_db = GroupsButtonsDatabase()
