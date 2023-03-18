import asyncpg
from dataclasses import dataclass


@dataclass()
class AdmChat:
    chat_id: int
    id_msg_settings: str
    id_msg_options: str
    id_msg_tools: str
    id_msg_values: str
    id_msg_system: str
    menu_back: bool
    menu_cancel: bool
    setting: str
    option: str
    tool: str
    value: str
    state: str


class AdmChatsDatabase:
    pool: asyncpg.Pool
    chats: dict = {}

    async def init(self, pool):
        self.pool = pool
        await self.create()

    # __________CREATE__________
    async def create(self):
        # await self.dell()
        query = """CREATE TABLE IF NOT EXISTS public.adm_chats
                (
                    chat_id integer NOT NULL,
                    id_msg_settings varchar(30) DEFAULT NULL,
                    id_msg_options varchar(30) DEFAULT NULL,
                    id_msg_tools varchar(30) DEFAULT NULL,
                    id_msg_values varchar(30) DEFAULT NULL,
                    id_msg_system varchar(30) DEFAULT NULL,
                    menu_back boolean DEFAULT false,
                    menu_cancel boolean DEFAULT false,
                    setting varchar(30) DEFAULT NULL,
                    option varchar(30) DEFAULT NULL,
                    tool varchar(30) DEFAULT NULL,
                    value varchar(30) DEFAULT NULL,
                    state varchar(30) DEFAULT NULL,
                    CONSTRAINT adm_chats_pkey PRIMARY KEY (chat_id)
                );
                    """
        async with self.pool.acquire():
            await self.pool.execute(query)

        for chat_id in await self.get_chats_id():
            await self.read(chat_id)

    #
    # __________READ__________
    async def get_chats_id(self):
        query = """SELECT chat_id FROM adm_chats;"""
        async with self.pool.acquire():
            chats_id = await self.pool.fetch(query)
        chats = []
        for i in chats_id:
            chats.append(i['chat_id'])
        return chats

    async def read(self, chat_id: int):
        query = """SELECT * FROM adm_chats WHERE chat_id = $1;"""
        async with self.pool.acquire():
            answer = await self.pool.fetch(query, chat_id)
        chat = None
        if answer:
            answer = answer[0]
            chat = AdmChat(
                chat_id=chat_id,
                id_msg_settings=answer['id_msg_settings'],
                id_msg_options=answer['id_msg_options'],
                id_msg_tools=answer['id_msg_tools'],
                id_msg_values=answer['id_msg_values'],
                id_msg_system=answer['id_msg_system'],
                menu_back=answer['menu_back'],
                menu_cancel=answer['menu_cancel'],
                setting=answer['setting'],
                option=answer['option'],
                tool=answer['tool'],
                value=answer['value'],
                state=answer['state']
            )
        self.chats.update({chat_id: chat})

    #
    # __________WRITE__________
    async def write(self, chat_id, tools, values):

        query = """INSERT INTO adm_chats (chat_id) VALUES ($1) ON CONFLICT (chat_id) DO NOTHING;"""
        async with self.pool.acquire():
            await self.pool.execute(query, chat_id)
        # print(query, chat_id)

        for i in range(len(tools)):
            if values[i] in ("NONE", "None", "none", "NULL", "null", "Null", None, ''):
                query = f"""UPDATE adm_chats SET {tools[i]} = NULL WHERE chat_id = '{chat_id}';"""
            else:
                query = f"""UPDATE adm_chats SET {tools[i]} = '{values[i]}' WHERE chat_id = '{chat_id}';"""
            async with self.pool.acquire():
                await self.pool.execute(query)
            # print(query, chat_id)

        await self.read(chat_id)

    #
    # __________DELETE TABLE__________
    async def dell(self):

        query = 'DROP TABLE public.adm_chats;'
        async with self.pool.acquire(): await self.pool.execute(query)

    async def get_all_from_bd(self):
        query = """SELECT * FROM adm_chats"""
        async with self.pool.acquire():
            res = await self.pool.fetch(query)
        return [dict(row) for row in res]


adm_chats_db = AdmChatsDatabase()
