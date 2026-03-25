from aiogram import Router, Bot
import random
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import sqlite3
import time

conn = sqlite3.connect('users_info.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users_info_table (id INTEGER PRIMARY KEY, full_name TEXT, username TEXT, is_making_post INTEGER DEFAULT 0, cooldown INTEGER DEFAULT 0, last_post TEXT DEFAULT 'None')''')
conn.commit()

rout = Router()

@rout.message(Command('start'))
async def start(message: Message):
    await message.answer('Бот для выкладывания анонимных постов в тг канале Anon iuca\n\nВыкладывать посты можно 1 раз в 24 часа\n\nЧтобы выложить пост пропишите команду /post')
    cursor.execute('INSERT OR IGNORE INTO users_info_table (id, full_name, username, is_making_post, cooldown) VALUES (?,?,?,0,0)', (message.from_user.id, message.from_user.full_name, message.from_user.username,))
    conn.commit()

@rout.message(Command('post'))
async def post(message: Message):
    cursor.execute('SELECT cooldown FROM users_info_table WHERE id = ?', (message.from_user.id,))
    result = cursor.fetchone()
    current_time = int(time.time())

    if result and result[0] > current_time:
        diff = result[0] - current_time
        hours = diff // 3600
        minutes = (diff % 3600) // 60
        await message.answer(f'Осталось подождать: {hours}ч {minutes}мин.')
    else:
        cursor.execute('UPDATE users_info_table SET is_making_post = 1 WHERE id = ?', (message.from_user.id,))
        conn.commit()
        await message.answer('Напишите ваш пост\nМожете присылать сообщение, фото с текстом, голосовое сообщение.')

@rout.message(Command('usersall'))
async def users_all(message: Message):
    if message.from_user.username == 'Icaomo':
        cursor.execute('SELECT id, full_name, username FROM users_info_table')
        result = cursor.fetchall()
        allUsers = 'users:\n\n'
        no = 1
        for id, full_name, username in result:
            allUsers += f'{no})\n{id}\n{full_name}\n@{username}\n-----------\n'
            no += 1
        await message.answer(allUsers)
    else:
        return

@rout.message(Command('resetcd'))
async def resetcd(message: Message):
    if message.from_user.username != 'Icaomo':
        return
    text = message.text.split()
    cursor.execute('UPDATE users_info_table SET cooldown = 0 WHERE id = ?', (text[1],))
    conn.commit()
    await message.answer('Кулдаун убран')

@rout.message(Command('postinfo'))
async def postinfo(message: Message):
    if message.from_user.username != 'Icaomo':
        return
    
    last_post = message.text.replace('/postinfo', '').strip()
    
    if not last_post:
        await message.answer("Введите текст поста")
        return

    cursor.execute('SELECT id, full_name, username FROM users_info_table WHERE last_post = ?', (last_post,))
    res = cursor.fetchone()
    
    if res:
        user_id, full_name, username = res
        await message.answer(f'Информация о посте {user_id}, {full_name}, @{username}')
    else:
        await message.answer('Пост не найден')

@rout.message()
async def send_post_to_group(message: Message, bot: Bot):
    if message.text and message.text.startswith('/'):
        return

    cursor.execute('SELECT is_making_post FROM users_info_table WHERE id = ?', (message.from_user.id,))
    result = cursor.fetchone()
    
    if result and result[0] == 1:
        group_id = -1003795268738
        try:
            await bot.copy_message(chat_id=group_id, from_chat_id=message.chat.id, message_id=message.message_id)
            await message.answer('Пост сделан.\nСледующий пост можно будет сделать через 24 часа')
            cursor.execute('UPDATE users_info_table SET last_post = ? WHERE id = ?', (message.text, message.from_user.id))
            conn.commit()
            
            next_post = int(time.time()) + 86400
            cursor.execute('UPDATE users_info_table SET is_making_post = 0, cooldown = ? WHERE id = ?', (next_post, message.from_user.id))
            conn.commit()
        except Exception:
            cursor.execute('UPDATE users_info_table SET is_making_post = 0 WHERE id = ?', (message.from_user.id,))
            conn.commit()
    else:
        return