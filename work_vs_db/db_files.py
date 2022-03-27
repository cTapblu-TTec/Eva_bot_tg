import asyncpg

from loader import dp
from utils.notify_admins import notify


class FileDatabase:
    pool: asyncpg.Pool
    files = {}  # список файлов в бд

    # ______CREATE______
    async def create(self, pool: asyncpg.Pool):
        self.pool = pool

        query = """CREATE TABLE IF NOT EXISTS public.files
                (
                    file_name character varying(30) COLLATE pg_catalog."default" NOT NULL,
                    file_id character varying NOT NULL,
                    next_file_id varchar DEFAULT NULL,
                    CONSTRAINT "Files_pkey" PRIMARY KEY (file_name)
                ); """
        async with self.pool.acquire(): await self.pool.execute(query)
        await self.read()
        for file in self.files:
            await download(file)

    # ______READ______
    async def read(self):
        query = 'SELECT * FROM files;'
        async with self.pool.acquire(): F = await self.pool.fetch(query)
        if F:
            for i in F:
                self.files[i['file_name']] = i['file_id']

    # ______WRITE______
    async def write(self, file_name:str, file_id:str):
        # ДОБАВЛЕНИЕ в БД ФАЙЛА
        if self.files == {} or file_name not in self.files:
            query = """INSERT INTO files (file_id, file_name) VALUES ($1, $2) ON CONFLICT (file_name) DO NOTHING;"""
            async with self.pool.acquire(): await self.pool.execute(query, file_id, file_name)

        # ОБНОВЛЕНИЕ FILE_ID
        else:
            query = """UPDATE files SET file_id = $1 WHERE file_name = $2;"""
            async with self.pool.acquire(): await self.pool.execute(query, file_id, file_name)
            self.files[file_name] = file_id


async def download(file_name: str):
    dir = 'dir_files/'
    file_id = files_db.files[file_name]  # берем id из базы
    # получаем файл по id из телеграмма
    try:
        file = await dp.bot.get_file(file_id)
        file_path = file.file_path
        await dp.bot.download_file(file_path, dir+file_name)
    except Exception:
        await notify(f'Не удалось скачать файл с телеграмма: {file_name}')

files_db = FileDatabase()
