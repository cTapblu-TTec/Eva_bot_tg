import asyncpg
from dataclasses import dataclass

from utils.log import log
from work_vs_db.db_filess import f_db


@dataclass()
class Button:
    name: str
    num_button: str
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
    statistical: int = 1


class ButtonsDatabase:
    pool: asyncpg.Pool
    buttons_groups: list
    buttons: dict
    numbers: int = 0
    button_numbers = {}

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
                    num_block smallint DEFAULT NULL,
                    size_blok smallint NOT NULL DEFAULT 3, CHECK (size_blok >= 0 AND size_blok <= 20),
                    name_block varchar(30) DEFAULT NULL,
                    shablon_file varchar(30) DEFAULT NULL,
                    active smallint NOT NULL DEFAULT 1, CHECK (active >= 0 AND active <= 1),
                    sort smallint NOT NULL DEFAULT 1,
                    hidden smallint NOT NULL DEFAULT 0, CHECK (hidden >= 0 AND hidden <= 1),
                    users varchar DEFAULT NULL,
                    specification varchar DEFAULT 'Описание кнопки',
                    statistical smallint NOT NULL DEFAULT 1, CHECK (statistical >= 0 AND statistical <= 1),
                    CONSTRAINT buttons_pkey PRIMARY KEY (name)
                );
                    """
        async with self.pool.acquire():
            await self.pool.execute(query)

        buttons_names = await self.read('get_names_buttons', '')
        if not buttons_names:
            await self.write('Кнопка', 'add_button')
            buttons_names = await self.read('get_names_buttons', '')

        self.buttons = {butt: await self.read('', butt) for butt in buttons_names}
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
                if i['group_buttons']:
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
                    group_buttons=await self.get_groups_from_db(butt['group_buttons']),
                    work_file=butt['work_file'],
                    num_block=butt['num_block'],
                    size_blok=butt['size_blok'],
                    name_block=butt['name_block'],
                    shablon_file=butt['shablon_file'],
                    active=butt['active'],
                    sort=butt['sort'],
                    hidden=butt['hidden'],
                    users=butt['users'],
                    specification=butt['specification'],
                    statistical=butt['statistical'],
                    num_button=await self.get_num_butt(button_name)
                )
                if butt['work_file'] and butt['work_file'] not in f_db.files:
                    await log.write(f"Файла {butt['work_file']} из кнопки '{button_name}' нет в боте", 'admin')
                if butt['shablon_file'] and butt['shablon_file'] not in f_db.files:
                    await log.write(f"Файла {butt['shablon_file']} из кнопки '{button_name}' нет в боте", 'admin')
            return button

    #
    # __________WRITE__________
    async def write(self, button_name: str, command, values=None):

        if command == 'add_button':
            query = """INSERT INTO buttons (name) VALUES ($1) ON CONFLICT (name) DO NOTHING;"""
            async with self.pool.acquire():
                await self.pool.execute(query, button_name)

            button = await self.read('', button_name)
            self.buttons.update({button_name: button})

        elif command == 'dell_button':
            query = """DELETE FROM buttons WHERE name = $1;"""
            async with self.pool.acquire():
                await self.pool.execute(query, button_name)
            self.buttons.pop(button_name)

        elif command == 'n_block':
            query = """UPDATE buttons SET num_block = $2 WHERE name = $1;"""
            async with self.pool.acquire():
                await self.pool.execute(query, button_name, values)

        else:
            columns = command
            # ['name', 'group_buttons', 'work_file', 'num_block', 'size_blok', 'shablon_file', 'active']

            for i in range(len(columns)):
                if values[i] in ("NONE", "None", "none", "NULL", "null", "Null", None, ''):
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

    async def get_num_butt(self, button_name):
        def get_num_by_name_button(butt_name):
            for number in self.button_numbers.keys():
                if self.button_numbers[number] == butt_name:
                    return number

        if button_name not in self.button_numbers.values():
            self.numbers += 1
            num = 'b' + str(self.numbers)
            self.button_numbers[num] = button_name
        else:
            num = get_num_by_name_button(button_name)
        return num

    async def delete_group_from_buttons(self, group_name: str):
        for button in self.buttons:
            if self.buttons[button].group_buttons and group_name in self.buttons[button].group_buttons:
                old_groups_list = self.buttons[button].group_buttons.split(',')
                old_groups_list.remove(group_name)
                new_group = ",".join(old_groups_list)
                await self.write(button, ["group_buttons"], [new_group])
        self.buttons_groups.remove(group_name)

    async def get_groups_from_db(self, groups: str):
        if groups and ',' in groups:
            groups_list = groups.split(',')
            new_list_groups = []
            for group in groups_list:
                group = group.strip()
                if group:
                    new_list_groups.append(group)
            groups = ",".join(new_list_groups)
        return groups

    async def reset_buttons_num_blocks(self):
        for button in self.buttons:
            if self.buttons[button].num_block:
                await self.write(button, 'n_block', 1)
                self.buttons[button].num_block = 1

    async def change_value_for_all_buttons(self, tool, old_value, new_value):
        for button in self.buttons:
            value_butt = getattr(buttons_db.buttons[button], tool, None)
            if value_butt and old_value in value_butt:
                new_butt_value = value_butt.replace(old_value, new_value)
                await self.write(button, [tool], [new_butt_value])
                await log.write(f"Значение '{new_butt_value}' параметра '{tool}' для кнопки '{button}'"
                                f" установлено", 'admin')


buttons_db = ButtonsDatabase()
