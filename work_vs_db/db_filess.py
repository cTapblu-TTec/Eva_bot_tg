import asyncpg
from dataclasses import dataclass


@dataclass()
class File:
    name: str
    num_line: int
    active: int
    length: int


class FilesDatabase:
    pool: asyncpg.Pool
    files_names: list
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
            with open('files.txt', 'r') as f: # encoding='utf-8-sig'
                ff = f.readlines()
            query = """INSERT INTO filess (name) VALUES ($1) ON CONFLICT (name) DO NOTHING;"""
            for file in ff:
                file = file.rstrip('\n')
                async with self.pool.acquire(): await self.pool.execute(query, file)
            ff = await self.read('get_names_files', '')

        self.files = {i: await self.read('', i) for i in ff}
        self.files_names = []
        for name in ff:
            self.files_names.append(name[:-4])

    #
    # __________READ__________
    async def read(self, command: str, file_name: str):

        if command == 'get_names_files':
            query = """SELECT name FROM filess WHERE active = 1;"""
            async with self.pool.acquire():
                u = await self.pool.fetch(query)
            files_names = []
            for i in u:
                files_names.append(i['name'])
            return files_names

        else:
            # 'name, num_line, num_block, size_blok, file_id, next_file_id'
            query = f"""SELECT * FROM filess WHERE name = $1;"""
            async with self.pool.acquire():
                u = await self.pool.fetch(query, file_name)
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
    async def write(self, file_name: str, command, values):

        if command == 'add_file':
            query = """INSERT INTO filess (name) VALUES ($1) ON CONFLICT (name) DO NOTHING;"""
            async with self.pool.acquire(): await self.pool.execute(query, file_name)
            self.files_names.append(file_name[:-4])
            query = f"""UPDATE filess SET active = 1 WHERE name = $1;"""
            async with self.pool.acquire():
                await self.pool.execute(query, file_name)

            file = await self.read('', file_name)
            self.files.update({file_name: file})

        elif command == 'dell_file':
            query = f"""UPDATE filess SET active = 0 WHERE name = $1;"""
            async with self.pool.acquire():
                await self.pool.execute(query, file_name)

            self.files_names.remove(file_name[:-4])
            self.files.pop(file_name)

        else:
            stolbec = command  # ['name', 'num_line', 'num_block', 'size_blok', 'file_id', 'next_file_id']
            stolbcov = len(command)

            for i in range(stolbcov):
                query = f"""UPDATE filess SET {stolbec[i]} = '{values[i]}' WHERE name = $1;"""
                async with self.pool.acquire(): await self.pool.execute(query, file_name)
                if stolbec[i] == 'num_line':
                    self.files[file_name].num_line = values[i]
                if stolbec[i] == 'length':
                    self.files[file_name].length = values[i]

    #
    # __________DELETE TABLE__________
    async def dell(self):

        query = 'DROP TABLE public.filess'
        async with self.pool.acquire(): await self.pool.execute(query)


f_db = FilesDatabase()
