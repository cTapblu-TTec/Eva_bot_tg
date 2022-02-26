import asyncpg


class User:
    # user_name: str
    # user_id: int
    n_zamen: int
    n_last_otm: tuple
    n_last_shabl: tuple
    # status: str


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
                        user_id integer,
                        n_zamen integer DEFAULT 0,
                        n_last_otm varchar,
                        n_last_shabl varchar,
                        status VARCHAR COLLATE pg_catalog."default" DEFAULT 'user',
                        CONSTRAINT "Users_pkey" PRIMARY KEY (user_name)
                    ); """

        async with self.pool.acquire(): await self.pool.execute(query)

        u = await self.read('get_names_users', '')
        if not u:
            f = open('users.txt', 'r')
            u = f.readlines()
            f.close()
            query = """ INSERT INTO users (user_name) VALUES ($1) ON CONFLICT (user_name) DO NOTHING;"""
            for user in u:
                user = user.rstrip('\n')
                async with self.pool.acquire(): await self.pool.execute(query, user)
            u = await self.read('get_names_users', '')
        self.users_names = u
        self.users = {i: await users_db.read('n_zamen, n_last_otm, n_last_shabl', i) for i in self.users_names}
        # for i in self.users:
        #     print(self.users[i].n_last_shabl)

    # __________READ__________
    async def read(self, command: str, user_name: str):

        if command == 'get_names_users':
            query = """SELECT user_name FROM users;"""
            async with self.pool.acquire(): u = await self.pool.fetch(query)
            users_names = []
            for i in u:
                users_names.append(i['user_name'])
            return users_names

        else:
            # 'user_name, user_id, n_zamen, n_last_otm, n_last_shabl, status'
            query = f'SELECT {command} FROM users WHERE user_name = $1;'
            async with self.pool.acquire(): u = await self.pool.fetch(query, user_name)
            user = User()
            user.user_name = user_name
            if 'n_zamen' in command:
                user.n_zamen = u[0]['n_zamen']
            if 'n_last_otm' in command:
                if u[0]['n_last_otm']: user.n_last_otm = u[0]['n_last_otm']
                else: user.n_last_otm = ()
            if 'n_last_shabl' in command:
                if u[0]['n_last_shabl']: user.n_last_shabl = u[0]['n_last_shabl']
                else: user.n_last_shabl = ()
            return user

    # __________WRITE__________
    async def write(self, user_name, command, USER):

        if command == 'add_user':
            query = """ INSERT INTO users (user_name) VALUES ($1) ON CONFLICT (user_name) DO NOTHING;"""
            async with self.pool.acquire(): await self.pool.execute(query, user_name)
            self.users_names.append(user_name)

        elif command == 'dell_user':
            query = 'DELETE FROM users WHERE user_name = $1;'
            async with self.pool.acquire(): await self.pool.execute(query, user_name)
            self.users_names.remove(user_name)

        # await users_db.write('Princ', ['n_zamen', 'n_last_otm', 'n_last_shabl'], [345, 3, (43,45)])
        else:
            stolbec = command  # ['user_id', 'n_zamen', 'n_last_otm', 'n_last_shabl']
            stolbcov = len(command)

            for i in range(stolbcov):
                query = f"""UPDATE users SET {stolbec[i]} = {USER[i]} WHERE user_name = $1;"""
                async with self.pool.acquire(): await self.pool.execute(query, user_name)
                if stolbec[i] == 'n_zamen': self.users[user_name].n_zamen = USER[i]
                if stolbec[i] == 'n_last_otm': self.users[user_name].n_last_otm = USER[i]
                if stolbec[i] == 'n_last_shabl': self.users[user_name].n_last_shabl = USER[i]
            # print(self.users[user_name].n_zamen, self.users[user_name].n_last_otm, self.users[user_name].n_last_shabl)


users_db = UsersDatabase()
