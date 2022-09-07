import logging
import math
import time
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils import executor
import asyncio
from contextlib import suppress
import requests

from aiogram.utils.exceptions import (
    MessageToEditNotFound, MessageCantBeEdited, MessageCantBeDeleted, MessageToDeleteNotFound)

import config as cfg
import markups as nav
from db import Database

# logging.basicConfig(level=logging.INFO)

bot = Bot(token=cfg.tg_bot_token)
dp = Dispatcher(bot)
db = Database('database.db')
chat_admins = bot.get_chat_administrators(cfg.CHAT_ID)


print(chat_admins)


# Реализация логирования в отдельный файл: moderator.log
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


async def delete_message(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()


def check_sub_channel(chat_member):
    return chat_member['status'] != "left"


# Декоратор накинуть мут в чате. отправить !мут 55 в ответ сообщения (мут на 55 мин)


@dp.message_handler(commands=['мут'], commands_prefix="!")
async def mut(message: types.Message):
    x = str(message.from_user.username)
    y = str(message.reply_to_message.from_user.username)

    print(f"этот---> {x}, заблочил этого--> {y}")
    mute_min = int(message.text[5:])
    await bot.restrict_chat_member(cfg.CHAT_ID, message.reply_to_message.from_user.id, until_date=math.floor(time.time()) + mute_min * 60, can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False, can_add_web_page_previews=False)
    await message.bot.delete_message(cfg.CHAT_ID, message.reply_to_message.message_id)
    await message.bot.delete_message(cfg.CHAT_ID, message.message_id)
    await bot.send_message(message.chat.id, f'@{x} заблокировал @{y} на {mute_min} минут')


# Декоратор разрешить писать в чате в чате.


@dp.message_handler(commands=['размут'], commands_prefix="!")
async def unmut(message: types.Message):
    print(message.reply_to_message.from_user.id)
    await bot.restrict_chat_member(
        cfg.CHAT_ID, message.reply_to_message.from_user.id, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)


@dp.message_handler(commands=['свой'], commands_prefix="!")
async def add_svoi(message: types.Message):
    if str(message.from_user.id) == cfg.ADMIN_ID:
        fs = True
        db.add_wite_list(message.reply_to_message.from_user.id, fs)
        await message.bot.delete_message(cfg.CHAT_ID, message.message_id)


@dp.message_handler(content_types=["new_chat_members"])
async def user_joined(message: types.Message):
    new_mem = await message.reply(f'{message.from_user.full_name}, Привет! чат доступен:\nтолько для подписчиков канала @OmArtVall', reply_markup=nav.channelMenu)
    asyncio.create_task(delete_message(new_mem, 5))
    await message.delete()


@dp.message_handler()
async def mess_handler(message: types.Message):
    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)

    if not db.examination_white_list(message.from_user.id):
        if check_sub_channel(await bot.get_chat_member(chat_id=cfg.CHANNEL_ID, user_id=message.from_user.id)):
            text = message.text.lower()
            for word in cfg.WORLDS:
                if word in text:
                    await message.delete()

        else:
            msg = await message.reply(f'{message.from_user.full_name}, Чат доступен:\nТОЛЬКО ДЛЯ ПОДПИСЧИКОВ КАНАЛА!!!\n\nЕсть 3 секунды сделать это\n\n @OmArtVall', reply_markup=nav.channelMenu)
            asyncio.create_task(delete_message(msg, 5))
            await message.delete()
    else:
        print('z v o')


@dp.message_handler(content_types=["left_chat_member"])
async def start_commandr(message: types.Message):
    await message.answer("Ливнул, сучара...\n🤷‍♀️Чё приходил этот говноед...🤷🏻‍♂️")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

# @dp.message_handler(commands=['id'], commands_prefix="/")
# async def get_id(message: types.Message):
#     await bot.send_message(message.from_id, f"ID: {message.from_user.id}")
# test 135
