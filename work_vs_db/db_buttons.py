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
    shablon_file: str = None
    active: int = 1
    sort: int = 1


class ButtonsDatabase:
    pool: asyncpg.Pool
    buttons_names: list
    buttons_groups: list
    buttons: dict

    #
    # __________CREATE__________
    async def create(self, pool: asyncpg.Pool):
        if pool: self.pool = pool
        # await self.dell()
        query = """CREATE TABLE IF NOT EXISTS public.buttons
                (
                    name varchar(30) COLLATE pg_catalog."default" NOT NULL,
                    group_buttons varchar DEFAULT 'a',
                    work_file varchar DEFAULT NULL,
                    num_block smallint NOT NULL DEFAULT 1,
                    size_blok smallint NOT NULL DEFAULT 3,
                    shablon_file varchar DEFAULT NULL,
                    active smallint NOT NULL DEFAULT 1,
                    sort smallint NOT NULL DEFAULT 1,
                    CONSTRAINT buttons_pkey PRIMARY KEY (name)
                );
                    """
        async with self.pool.acquire():
            await self.pool.execute(query)

        buttons_names = await self.read('get_names_buttons', '')
        if not buttons_names:
            buttons_names = f_db.files_names
            query = """INSERT INTO buttons (name, work_file) VALUES ($1, $2) ON CONFLICT (name) DO NOTHING;"""
            for butt in buttons_names:
                butt = butt.strip()
                async with self.pool.acquire(): await self.pool.execute(query, butt, butt+'.txt')
            buttons_names = await self.read('get_names_buttons', '')

        self.buttons = {i: await self.read('', i) for i in buttons_names}
        self.buttons_names = buttons_names
        self.buttons_groups = await self.read('get_names_groups', '')

    #
    # __________READ__________
    async def read(self, command: str, button_name: str):

        if command == 'get_names_buttons':
            query = """SELECT name FROM buttons WHERE active = 1 ORDER BY sort ASC ;"""
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
                if i not in buttons_groups:
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
                            shablon_file=butt['shablon_file'],
                            active=butt['active'],
                            sort=butt['sort']
                            )
            return button

    #
    # __________WRITE__________
    async def write(self, button_name: str, command, values):

        if command == 'add_button':
            query = """INSERT INTO buttons (name) VALUES ($1) ON CONFLICT (name) DO NOTHING;"""
            async with self.pool.acquire(): await self.pool.execute(query, button_name)
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

        else:
            columns = command
            # ['name', 'group_buttons', 'work_file', 'num_block', 'size_blok', 'shablon_file', 'active']

            for i in range(len(columns)):
                query = f"""UPDATE buttons SET {columns[i]} = {values[i]} WHERE name = $1;"""
                async with self.pool.acquire(): await self.pool.execute(query, button_name)

            button = await self.read('', button_name)
            self.buttons.update({button_name: button})

    #
    # __________DELETE TABLE__________
    async def dell(self):

        query = 'DROP TABLE public.buttons;'
        async with self.pool.acquire(): await self.pool.execute(query)


buttons_db = ButtonsDatabase()