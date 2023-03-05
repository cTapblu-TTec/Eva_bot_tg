import asyncpg

from loader import dp
from utils.notify_admins import notify_admins


class FileDatabase:
    pool: asyncpg.Pool
    files = {}  # список файлов в бд

    # ______CREATE______
    async def create(self, pool: asyncpg.Pool):
        self.pool = pool

        query = """CREATE TABLE IF NOT EXISTS public.files_id
                (
                    file_name character varying(30) COLLATE pg_catalog."default" NOT NULL,
                    file_id character varying NOT NULL,
                    next_file_id varchar DEFAULT NULL,
                    CONSTRAINT "Files_id_pkey" PRIMARY KEY (file_name)
                ); """
        async with self.pool.acquire(): await self.pool.execute(query)
        await self.read()
        for file in self.files:
            await download_file_from_tg(file)
            # отрезать от файла использованное
            # добавить проверку что если в файле осталось больше 5000 неиспользованных строк, то из него
            # нужно вырезать кусок в 5000 строк

    # ______READ______
    async def read(self):
        query = 'SELECT * FROM files_id;'
        async with self.pool.acquire(): file = await self.pool.fetch(query)
        if file:
            for i in file:
                self.files[i['file_name']] = i['file_id']

    # ______WRITE______
    async def write(self, file_name: str, file_id: str):
        # ДОБАВЛЕНИЕ в БД ФАЙЛА
        if self.files == {} or file_name not in self.files:
            query = """INSERT INTO files_id (file_id, file_name) VALUES ($1, $2) ON CONFLICT (file_name) DO NOTHING;"""
            async with self.pool.acquire(): await self.pool.execute(query, file_id, file_name)

        # ОБНОВЛЕНИЕ FILE_ID
        else:
            query = """UPDATE files_id SET file_id = $1 WHERE file_name = $2;"""
            async with self.pool.acquire(): await self.pool.execute(query, file_id, file_name)
            self.files[file_name] = file_id


async def download_file_from_tg(file_name: str):
    dir_f = 'dir_files/'
    if file_name in files_id_db.files[file_name]:
        file_id = files_id_db.files[file_name]  # берем id из базы
        try:
            # получаем файл по id из телеграмма
            file = await dp.bot.get_file(file_id)
            file_path = file.file_path
            await dp.bot.download_file(file_path, dir_f + file_name)
        except Exception:
            await notify_admins(f'Не удалось скачать файл с телеграмма: {file_name}')

files_id_db = FileDatabase()
