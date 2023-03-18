import asyncpg
from dataclasses import dataclass
from transliterate import translit


@dataclass()
class GroupButtons:
    name: str
    en_name: str
    users: str = None
    hidden: int = 0
    specification: str = 'Описание группы кнопок'


class GroupsButtonsDatabase:
    pool: asyncpg.Pool
    groups: dict = {}
    en_names_groups: list

    #
    # __________CREATE__________
    async def create(self, list_groups = None, pool: asyncpg.Pool = None):
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

        if not list_groups:
            list_groups = list(self.groups)

        for group in list_groups:
            if group not in self.groups:
                query = """INSERT INTO groups_buttons (name) VALUES ($1) ON CONFLICT (name) DO NOTHING;"""
                async with self.pool.acquire(): await self.pool.execute(query, group)

        self.groups = {}
        self.en_names_groups = []
        for group in list_groups:
            await self.read(group)

        await self.dell_old()

    #
    # __________DELETE OLD GROUPS__________
    async def dell_old(self):

        query = """SELECT * FROM groups_buttons;"""
        async with self.pool.acquire():
            groups_all = await self.pool.fetch(query)
        query = ""
        for group in groups_all:
            if group['name'] not in self.groups:
                query += f"DELETE FROM groups_buttons WHERE name = ('{group['name']}');"
        if query != "":
            async with self.pool.acquire(): await self.pool.execute(query)

    #
    # __________READ__________
    async def read(self, group_name: str):

        # 'name, work_file, num_block, size_blok, shablon_file, active'
        query = """SELECT * FROM groups_buttons WHERE name = $1;"""
        async with self.pool.acquire():
            gr = await self.pool.fetch(query, group_name)
        if gr:
            en_name = group_name.lower()[:30].replace(' ', '_')
            en_name = translit(en_name, language_code='ru', reversed=True)

            gr = gr[0]
            group = GroupButtons(
                        name=group_name,
                        en_name=en_name,
                        users=gr['users'],
                        specification=gr['specification'],
                        hidden=gr['hidden']
                        )
            self.groups.update({group_name: group})
            self.en_names_groups.append(en_name)

    #
    # __________WRITE__________
    async def write(self, group_name: str, tools, values):

        columns = tools
        for i in range(len(columns)):
            if values[i] in ("NONE", "None", "none", "NULL", "null", "Null", None, ''):
                query = f"""UPDATE groups_buttons SET {columns[i]} = NULL WHERE name = $1;"""
            else:
                query = f"""UPDATE groups_buttons SET {columns[i]} = '{values[i]}' WHERE name = $1;"""
            async with self.pool.acquire():
                await self.pool.execute(query, group_name)

        await self.create()

    #
    # __________DELETE TABLE__________
    async def dell(self):
        query = 'DROP TABLE public.groups_buttons;'
        async with self.pool.acquire(): await self.pool.execute(query)

    async def get_all_from_bd(self):
        query = """SELECT * FROM groups_buttons"""
        async with self.pool.acquire():
            all = await self.pool.fetch(query)
        all_groups = [dict(row) for row in all]
        return all_groups


groups_db = GroupsButtonsDatabase()
