import asyncpg
from dataclasses import dataclass


@dataclass()
class User:
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
    users_names: list
    users: dict

    # __________CREATE__________
    async def create(self, pool: asyncpg.Pool):
        self.pool = pool
        query = """CREATE TABLE IF NOT EXISTS public.users
                    (
                        user_name character varying(30) COLLATE pg_catalog."default" NOT NULL,
                        user_stat_name varchar,
                        user_id integer,
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
        self.users_names = names
        self.users = {name: await self.read('', name) for name in names}

    #
    # __________READ__________
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
            user = None
            if u:
                u = u[0]
                user = User(
                    user_id=u['user_id'],
                    user_stat_name=u['user_stat_name'],
                    n_zamen=u['n_zamen'],
                    n_last_shabl=u['n_last_shabl'],
                    menu=u['menu'],
                    last_button=u['last_button'],
                    use_many_blocks=u['use_many_blocks'],
                    menu_mess_id=u['menu_mess_id']
                )
            return user

    #
    # __________WRITE__________
    async def write(self, user_name, command, values):

        if command == 'add_user':
            query = """INSERT INTO users (user_name) VALUES ($1) ON CONFLICT (user_name) DO NOTHING;"""
            async with self.pool.acquire():
                await self.pool.execute(query, user_name)
            self.users_names.append(user_name)
            user = await self.read('', user_name)
            self.users.update({user_name: user})

        elif command == 'dell_user':
            query = """DELETE FROM users WHERE user_name = $1;"""
            async with self.pool.acquire():
                await self.pool.execute(query, user_name)
            self.users_names.remove(user_name)

        else:
            columns = command  # ['user_id', 'n_zamen', 'n_last_otm', 'n_last_shabl']

            for i in range(len(columns)):
                if values[i] in ("NONE", "None", "none", "NULL", "null", "Null", None, ''):
                    query = f"""UPDATE users SET {columns[i]} = NULL WHERE user_name = $1;"""

                else:
                    if isinstance(values[i], str):
                        values[i] = "'" + values[i] + "'"
                    query = f"""UPDATE users SET {columns[i]} = {values[i]} WHERE user_name = $1;"""
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


users_db = UsersDatabase()
