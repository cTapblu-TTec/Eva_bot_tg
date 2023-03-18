import asyncpg

from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_users import users_db


class StatDatabase:
    columns: list = []  # список столбцов в статистике
    pool: asyncpg.Pool
    users_st: list  # - список имен юзеров в статистике

    # ______CREATE______
    async def create(self, pool: asyncpg.Pool):
        if pool: self.pool = pool
        query = """CREATE TABLE IF NOT EXISTS public.statistic
                (
                    user_name character varying(30) COLLATE pg_catalog."default" NOT NULL,
                    CONSTRAINT "Statistic_pkey" PRIMARY KEY (user_name)
                ); """
        async with self.pool.acquire(): await self.pool.execute(query)

        query = """SELECT user_name FROM statistic;"""
        async with self.pool.acquire():
            u = await self.pool.fetch(query)
        self.users_st = []
        for i in u:
            self.users_st.append(i[0])

    # ______GET personal______
    async def get_personal_stat(self, user_name):
        async def get_list_users_in_statistic():
            users = [user_name]
            if users_db.users[user_name].user_stat_name:
                user_stat_name = users_db.users[user_name].user_stat_name
            else:
                user_stat_name = user_name
            for us in users_db.users:
                if users_db.users[us].user_stat_name == user_stat_name and us not in users:
                    users.append(us)
            return users

        async def get_user_stat():
            query = 'SELECT * FROM "statistic" WHERE "user_name" = $1;'
            async with self.pool.acquire():
                stat = await self.pool.fetch(query, user)
            in_statistic = ''
            not_in_statistic = ''
            result = ''
            if stat:
                stat = stat[0]
                stat_l = {}
                for button in stat.keys():
                    if isinstance(stat[button], int):
                        stat_l[button] = stat[button]
                stat_l = dict(sorted(stat_l.items(), key=lambda item: item[1], reverse=True))
                for button in stat_l:
                    if stat_l[button] > 0:
                        text = f'\n• {button} - {stat_l[button]}'
                        butt = buttons_db.buttons.get(button)
                        if butt:
                            if butt.hidden == 0 and butt.statistical == 1:
                                in_statistic += text
                            else:
                                not_in_statistic += text
                        else:
                            in_statistic += text
                if in_statistic:
                    result += f'Идет в статистику:{in_statistic}\n'
                if not_in_statistic:
                    result += f'Не идет в статистику:{not_in_statistic}\n'
            return result

        user_stats = ''
        for user in await get_list_users_in_statistic():
            user_stats += f'\n    {user}\n{await get_user_stat()}'
        return user_stats

    # ______GET HTML______
    async def get_html(self, get_all=False, file_stat='statistic.html'):
        query = 'SELECT * FROM statistic;'
        async with self.pool.acquire():
            stat = await self.pool.fetch(query)

        head = await get_head()
        columns = '\n\t\t\t<tr>'
        table = ''
        if stat:
            statistic, buttons = await get_sort_stat(stat, get_all)
            columns += '<th>Имя</th>'
            for column in buttons:
                columns += f'<th> {column} ({buttons[column]}) </th>'
            columns += '</tr>'

            for user in statistic:
                table += '\n\t\t\t<tr>'
                table += '<td>' + user + '</td>'
                for butt in buttons:
                    if statistic[user].get(butt):
                        table += '<td>' + str(statistic[user][butt]) + '</td>'
                    else:
                        table += '<td>0</td>'
                table += '</tr>'
        close = """</table> </body> </html>"""

        text = head + columns + table + close

        with open(file_stat, 'w', encoding='utf-8') as file:
            file.write(text)

    # ______WRITE______
    #   ведение statistic
    # INSERT INTO distributors (did, dname)
    # VALUES (5, 'Gizmo Transglobal'), (6, 'Associated Computing, Inc')
    # ON CONFLICT (did) DO UPDATE SET dname = EXCLUDED.dname;
    async def write(self, button_name, user_name: str, blocks: int):

        # ДОБАВЛЕНИЕ в БД пользователя
        if self.users_st == [] or user_name not in self.users_st:
            query = """INSERT INTO "statistic" (user_name) VALUES ($1) ON CONFLICT (user_name) DO NOTHING;"""
            async with self.pool.acquire(): await self.pool.execute(query, user_name)
            self.users_st.append(user_name)

        # ДОБВЛЕНИЕ СТОЛБЦА
        if button_name not in self.columns:
            query = f"""ALTER TABLE public.statistic ADD COLUMN IF NOT EXISTS "{button_name}" smallint DEFAULT 0;"""

            async with self.pool.acquire(): await self.pool.execute(query)
            self.columns.append(button_name)

        # ОБНОВЛЕНИЕ статистики пользователя
        query = f"""UPDATE statistic SET "{button_name}" = "{button_name}" + {blocks} WHERE user_name = $1;"""
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


async def get_sort_stat(stat, get_all):
    stat = [dict(row) for row in stat]
    statistic = {}
    buttons = {}
    for st_user in stat:
        user_name = st_user['user_name']
        # имя пользователя
        if users_db.users[user_name].user_stat_name:
            user_stat_name = users_db.users[user_name].user_stat_name
        else:
            user_stat_name = user_name
        user_stat = {}
        for button in st_user:
            if button != 'user_name' and st_user[button] > 0:
                if button in buttons_db.buttons:
                    butt = buttons_db.buttons[button]
                    if (butt and butt.hidden == 0 and butt.statistical == 1) or get_all:
                        user_stat[button] = st_user[button]
                        if button not in buttons:
                            buttons[button] = st_user[button]
                        else:
                            buttons[button] += st_user[button]
                            # складывать значения для кнопки

        if not statistic.get(user_stat_name):
            statistic[user_stat_name] = user_stat
        else:  # складываем статистики пользователей с одинаковыми именами
            i = 0
            for button in statistic[user_stat_name]:
                if not user_stat.get(button):
                    user_stat[button] = 0
                user_stat[button] += statistic[user_stat_name][button]
                i += 1
            statistic[user_stat_name] = user_stat
    sort = {}
    for st_user in statistic:
        user_clicks = list(statistic[st_user].values())
        sort[st_user] = sum(user_clicks)
    sort = dict(sorted(sort.items(), key=lambda item: item[1], reverse=True))
    buttons = dict(sorted(buttons.items(), key=lambda item: item[1], reverse=True))
    sort_stat = {}
    for st_user in sort:
        if sort[st_user] > 0:
            sort_stat[st_user] = statistic[st_user]
    return sort_stat, buttons


async def get_head():
    from datetime import datetime
    from pytz import timezone

    dtime = datetime.now(tz=timezone('Europe/Moscow')).strftime('%d.%m.%Y %H:%M')
    return """
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
