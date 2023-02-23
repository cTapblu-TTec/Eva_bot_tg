import asyncpg
from datetime import datetime
from pytz import timezone

from work_vs_db.db_users import users_db


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

    # ______GET personal______
    async def get_personal_stat(self, user_name):
        query = 'SELECT * FROM statistic WHERE user_name = $1;'
        async with self.pool.acquire():
            stat = await self.pool.fetch(query, user_name)
            result = ''
            if stat:
                for i in stat[0].keys():
                    if isinstance(stat[0][i],int) and stat[0][i] > 0:
                        result += f'\n{i} - {stat[0][i]}'
        return result

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
            for column in stat[0].keys():
                columns += '<th>' + column + '</th>'
            columns += '</tr>'

        statistic = {}
        for user in stat:
            user_name = user['user_name']
            if users_db.users[user_name].user_stat_name:
                user_stat_name = users_db.users[user_name].user_stat_name
            else:
                user_stat_name = user_name
            user_stat = list(user)[1:]
            if not statistic.get(user_stat_name):
                statistic[user_stat_name] = user_stat
            else:
                i = 0
                for clics in statistic[user_stat_name]:
                    user_stat[i] += clics
                    i += 1
                statistic[user_stat_name] = user_stat
        sort_stat = {}
        for user in statistic:
            sort_stat[user] = sum(statistic[user])
        sort_stat = dict(sorted(sort_stat.items(),key=lambda item: item[1],reverse=True))
        table = ''
        for user in sort_stat:
            table += '\n\t\t\t<tr>'
            table += '<td>' + user + '</td>'
            for clics in statistic[user]:
                table += '<td>' + str(clics) + '</td>'
            table += '</tr>'
        close = """
            </table>
        </body>
        </html>"""

        text = head + columns + table + close

        with open('statistic.html', 'w', encoding='utf-8') as file:
            file.write(text)

    # ______WRITE______
    #   ведение statistic
    async def write(self, button_name, user_name: str, blocks: int):

        button_name = button_name.replace(' ', '_')

        # ДОБАВЛЕНИЕ в БД пользователя
        if self.users_st == [] or user_name not in self.users_st:
            query = """INSERT INTO statistic (user_name) VALUES ($1) ON CONFLICT (user_name) DO NOTHING;"""
            async with self.pool.acquire(): await self.pool.execute(query, user_name)
            self.users_st.append(user_name)

        # ДОБВЛЕНИЕ СТОЛБЦА
        if button_name not in self.columns:
            query = f"""ALTER TABLE public.statistic ADD COLUMN IF NOT EXISTS {button_name} smallint DEFAULT 0;"""

            async with self.pool.acquire(): await self.pool.execute(query)
            self.columns.append(button_name)

        # ОБНОВЛЕНИЕ статистики пользователя
        query = f"""UPDATE statistic SET {button_name} = {button_name} + {blocks} WHERE user_name = $1;"""
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
