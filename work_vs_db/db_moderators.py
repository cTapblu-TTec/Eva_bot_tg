import asyncpg
from dataclasses import dataclass

from data.config import ADMINS


@dataclass()
class Moderator:
    moderator_id: int
    user_name: str
    access_to_buttons_tools: str
    access_to_files_tools: str
    access_to_groups_tools: str
    access_to_users_tools: str
    access_to_state_tools: str


class ModeratorsDatabase:
    pool: asyncpg.Pool
    moderators = {}

    async def init(self, pool):
        self.pool = pool
        await self.create()

    # __________CREATE__________
    async def create(self):
        # await self.dell()
        query = """CREATE TABLE IF NOT EXISTS public.moderators
                (
                    moderator_id integer NOT NULL,
                    user_name varchar(30),
                    access_to_buttons_tools varchar DEFAULT 'all',
                    access_to_files_tools varchar DEFAULT 'all',
                    access_to_groups_tools varchar DEFAULT 'all',
                    access_to_users_tools varchar DEFAULT 'all',
                    access_to_state_tools varchar DEFAULT 'all',
                    CONSTRAINT moderators_pkey PRIMARY KEY (moderator_id)
                );"""
        async with self.pool.acquire():
            await self.pool.execute(query)

        moderators_list = await self.read(command='get_moderators_list')
        for moderator_id in moderators_list:
            await self.read(moderator_id)

    #
    # __________READ__________
    async def read(self, moderator_id=None, command=None):

        if command == 'get_moderators_list':
            query = """SELECT moderator_id FROM moderators;"""
            async with self.pool.acquire():
                answer = await self.pool.fetch(query)
            moderators_list = []
            for i in answer:
                moderators_list.append(i['moderator_id'])
            return moderators_list

        elif command is None and moderator_id is not None:
            query = """SELECT * FROM moderators WHERE moderator_id = $1;"""
            async with self.pool.acquire():
                answer = await self.pool.fetch(query, moderator_id)
            if answer:
                answer = answer[0]
                moderator = Moderator(
                    moderator_id=moderator_id,
                    user_name=answer['user_name'],
                    access_to_buttons_tools=await self.format_tools_from_db(answer['access_to_buttons_tools']),
                    access_to_files_tools=await self.format_tools_from_db(answer['access_to_files_tools']),
                    access_to_groups_tools=await self.format_tools_from_db(answer['access_to_groups_tools']),
                    access_to_users_tools=await self.format_tools_from_db(answer['access_to_users_tools']),
                    access_to_state_tools=await self.format_tools_from_db(answer['access_to_state_tools'])
                )
                self.moderators.update({moderator_id: moderator})

    #
    # __________WRITE__________
    async def write(self, moderator_id, tools, values=None):

        if tools == 'del_moderator':
            query = """DELETE FROM moderators WHERE moderator_id = $1;"""
            async with self.pool.acquire():
                await self.pool.execute(query, moderator_id)
            self.moderators.pop(moderator_id)

        elif tools == 'add_moderator':
            query = """INSERT INTO moderators (moderator_id) VALUES ($1) ON CONFLICT (moderator_id) DO NOTHING;"""
            async with self.pool.acquire():
                await self.pool.execute(query, moderator_id)
            if values:
                query = f"""UPDATE moderators SET user_name = '{values}' WHERE moderator_id = '{moderator_id}';"""
                async with self.pool.acquire():
                    await self.pool.execute(query)
            await self.read(moderator_id)

        else:
            for i in range(len(tools)):
                if values[i] in ("NONE", "None", "none", "NULL", "null", "Null", None, ''):
                    query = f"""UPDATE moderators SET {tools[i]} = NULL WHERE moderator_id = '{moderator_id}';"""
                else:
                    query = f"""UPDATE moderators SET {tools[i]} = '{values[i]}' WHERE moderator_id = '{moderator_id}';"""
                async with self.pool.acquire():
                    await self.pool.execute(query)

            await self.read(moderator_id)

    #
    # __________DELETE TABLE__________
    async def dell(self):

        query = 'DROP TABLE public.moderators;'
        async with self.pool.acquire(): await self.pool.execute(query)

    async def format_tools_from_db(self, tools: str):
        if tools and ',' in tools:
            tools_list = tools.split(',')
            new_list_groups = []
            for tool in tools_list:
                tool = tool.strip()
                if tool:
                    new_list_groups.append(tool)
            tools = ",".join(new_list_groups)
        return tools

    async def list_all_moderators(self):
        moders_list = []
        for moder in self.moderators:
            moders_list.append(self.moderators[moder].user_name)
        num = len(moders_list)
        moders_list.sort(key=str.lower)
        moders = "\n".join(moders_list)
        return f'Всего {num} модераторов:\n{moders}'

    async def check_access_moderator(self, moder_id, option='any', tool='None'):
        moder_id = int(moder_id)
        if moder_id in ADMINS:
            return True
        access = False
        if moder_id not in self.moderators:
            return False

        if option == 'any':
            options = ['access_to_buttons_tools', 'access_to_files_tools', 'access_to_groups_tools',
                       'access_to_users_tools', 'access_to_state_tools']
            for opt in options:
                access = getattr(self.moderators[moder_id], opt, None)
                if access:
                    return True
            return False

        if isinstance(option, list):
            for opt in option:
                access = getattr(self.moderators[moder_id], opt, None)
                if access:
                    return True
            return False

        if option:
            access = getattr(self.moderators[moder_id], option, None)
        if not access:
            return False
        if access == 'all' or tool in access.split(',') or tool == 'any':
            return True
        return False

    async def get_all_from_bd(self):
        query = """SELECT * FROM moderators"""
        async with self.pool.acquire():
            res = await self.pool.fetch(query)
        return [dict(row) for row in res]


moderators_db = ModeratorsDatabase()
