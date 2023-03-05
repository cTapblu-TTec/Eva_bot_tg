import os

import asyncpg
from dataclasses import dataclass

from utils.log import log
from utils.notify_admins import notify_admins


@dataclass()
class File:
    name: str
    num_line: int
    active: int
    length: int


class FilesDatabase:
    pool: asyncpg.Pool
    files: dict

    #
    # __________CREAT__________
    async def create(self, pool: asyncpg.Pool):

        if pool: self.pool = pool
        # await self.dell()
        query = """CREATE TABLE IF NOT EXISTS public.filess
                (
                    name character varying(30) COLLATE pg_catalog."default" NOT NULL,
                    num_line smallint NOT NULL DEFAULT 0,
                    active smallint NOT NULL DEFAULT 1,
                    length smallint DEFAULT NULL,
                    CONSTRAINT filess_pkey PRIMARY KEY (name)
                );
                    """
        async with self.pool.acquire():
            await self.pool.execute(query)

        ff = await self.read('get_names_files', '')
        if not ff:
            with open('files.txt', 'r', encoding='utf-8') as f:
                ff = f.readlines()
            query = """INSERT INTO filess (name) VALUES ($1) ON CONFLICT (name) DO NOTHING;"""
            for file in ff:
                file = file.rstrip('\n')
                async with self.pool.acquire(): await self.pool.execute(query, file)
            ff = await self.read('get_names_files', '')

        self.files = {i: await self.read('', i) for i in ff}

        files_in_dir = os.listdir('dir_files/')
        for file in files_in_dir:
            if file not in ff:
                await self.write(file, 'add_file')
        for file in ff:
            if file not in files_in_dir:
                await log.write(f'Файла "{file}" нет в папке', 'admin')

    #
    # __________READ__________
    async def read(self, command: str, file_name: str):

        if command == 'get_names_files':
            query = """SELECT name FROM filess WHERE active = 1;"""
            async with self.pool.acquire(): u = await self.pool.fetch(query)
            files_names = []
            for i in u:
                files_names.append(i['name'])
            return files_names

        else:
            # 'name, num_line, num_block, size_blok, file_id, next_file_id'
            query = f"""SELECT * FROM filess WHERE name = $1;"""
            async with self.pool.acquire(): u = await self.pool.fetch(query, file_name)
            file = None
            if u:
                file = File(
                            name=file_name,
                            num_line=u[0]['num_line'],
                            active=u[0]['active'],
                            length=u[0]['length']
                            )
            return file

    #
    # __________WRITE__________
    async def write(self, file_name: str, command, values=None):

        if command == 'add_file':
            query = """INSERT INTO filess (name) VALUES ($1) ON CONFLICT (name) DO NOTHING;"""
            async with self.pool.acquire(): await self.pool.execute(query, file_name)
            file = await self.read('', file_name)
            self.files.update({file_name: file})

        elif command == 'dell_file':
            if file_name in ['name.txt', 'gena.txt']:
                await log.write(f'Файлы "name.txt", "gena.txt" нельзя удалять', 'admin')
                return
            from work_vs_db.db_buttons import buttons_db

            query = """DELETE FROM filess WHERE name = $1;"""
            async with self.pool.acquire(): await self.pool.execute(query, file_name)
            self.files.pop(file_name)
            os.remove('dir_files/' + file_name)
            await buttons_db.change_value_for_all_buttons("work_file", file_name, 'None')
            await buttons_db.change_value_for_all_buttons("shablon_file", file_name, 'None')

        elif command == 'n_line':
            query = """UPDATE filess SET num_line = $2 WHERE name = $1;"""
            async with self.pool.acquire(): await self.pool.execute(query, file_name, values)

        else:
            columns = command  # ['name', 'num_line', 'num_block', 'size_blok', 'file_id', 'next_file_id']

            for i in range(len(columns)):
                query = f"""UPDATE filess SET {columns[i]} = '{values[i]}' WHERE name = $1;"""
                async with self.pool.acquire(): await self.pool.execute(query, file_name)

            file = await self.read('', file_name)
            self.files.update({file_name: file})

    #
    # __________DELETE TABLE__________
    async def dell(self):

        query = 'DROP TABLE public.filess'
        async with self.pool.acquire(): await self.pool.execute(query)

    async def get_len_file(self, file):
        length = self.files[file].length
        if length:
            return int(length)
        else:
            try:
                with open('dir_files/' + file, "r", encoding='utf-8') as f:
                    length = len(f.readlines())
                await f_db.write(file, ['length'], [length])
                return int(length)
            except FileNotFoundError:
                await notify_admins(f'файл {file} не найден')


async def another():
    content = os.listdir('dir_files/')
    print(content)


f_db = FilesDatabase()
