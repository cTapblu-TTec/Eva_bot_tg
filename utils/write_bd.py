from asyncio import sleep

from dataclasses import dataclass


@dataclass()
class WritedBD:
    writed: bool = True
    write_number: bool = False
    write_template: bool = False
    write_links: bool = False


async def write_bd(number, template, links):
    #  что нужно записать в базу
    if number:
        WritedBD.write_number = True
    if template:
        WritedBD.write_template = True
    if links:
        WritedBD.write_links = True
    await wait_10sec()


async def wait_10sec():
    if WritedBD.writed:
        WritedBD.writed = False
        await sleep(10)  # ждем накопления записей в БД 10 сек
        if not WritedBD.writed:
            WritedBD.writed = True
            # await write()
    else:
        return


# TODO тут неплохо было бы доделать периодическую запись в базу а не как сейчас
"""
async def write():
    if WritedBD.write_number:  # если с номером
        await buttons_db.write(button_name, 'num_block', button.num_block)

    # -----===== исправить на работу без Ф-строк========-------
    if tem:  # если с шаблоном
        await users_db.write(message.from_user.username, ['n_zamen', 'n_last_shabl', 'last_button'],
                             [u.n_zamen, u.n_last_shabl, button_name])
    else:  # клавиатура
        await users_db.write(message.from_user.username, ['last_button'], [button_name])

    if button.hidden == 0:  # пишем статистику если кнопка не скрытая
        await stat_db.write(message.text, message.from_user.username)

    if otm:  # если с отметками
        await f_db.write(button.work_file, 'num_line', f_db.files[button.work_file].num_line)
        # лог всегда дб последним действием!
        await log(f'№ строки {message.text}: {num_line}, ({message.from_user.username})\n')
        logger.info("8 - Конец")
    else:
        await log(f'{message.text}, ({message.from_user.username})\n')
"""
