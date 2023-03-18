import asyncpg

from utils.log import log
from work_vs_db.db_adm_chats import adm_chats_db
from work_vs_db.db_buttons import buttons_db
from work_vs_db.db_files_id import files_id_db
from work_vs_db.db_filess import f_db
from work_vs_db.db_groups_buttons import groups_db
from work_vs_db.db_moderators import moderators_db
from work_vs_db.db_stat import stat_db
from work_vs_db.db_users import users_db


async def init_bd(pool: asyncpg.Pool):

    await users_db.create(pool)
    await files_id_db.create(pool)
    await f_db.create(pool)
    await stat_db.create(pool)
    await buttons_db.init(pool)
    await groups_db.create(await buttons_db.get_names_groups(), pool)
    await adm_chats_db.init(pool)
    await moderators_db.init(pool)
    await buttons_db.check_files_in_buttons(list(f_db.files))


# ----==== ГРУППЫ ====----
async def change_group_tool(group, tool, value):
    if tool == 'name':
        old_name = group
        new_name = value
        await buttons_db.change_value_for_all_buttons("group_buttons", old_name, new_name)
        await users_db.change_last_group_for_all_users(old_name, new_name)
        await groups_db.create(await buttons_db.get_names_groups())
        await log.write(f"Группа {old_name} заменена на {new_name} для всех кнопок", 'admin')
        await log.write(f"Текущая группа {old_name} заменена на {new_name} для всех юзеров", 'admin')
        await log.write(f"Таблица групп создана заново", 'admin')
    else:
        await groups_db.write(group, [tool], [value])
        await log.write(f"Таблица групп создана заново", 'admin')


async def delete_group(group_name):
    await buttons_db.delete_group_from_buttons(group_name)
    await users_db.change_last_group_for_all_users(group_name, None)
    await groups_db.create(await buttons_db.get_names_groups())
    await log.write(f"Группа {group_name} удалена из всех кнопок", 'admin')
    await log.write(f"Текущая группа {group_name} удалена для всех юзеров", 'admin')
    await log.write(f"Таблица групп создана заново", 'admin')


# ----==== КНОПКИ ====----
async def add_button(new_button):
    await buttons_db.write(new_button, 'add_button')
    await groups_db.create(await buttons_db.get_names_groups())
    await log.write(f"Таблица групп создана заново", 'admin')


async def del_button(button):
    await buttons_db.write(button, 'del_button')
    await groups_db.create(await buttons_db.get_names_groups())
    await log.write(f"Таблица групп создана заново", 'admin')


async def change_button_tool(button, tool, value):
    if tool == "active":
        await buttons_db.write(button, [tool], [value])
        await groups_db.create(await buttons_db.get_names_groups())
        await log.write(f"Таблица групп создана заново", 'admin')

    elif tool == "group_buttons":
        list_old_names = buttons_db.buttons[button].group_buttons.split(',')
        await buttons_db.write(button, [tool], [value])
        new_list_groups = await buttons_db.get_names_groups()
        for name in list_old_names:
            if name not in new_list_groups:
                if ',' not in value:
                    await users_db.change_last_group_for_all_users(name, value)
                    await log.write(f"Текущая группа {name} заменена на {value} для всех юзеров", 'admin')
        await groups_db.create(new_list_groups)
        await log.write(f"Таблица групп создана заново", 'admin')
    else:
        await buttons_db.write(button, [tool], [value])
