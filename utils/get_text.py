import random

from utils.notify_admins import notify


Files: dict = {}  # имя файла: файл


async def open_file(file: str):
    try:
        if file not in Files:
            f = open('dir_files/'+file, 'r', encoding='utf-8')
            Files[file] = f.readlines()
            f.close()
        if len(Files) >= 5:  # храним последние 5 файлов в памяти
            for k in Files.keys():
                Files.pop(k)
                break
        return Files[file]
    except Exception:
        await notify(f'Файл {file} не читается')
        return None


async def get_template(replacement_num, n_lasts_templates, file_template):
    list_f = await open_file(file_template)
    list_re = await open_file('name.txt')
    if list_f is None or list_re is None:
        return f'Файл {file_template} не читается', replacement_num, n_lasts_templates

    num_line = random.randint(0, len(list_f) - 1)

    # проверка что этот шаблон не выдавался этому пользователю 35 последних раз
    if n_lasts_templates:
        if isinstance(n_lasts_templates, str) and len(n_lasts_templates) > 4:
            n_lasts_templates = n_lasts_templates[1:-1]
            list_lasts = n_lasts_templates.split(',')  # список номеров использованных шаблонов
        elif isinstance(n_lasts_templates, list):
            list_lasts = n_lasts_templates
        elif isinstance(n_lasts_templates, tuple):
            list_lasts = list(n_lasts_templates)
        else:
            list_lasts = []
            list_lasts.append(n_lasts_templates)
        if len(list_lasts) >= 35: del list_lasts[0:len(list_lasts) - 35]  # удаляем лишнее

        # если выдавался ранее, ищем другой
        while str(num_line) in list_lasts:
            num_line = random.randint(0, len(list_f) - 1)
        list_lasts.append(str(num_line))
        n_lasts_templates = tuple(list_lasts)
    else:
        n_lasts_templates = str(num_line)

    text = str(list_f[num_line])  # выдача нужного шаблона

    # ПОДМЕНА В ШАБЛОНЕ СИНОНИМОВ
    replace = False
    for line in list_re:
        synonyms = line.split(', ')  # делим строку на список
        for word in synonyms:  # проверка строки
            word = word.strip()
            if word in text:
                index1 = text.find(word)
                index2 = len(word) + index1
                if index2 == len(text) or text[index2] in ' !?.,\n)"':
                    word2 = synonyms[replacement_num % len(synonyms)].strip()
                    replace = True
                    text = text.replace(word, word2)  # замена слова
    if replace: replacement_num += 1
    if replacement_num >= 10: replacement_num = 0
    return text, replacement_num, n_lasts_templates


async def get_link_list(n_f_line: int, k: int, file: str):
    linesf = await open_file(file)
    if linesf is None:
        await notify(f'Файл {file} не читается')
        return f'Файл не читается', n_f_line
    len_f = len(linesf)

    text = ''
    for i in range(k):
        if n_f_line >= len_f:
            # todo сюда добавить проверку что в основном файле есть еще отметки и загрузку из него нового кусочка 5000
            text += '\nсписок исчерпан'
            await notify(f"{file} исчерпан")
            break
        if text != '' and text[-1] != '\n': text = text + '\n'
        text += str(linesf[n_f_line])
        n_f_line += 1

    return text, n_f_line
