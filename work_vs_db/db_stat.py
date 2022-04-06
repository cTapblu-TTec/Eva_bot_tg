import asyncpg
from datetime import datetime
from pytz import timezone


class StatDatabase:
    columns: list = []  # список столбцов в статистике
    pool: asyncpg.Pool
    users_st: list  # users_st - список имен юзеров в статистике

    # vk_ludi.txt', 'vk_lotereya.txt', 'vk_gruppa.txt', 'vk_storis.txt
    # ______CREATE______
    async def create(self, pool: asyncpg.Pool):
        if pool: self.pool = pool

        # await self.dell()

        query = """CREATE TABLE IF NOT EXISTS public.statistic
                (
                    user_name character varying(30) COLLATE pg_catalog."default" NOT NULL,
                    CONSTRAINT "Statistic_pkey" PRIMARY KEY (user_name)
                ); """
        async with self.pool.acquire(): await self.pool.execute(query)

        query = """SELECT user_name FROM statistic;"""
        async with self.pool.acquire(): u = await self.pool.fetch(query)
        self.users_st = []
        for i in u:
            self.users_st.append(i[0])
        # print(self.users_st)

    # ______GET HTML______
    async def get_html(self):

        query = 'SELECT * FROM statistic;'
        async with self.pool.acquire():
            stat = await self.pool.fetch(query)
        dtime = datetime.now(tz=timezone('Europe/Moscow')).strftime('%d.%m.%Y %H:%M')
        head = """
        <!DOCTYPE HTML>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Статистика</title>
        </head>
        <style>
            table
                {border-collapse: collapse;
                width: 100%;
                background-color: White;}
            th
                {font-weight:normal;
                 background-color:  MediumVioletRed;
                 color: White;}
            th, td
                {border: 1px solid Teal; 
                padding: 2px;
                text-align: center; 
                width: 100px;}
            body
                {background-color: Teal;
                font: 100% monospace;
                font-style: normal;}
            caption
                {color: White;
                text-align: left;}
        </style>
        <body>
            <table>
            <colgroup>
                <col span="1" style="background:#FFFACD">
            </colgroup>
            <caption>""" + dtime + """</caption>"""

        columns = '\n\t\t\t<tr>'

        if stat:
            for i in stat[0].keys():
                columns += '<th>' + i + '</th>'
            columns += '</tr>'

        table = ''
        for i in stat:
            i = list(i)
            table += '\n\t\t\t<tr>'
            for j in i:
                table += '<td>' + str(j) + '</td>'
            table += '</tr>'
        close = """
            </table>
        </body>
        </html>"""

        text = head + columns + table + close

        file = open('statistic.html', 'w', encoding='utf-8')
        file.write(text)
        file.close()

    # ______WRITE______
    #   ведение statistic
    async def write(self, command: str, user_name: str):

        stolbec = command.replace(' ', '_')

        # ДОБАВЛЕНИЕ в БД пользователя
        if self.users_st == [] or user_name not in self.users_st:
            query = """INSERT INTO statistic (user_name) VALUES ($1) ON CONFLICT (user_name) DO NOTHING;"""
            async with self.pool.acquire(): await self.pool.execute(query, user_name)
            self.users_st.append(user_name)

        # ДОБВЛЕНИЕ СТОЛБЦА
        if stolbec not in self.columns:
            query = f"""ALTER TABLE public.statistic ADD COLUMN IF NOT EXISTS {stolbec} smallint DEFAULT 0;"""

            async with self.pool.acquire(): await self.pool.execute(query)
            self.columns.append(stolbec)

        # ОБНОВЛЕНИЕ статистики пользователя
        query = f"""UPDATE statistic SET {stolbec} = {stolbec} + 1 WHERE user_name = $1;"""
        async with self.pool.acquire(): await self.pool.execute(query, user_name)

    # ______CLEAR______
    async def clear(self):
        query = 'DELETE FROM statistic *'
        async with self.pool.acquire(): await self.pool.execute(query)
        self.users_st = []

    # __________DELETE TABLE__________
    async def dell(self):

        query = 'DROP TABLE IF EXISTS public.statistic'
        async with self.pool.acquire(): await self.pool.execute(query)
        self.columns = []
        self.users_st = []


stat_db = StatDatabase()
