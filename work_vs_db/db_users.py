import asyncpg
from dataclasses import dataclass


@dataclass()
class User:
    user_stat_name: str
    # user_id: int
    n_zamen: int
    n_last_shabl: tuple
    # status: str - хочу добавить кураторов
    menu: str
    last_button: str
    blocks: int


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
                        user_stat_name varchar DEFAULT NULL,
                        user_id integer,
                        n_zamen integer DEFAULT 0,
                        n_last_shabl varchar,
                        menu varchar DEFAULT NULL,
                        last_button varchar DEFAULT NULL,
                        status VARCHAR COLLATE pg_catalog."default" DEFAULT 'user',
                        blocks smallint NOT NULL DEFAULT 1, CHECK (blocks >= 1 AND blocks <= 10),
                        CONSTRAINT "Users_pkey" PRIMARY KEY (user_name)
                    ); """
        async with self.pool.acquire():
            await self.pool.execute(query)

        query = """
                ALTER TABLE public.users ADD COLUMN IF NOT EXISTS blocks smallint NOT NULL DEFAULT 1;
                ALTER TABLE public.users ADD CHECK (blocks >= 1 AND blocks <= 10);
                ALTER TABLE public.users ADD COLUMN IF NOT EXISTS user_stat_name varchar DEFAULT NULL;
               """
        #  async with self.pool.acquire(): await self.pool.execute(query)

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
                    user_stat_name=u['user_stat_name'],
                    n_zamen=u['n_zamen'],
                    n_last_shabl=u['n_last_shabl'],
                    menu=u['menu'],
                    last_button=u['last_button'],
                    blocks=u['blocks']
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
                if values[i] in ("NONE", "None", "none", "NULL", "null", "Null", None):
                    query = f"""UPDATE users SET {columns[i]} = NULL WHERE user_name = $1;"""

                else:
                    if isinstance(values[i], str):
                        values[i] = "'" + values[i] + "'"
                    query = f"""UPDATE users SET {columns[i]} = {values[i]} WHERE user_name = $1;"""
                async with self.pool.acquire():
                    await self.pool.execute(query, user_name)


users_db = UsersDatabase()
