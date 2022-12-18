import asyncpg
from dataclasses import dataclass

from work_vs_db.db_filess import f_db


@dataclass()
class Button:
    name: str
    group_buttons: str = 'a'
    work_file: str = None
    num_block: int = 1
    size_blok: int = 3
    name_block: str = None
    shablon_file: str = None
    active: int = 1
    sort: int = 1
    hidden: int = 0
    users: str = None  # список допущенных
    specification: str = 'Описание кнопки'


class ButtonsDatabase:
    pool: asyncpg.Pool
    buttons_names: list
    buttons_groups: list
    buttons: dict

    async def init(self, pool):
        self.pool = pool
        await self.create()

    # __________CREATE__________
    async def create(self):
        # await self.dell()
        query = """CREATE TABLE IF NOT EXISTS public.buttons
                (
                    name varchar(30) COLLATE pg_catalog."default" NOT NULL,
                    group_buttons varchar DEFAULT 'a',
                    work_file varchar DEFAULT NULL,
                    num_block smallint NOT NULL DEFAULT 1,
                    size_blok smallint NOT NULL DEFAULT 3, CHECK (size_blok >= 0 AND size_blok <= 20),
                    name_block varchar(30) DEFAULT NULL,
                    shablon_file varchar(30) DEFAULT NULL,
                    active smallint NOT NULL DEFAULT 1, CHECK (active >= 0 AND active <= 1),
                    sort smallint NOT NULL DEFAULT 1,
                    hidden smallint NOT NULL DEFAULT 0, CHECK (hidden >= 0 AND hidden <= 1),
                    users varchar DEFAULT NULL,
                    specification varchar DEFAULT 'Описание кнопки',
                    CONSTRAINT buttons_pkey PRIMARY KEY (name)
                );
                    """
        async with self.pool.acquire():
            await self.pool.execute(query)

        query = """
                ALTER TABLE public.buttons ADD COLUMN IF NOT EXISTS specification varchar DEFAULT 'Описание кнопки';
                ALTER TABLE public.buttons ADD CHECK (size_blok >= 0 AND size_blok <= 20);
                ALTER TABLE public.buttons ADD CHECK (active >= 0 AND active <= 1);
                ALTER TABLE public.buttons ADD CHECK (hidden >= 0 AND hidden <= 1);
               """
        # async with self.pool.acquire(): await self.pool.execute(query)

        buttons_names = await self.read('get_names_buttons', '')
        if not buttons_names:
            buttons_names = f_db.files_names
            query = """INSERT INTO buttons (name, work_file) VALUES ($1, $2) ON CONFLICT (name) DO NOTHING;"""
            for butt in buttons_names:
                butt = butt.strip()
                async with self.pool.acquire(): await self.pool.execute(query, butt, butt + '.txt')
            buttons_names = await self.read('get_names_buttons', '')

        self.buttons = {i: await self.read('', i) for i in buttons_names}
        self.buttons_names = buttons_names
        self.buttons_groups = await self.read('get_names_groups', '')

    #
    # __________READ__________
    async def read(self, command: str, button_name: str):

        if command == 'get_names_buttons':
            query = """SELECT name FROM buttons ORDER BY sort ASC ;"""
            async with self.pool.acquire():
                butt_names = await self.pool.fetch(query)
            buttons_names = []
            for i in butt_names:
                buttons_names.append(i['name'])
            return buttons_names

        if command == 'get_names_groups':
            query = """SELECT group_buttons FROM buttons WHERE active = 1;"""
            async with self.pool.acquire():
                group_names = await self.pool.fetch(query)
            buttons_groups = []
            for i in group_names:
                if i['group_buttons'] not in buttons_groups:
                    if ',' in i['group_buttons']:
                        list_grups = i['group_buttons']
                        list_grups = list_grups.replace(' ', '')
                        list_grups = list_grups.split(',')
                        for grup in list_grups:
                            if grup not in buttons_groups:
                                buttons_groups.append(grup)
                    else:
                        buttons_groups.append(i['group_buttons'])
            return buttons_groups

        else:
            # 'name, work_file, num_block, size_blok, shablon_file, active'
            query = """SELECT * FROM buttons WHERE name = $1 ORDER BY sort ASC ;"""
            async with self.pool.acquire():
                butt = await self.pool.fetch(query, button_name)
            button = None
            if butt:
                butt = butt[0]
                button = Button(
                    name=button_name,
                    group_buttons=butt['group_buttons'],
                    work_file=butt['work_file'],
                    num_block=butt['num_block'],
                    size_blok=butt['size_blok'],
                    name_block=butt['name_block'],
                    shablon_file=butt['shablon_file'],
                    active=butt['active'],
                    sort=butt['sort'],
                    hidden=butt['hidden'],
                    users=butt['users'],
                    specification=butt['specification']
                )
            return button

    #
    # __________WRITE__________
    async def write(self, button_name: str, command, values):

        if command == 'add_button':
            query = """INSERT INTO buttons (name) VALUES ($1) ON CONFLICT (name) DO NOTHING;"""
            async with self.pool.acquire():
                await self.pool.execute(query, button_name)
            self.buttons_names.append(button_name)
            query = """UPDATE buttons SET active = 1 WHERE name = $1;"""
            async with self.pool.acquire():
                await self.pool.execute(query, button_name)

            button = await self.read('', button_name)
            self.buttons.update({button_name: button})

        elif command == 'dell_button':
            query = """UPDATE buttons SET active = 0 WHERE name = $1;"""
            async with self.pool.acquire():
                await self.pool.execute(query, button_name)
            self.buttons_names.remove(button_name)
            self.buttons.pop(button_name)

        elif command == 'n_block':
            query = """UPDATE buttons SET num_block = $2 WHERE name = $1;"""
            async with self.pool.acquire():
                await self.pool.execute(query, button_name, values)

        else:
            columns = command
            # ['name', 'group_buttons', 'work_file', 'num_block', 'size_blok', 'shablon_file', 'active']

            for i in range(len(columns)):
                if values[i] in ("NONE", "None", "none", "NULL", "null", "Null"):
                    query = f"""UPDATE buttons SET {columns[i]} = NULL WHERE name = $1;"""
                else:
                    query = f"""UPDATE buttons SET {columns[i]} = '{values[i]}' WHERE name = $1;"""
                async with self.pool.acquire():
                    await self.pool.execute(query, button_name)

            button = await self.read('', button_name)
            self.buttons.update({button_name: button})

    #
    # __________DELETE TABLE__________
    async def dell(self):

        query = 'DROP TABLE public.buttons;'
        async with self.pool.acquire(): await self.pool.execute(query)


buttons_db = ButtonsDatabase()
