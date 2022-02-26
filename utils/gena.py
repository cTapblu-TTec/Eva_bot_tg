import random


class SlovDB:
    class Sinonemi:
        id: str  # p1, op5, s3, d6, - личный номер
        si: str  # p1, s3 - к каком слову привязано, если p - подлежащее, s - сказуемое
        ti: str  # p, op, s, d, ob - что за член предложения
        txt: str  # сами синонемы одинакового рода
        k: int  # количество вариантов в строке

    l_sl = []  # полный список
    l_skaz = []  # список номеров сказуемых
    vsego_variantov = 0

    def __init__(self):
        self.read()

    def read(self):
        with open('db.txt', 'r') as f_db:
            lf = f_db.readlines()
        k = 1
        pk = 1
        for i in lf:

            i = i.strip()
            if i != '' and '#' not in i:
                i = i.split('/')
                sl = self.Sinonemi()
                sl.id = i[0]
                sl.si = i[1]
                sl.txt = i[2].strip().split('. ')

                # создаем sl.ti (тип слов)
                n_ = 0
                for j in i[0]:
                    if j.isdigit() and n_ == 0: n_ = j
                n = i[0].find(n_)
                sl.ti = i[0][:n]

                # список сказуемых
                if sl.ti == 's': self.l_skaz.append((sl.id, sl.si))
                self.l_sl.append(sl)

                # количество вариантов для текущего сказуемого
                sl.k = len(sl.txt)
                if sl.ti == 'op':
                    k = 1
                    pk = 1
                if sl.ti == 'ob':
                    k = 1
                if sl.k != 0:
                    k = k * sl.k
                if sl.ti == 'p':
                    pk = k
                    k = 1
                if sl.ti == 'd':
                    sk = pk * k
                    self.l_skaz[-1] += (sk, self.vsego_variantov)
                    k = 1
                    # print(sk, sl.si)
                    self.vsego_variantov += sk


db_sl = SlovDB()
# print(db_sl.l_skaz)
print('Вариантов шаблонов Гены:', db_sl.vsego_variantov)


class Predlojenie:
    class Chlen:
        text = ''
        poziciya: int
        nomer: int

    last_s = []
    podlezashee = Chlen()
    skazuemoe = Chlen()
    opredelenie = Chlen()
    dopolnenie = Chlen()
    obstoyatelstvo = Chlen()

    async def get_text(self):
        await self.vibor_slov()
        text = await self.slojenie_slov()
        while text in self.last_s:
            print('iskl')
            await self.vibor_slov()
            text = await self.slojenie_slov()

        self.last_s.append(text)
        if len(self.last_s) >= 100: del self.last_s[0:len(self.last_s) - 100]  # удаляем лишнее

        return text

    async def slojenie_slov(self):
        t_l = [self.opredelenie.text, self.podlezashee.text, self.obstoyatelstvo.text, self.skazuemoe.text, self.dopolnenie.text]
        t = ''
        for i in t_l:
            if not '$' in i and i.strip():
                t += i
        t = t.strip().replace('  ', ' ')
        x = t[:1].upper()
        return x + t[1:]

    async def vibor_slov(self):
        c = random.randint(1, db_sl.vsego_variantov)
        zn = db_sl.l_sl[c % len(db_sl.l_sl)]
        for i in db_sl.l_skaz:
            if i[3] < c < i[3] + i[2]:
                # print(i[3], c, i[3] + i[2])
                zn = i
        self.last_s.append(zn)
        if len(self.last_s) >= 5: del self.last_s[0:len(self.last_s) - 5]  # удаляем лишнее

        for i in db_sl.l_sl:
            if i.si == zn[1] and i.ti == 'op':
                c = random.randint(0, 50)
                self.opredelenie.text = i.txt[c % len(i.txt)].strip() + ' '  # выбор слова из списка
            if i.id == zn[1]:
                c = random.randint(0, 50)
                self.podlezashee.text = i.txt[c % len(i.txt)].strip() + ' '
            if i.si == zn[1] and i.id == zn[0]:
                c = random.randint(0, 50)
                self.skazuemoe.text = i.txt[c % len(i.txt)].strip() + ' '
            if i.si == zn[0] + zn[1] and i.ti == 'ob':
                c = random.randint(0, 50)
                self.obstoyatelstvo.text = i.txt[c % len(i.txt)].strip() + ' '  # выбор слова из списка
            if i.si == zn[0] + zn[1] and i.ti == 'd':
                c = random.randint(0, 50)
                self.dopolnenie.text = i.txt[c % len(i.txt)].strip()  # выбор слова из списка


gennadij = Predlojenie()
