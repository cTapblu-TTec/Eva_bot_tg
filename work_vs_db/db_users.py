import asyncpg
from dataclasses import dataclass


@dataclass()
class User:
    user_name:  str
    user_stat_name: str
    user_id: int
    n_zamen: int
    n_last_shabl: tuple
    menu: str
    last_button: str
    use_many_blocks: int
    menu_mess_id: int


class UsersDatabase:
    pool: asyncpg.Pool
    users_names: list = []
    users_id_names: dict = {}
    users: dict = {}

    # __________CREATE__________
    async def create(self, pool: asyncpg.Pool):
        self.pool = pool
        query = """CREATE TABLE IF NOT EXISTS public.users
                    (
                        user_name character varying(30) COLLATE pg_catalog."default" NOT NULL,
                        user_stat_name varchar,
                        user_id bigint,
                        n_zamen integer DEFAULT 0,
                        n_last_shabl varchar,
                        menu varchar,
                        last_button varchar,
                        menu_mess_id integer,
                        use_many_blocks smallint DEFAULT 1, CHECK (use_many_blocks >= 0 AND use_many_blocks <= 1),
                        CONSTRAINT "Users_pkey" PRIMARY KEY (user_name)
                    ); """
        async with self.pool.acquire():
            await self.pool.execute(query)
        # ALTER TABLE public.users ADD COLUMN IF NOT EXISTS blocks smallint NOT NULL DEFAULT 1;
        # ALTER TABLE IF EXISTS public.users DROP CONSTRAINT users_blocks_check;
        # ALTER TABLE public.users DROP COLUMN blocks;
        # ALTER TABLE public.users ADD CHECK (blocks >= 0 AND blocks <= 1);
        # query = """"""
        # async with self.pool.acquire(): await self.pool.execute(query)

        names = await self.read('get_names_users', '')
        if not names:
            with open('users.txt', 'r', encoding='utf-8') as f:
                names = f.readlines()
            query = """INSERT INTO users (user_name) VALUES ($1) ON CONFLICT (user_name) DO NOTHING;"""
            for user in names:
                user = user.rstrip('\n')
                async with self.pool.acquire(): await self.pool.execute(query, user)
            names = await self.read('get_names_users', '')
        for name in names:
            await self.read('', name)

    #
    # __________READ__________ todo мб разделить на две функции
    async def read(self, command: str, user_name: str):

        if command == 'get_names_users':
            query = """SELECT user_name FROM users;"""
            async with self.pool.acquire():
                u = await self.pool.fetch(query)
            users_names = []
            for i in u:
                users_names.append(i['user_name'])
            return users_names

        else:
            # 'user_name, user_id, n_zamen, n_last_otm, n_last_shabl, status'
            query = f"""SELECT * FROM users WHERE user_name = $1;"""
            async with self.pool.acquire():
                u = await self.pool.fetch(query, user_name)
            if u:
                u = u[0]
                user = User(
                    user_name=u['user_name'],
                    user_id=u['user_id'],
                    user_stat_name=u['user_stat_name'],
                    n_zamen=u['n_zamen'],
                    n_last_shabl=u['n_last_shabl'],
                    menu=u['menu'],
                    last_button=u['last_button'],
                    use_many_blocks=u['use_many_blocks'],
                    menu_mess_id=u['menu_mess_id']
                )
                self.users.update({user_name: user})
                if user.user_id:
                    self.users_id_names.update({user.user_id: user_name})
                if user_name not in self.users_names:
                    self.users_names.append(user_name)

    #
    # __________WRITE__________
    async def write(self, user_name, command, values):

        if command == 'add_user':
            query = """INSERT INTO users (user_name) VALUES ($1) ON CONFLICT (user_name) DO NOTHING;"""
            async with self.pool.acquire():
                await self.pool.execute(query, user_name)
            await self.read('', user_name)

        elif command == 'dell_user':
            query = """DELETE FROM users WHERE user_name = $1;"""
            async with self.pool.acquire():
                await self.pool.execute(query, user_name)
            if self.users[user_name].user_id in self.users_id_names:
                self.users_id_names.pop(self.users[user_name].user_id)
            self.users_names.remove(user_name)
            self.users.pop(user_name)

        else:
            tools = command  # ['user_id', 'n_zamen', 'n_last_otm', 'n_last_shabl']

            for i in range(len(tools)):
                if values[i] in ("NONE", "None", "none", "NULL", "null", "Null", None, ''):
                    query = f"""UPDATE users SET {tools[i]} = NULL WHERE user_name = $1;"""
                else:
                    if isinstance(values[i], str):
                        values[i] = "'" + values[i] + "'"
                    query = f"""UPDATE users SET {tools[i]} = {values[i]} WHERE user_name = $1;"""
                async with self.pool.acquire():
                    await self.pool.execute(query, user_name)

    async def del_user(self, user):
        all_users = self.users_names
        user = user.strip()
        user = user.lstrip('@')
        if user in all_users:
            await self.write(user, 'dell_user', None)
            return f"Пользователь удален - {user}"
        else:
            return f"Пользователь не найден - {user}"

    async def add_user(self, new_user):
        all_users = self.users_names
        new_user = new_user.strip()
        new_user = new_user.lstrip('@')
        iskl = ' !"$%&()*+,/:;<>=?@^#{}|~'
        begin = True
        for i in iskl:
            if i in new_user:
                begin = False
        if new_user == '':
            begin = False
        if new_user.isascii() and begin:
            if new_user in all_users:
                return f"Пользователь {new_user} уже был в списке"
            await self.write(new_user, 'add_user', None)
            return f"Добавлен пользователь - {new_user}"

        else:
            return f"Неверный формат - {new_user}"

    async def change_last_group_for_all_users(self, old_group, new_group):
        for user in self.users:
            if self.users[user].menu == old_group:
                await self.write(user, ['menu'], [new_group])
                self.users[user].menu = new_group

    async def get_all_from_bd(self):
        query = """SELECT * FROM users"""
        async with self.pool.acquire():
            all = await self.pool.fetch(query)
        all_users = [dict(row) for row in all]
        return all_users


users_db = UsersDatabase()
