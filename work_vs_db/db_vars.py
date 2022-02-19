import asyncpg


class VarsDatabase:
    pool: asyncpg.Pool
    n_otmetki: int
    n_storis: int
    n_shablon: int
    n_get_id: int
    n_vk_id: int
    n_get_http: int
    n_vk_http: int
    n_get_club: int
    n_vk_club: int
    n_get_lots: int
    n_vk_lots: int

    # __________CREAT__________
    async def create(self, pool: asyncpg.Pool):
        self.pool = pool

        query = """CREATE TABLE IF NOT EXISTS public.vars
                (
                    n_otmetki integer NOT NULL DEFAULT 0,
                    n_storis smallint NOT NULL DEFAULT 1,
                    n_shablon smallint NOT NULL DEFAULT 0,
                    n_get_id smallint NOT NULL DEFAULT 1,
                    n_vk_id smallint NOT NULL DEFAULT 0,
                    n_get_http smallint NOT NULL DEFAULT 1,
                    n_vk_http smallint NOT NULL DEFAULT 0,
                    n_get_club smallint NOT NULL DEFAULT 1,
                    n_vk_club smallint NOT NULL DEFAULT 0,
                    n_get_lots smallint NOT NULL DEFAULT 1,
                    n_vk_lots smallint NOT NULL DEFAULT 0,
                    num smallint NOT NULL DEFAULT 1,
                    CONSTRAINT vars_pkey PRIMARY KEY (num)
                );
                    
                    INSERT INTO vars (num) VALUES (1) ON CONFLICT (num) DO NOTHING;
                    """
        async with self.pool.acquire(): await self.pool.execute(query)

        await self.read()
        # query = f'SELECT * FROM vars WHERE num = $1'
        # async with self.pool.acquire(): z = await self.pool.fetch(query, 1)
        # print(z)

    # __________READ__________
    async def read(self):

        query = 'SELECT * FROM vars WHERE num = 1'
        async with self.pool.acquire(): v = await self.pool.fetch(query)
        self.n_otmetki = v[0]['n_otmetki']
        self.n_storis = v[0]['n_storis']
        self.n_shablon = v[0]['n_shablon']
        self.n_get_id = v[0]['n_get_id']
        self.n_vk_id = v[0]['n_vk_id']
        self.n_get_http = v[0]['n_get_http']
        self.n_vk_http = v[0]['n_vk_http']
        self.n_get_club = v[0]['n_get_club']
        self.n_vk_club = v[0]['n_vk_club']
        self.n_get_lots = v[0]['n_get_lots']
        self.n_vk_lots = v[0]['n_vk_lots']

    # __________WRITE__________
    async def write(self, command: list, DICT: list):
        stolbec = command  # ['n_otmetki', 'n_storis', 'n_shablon']
        stolbcov = len(command)
        for i in range(stolbcov):
            query = f'UPDATE vars SET {stolbec[i]} = {DICT[i]} WHERE num = 1'
            async with self.pool.acquire(): await self.pool.execute(query)

            if stolbec[i] == 'n_otmetki': self.n_otmetki = DICT[i]
            if stolbec[i] == 'n_storis': self.n_storis = DICT[i]
            if stolbec[i] == 'n_shablon': self.n_shablon = DICT[i]
            if stolbec[i] == 'n_get_id': self.n_get_id = DICT[i]
            if stolbec[i] == 'n_vk_id': self.n_vk_id = DICT[i]
            if stolbec[i] == 'n_get_http': self.n_get_http = DICT[i]
            if stolbec[i] == 'n_vk_http': self.n_vk_http = DICT[i]
            if stolbec[i] == 'n_get_club': self.n_get_club = DICT[i]
            if stolbec[i] == 'n_vk_club': self.n_vk_club = DICT[i]
            if stolbec[i] == 'n_get_lots': self.n_get_lots = DICT[i]
            if stolbec[i] == 'n_vk_lots': self.n_vk_lots = DICT[i]


vars_db = VarsDatabase()
