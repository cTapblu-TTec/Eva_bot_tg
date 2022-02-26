import asyncpg


class StatDatabase:
    pool: asyncpg.Pool
    users_st: list  # users_st - список имен юзеров в статистике

    # ______CREATE______
    async def create(self, pool: asyncpg.Pool):
        self.pool = pool

        query = """CREATE TABLE IF NOT EXISTS public.statistic
                (
                    user_name character varying(30) COLLATE pg_catalog."default" NOT NULL,
                    shablon smallint DEFAULT 0,
                    vk smallint DEFAULT 0,
                    storis smallint DEFAULT 0,
                    vk_otm smallint DEFAULT 0,
                    otmetki smallint DEFAULT 0,
                    other smallint DEFAULT 0,
                    visit smallint DEFAULT 0,
                    CONSTRAINT "Statistic_pkey" PRIMARY KEY (user_name)
                ); """
        async with self.pool.acquire(): await self.pool.execute(query)

        query = """SELECT user_name FROM statistic;"""
        async with self.pool.acquire(): u = await self.pool.fetch(query)
        self.users_st = []
        for i in u:
            self.users_st.append(i[0])
        #print(self.users_st)

    # ______GET______
    async def get(self):
        query = 'SELECT * FROM statistic;'
        async with self.pool.acquire(): ST =  await self.pool.fetch(query)

        text = 'User\t'.expandtabs(tabsize=20) + 'shablon\tvk\tstoris\tvk_otm\totmetki\tДругое\tВсего\n'.expandtabs(
            tabsize=10)

        for i in ST:
            i = list(i)
            k = i.pop(0)
            t = ''
            for j in i:
                t = t + '\t' + str(j)
            text = text + (str(k) + '\t').expandtabs(tabsize=20) + t.lstrip('\t').expandtabs(tabsize=10) + '\n'

        file = open('statistic.txt', 'w')
        file.write(text)
        file.close()

    # ______WRITE______
    #   ведение statistic
    async def write(self, command: str, user_name: str):

        stolbec = command  # 'shablon', 'vk', 'storis', 'vk_otm', 'otmetki', 'other' , 'visit'

        # ДОБАВЛЕНИЕ в БД пользователя
        if self.users_st == [] or user_name not in self.users_st:
            query = """INSERT INTO statistic (user_name) VALUES ($1) ON CONFLICT (user_name) DO NOTHING;"""
            async with self.pool.acquire(): await self.pool.execute(query, user_name)
            self.users_st.append(user_name)

        # ОБНОВЛЕНИЕ статистики пользователя
        query = f'UPDATE statistic SET {stolbec} = {stolbec} + 1, visit = visit + 1 WHERE user_name = $1;'
        async with self.pool.acquire(): await self.pool.execute(query, user_name)

    # ______CLEAR______
    async def clear(self):
        query = 'DELETE FROM statistic *'
        async with self.pool.acquire(): await self.pool.execute(query)
        self.users_st = []


stat_db = StatDatabase()
