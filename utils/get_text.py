import random

from data.config import ADMINS
from loader import dp


class Spiski:
    l_otmetki: list
    l_polina: list
    l_zamena: list
    l_otm_vernuli: list

    def __init__(self):
        self.create_spiski(('otmetki.txt', 'polina.txt', 'name.txt'))

    def create_spiski(self, files: tuple):

        if 'otmetki.txt' in files:
            with open('otmetki.txt', "r") as f:
                self.l_otmetki = f.readlines()

        if 'polina.txt' in files:
            with open('polina.txt', "r") as f:
                self.l_polina = f.readlines()

        if 'name.txt' in files:
            with open('name.txt', "r") as f:
                self.l_zamena = f.readlines()

        self.l_otm_vernuli = []


s = Spiski()


# Vid_Shabl(b, n_zamen, n_last_sabl)
async def Vid_Shabl(b, c, N_50_sabl):
    N_shabl = random.randint(0, len(s.l_polina) - 1)

    # проверка что этот шаблон не выдавался этому пользователю 50 последних раз
    if N_50_sabl:
        if isinstance(N_50_sabl, str) and len(N_50_sabl) > 4:
            N_50_sabl = N_50_sabl[1:-1]
            list_shabl = N_50_sabl.split(',')  # список номеров использованных шаблонов
        elif isinstance(N_50_sabl, list):
            list_shabl = N_50_sabl
        elif isinstance(N_50_sabl, tuple):
            list_shabl = list(N_50_sabl)
        else:
            list_shabl = []
            list_shabl.append(N_50_sabl)
        if len(list_shabl) >= 35: del list_shabl[0:len(list_shabl) - 35]  # удаляем лишнее

        while str(N_shabl) in list_shabl:
            N_shabl = random.randint(0, len(s.l_polina) - 1)
        list_shabl.append(str(N_shabl))
        N_50_ = tuple(list_shabl)
    else:
        N_50_ = str(N_shabl)

    text = str(s.l_polina[N_shabl])  # выдача нужного шаблона

    est = False
    for line in s.l_zamena:
        stroka = line.split(', ')  # делим строку на список
        for slovo in stroka:  # проверка строки
            slovo = slovo.strip()
            if slovo in text:
                index1 = text.find(slovo)
                index2 = len(slovo) + index1
                if index2 == len(text) or text[index2] in ' !?.,\n)"':
                    slovo2 = stroka[c % len(stroka)].strip()
                    est = True
                    text = text.replace(slovo, slovo2)  # замена слова
    if est: c = c + 1
    if c >= 10: c = 0
    b += 1  # просто счетчик выданных шаблонов
    return text, b, c, N_50_


# k - сколько выдать отметок
async def Vid_Otmetok(text, a, k, l_otm_vernuli):
    n_last_otm = ()
    use = True
    for i in range(k):
        if len(l_otm_vernuli) > 0:
            if text != '' and text[-1] != '\n': text = text + '\n'
            n_last_otm += (l_otm_vernuli[0],)
            text = text + str(l_otm_vernuli.pop(0))
        else:
            if a >= len(s.l_otmetki):
                use = False
            if use:
                if text != '' and text[-1] != '\n': text = text + '\n'
                text = text + s.l_otmetki[a]
                n_last_otm += (s.l_otmetki[a],)
                a += 1
    if not use:
        text += '\nсписок отметок исчерпан'
        if n_last_otm == (): n_last_otm = 0
        for admin in ADMINS:
            await dp.bot.send_message(admin, "список отметок исчерпан")
    return text, a, n_last_otm, l_otm_vernuli


async def get_vk_text(n_f_line: int, n_get: int, k: int, file: str):
    use = True
    f = open(file, 'r')
    linesf = f.readlines()
    f.close()

    text = ''
    for i in range(k):
        if n_f_line >= len(linesf):
            use = False
        if use:
            if text != '' and text[-1] != '\n': text = text + '\n'
            text += str(linesf[n_f_line])
            n_f_line += 1
    text = f'{n_get} \n {text}'
    if not use:
        text += '\nсписок отметок исчерпан'
        for admin in ADMINS:
            await dp.bot.send_message(admin, "список отметок исчерпан")

    return text, n_f_line, n_get + 1
