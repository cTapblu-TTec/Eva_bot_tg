import random

from utils.notify_admins import notify


# Vid_Shabl(b, n_zamen, n_last_sabl)
async def get_template(c, N_50_sabl, file_template):
    try:
        with open('dir_files/'+file_template, 'r') as file:
            l_shablon = file.readlines()
        with open('dir_files/name.txt', 'r') as file:
            l_zamena = file.readlines()
    except Exception:
        await notify(f'Файл {file_template} не читается')
        return f'Файл {file_template} не читается', c, N_50_sabl

    N_shabl = random.randint(0, len(l_shablon) - 1)

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
            N_shabl = random.randint(0, len(l_shablon) - 1)
        list_shabl.append(str(N_shabl))
        N_50_ = tuple(list_shabl)
    else:
        N_50_ = str(N_shabl)

    text = str(l_shablon[N_shabl])  # выдача нужного шаблона

    est = False
    for line in l_zamena:
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
    return text, c, N_50_


async def get_link_list(n_f_line: int, k: int, file: str):
    use = True
    try:
        with open('dir_files/'+file, 'r') as f:
            linesf = f.readlines()
    except Exception:
        await notify(f'Файл {file} не читается')
        return f'Файл {file} не читается', n_f_line
    text = ''
    for i in range(k):
        if n_f_line >= len(linesf):
            use = False
        if use:
            if text != '' and text[-1] != '\n': text = text + '\n'
            text += str(linesf[n_f_line])
            n_f_line += 1

    if not use:
        text += '\nсписок исчерпан'
        await notify(f"{file} исчерпан")

    return text, n_f_line
