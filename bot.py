import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from dotenv import load_dotenv
from database import get_expenses, save_expenses
import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

logging.basicConfig(level=logging.INFO)

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()    


@dp.message(Command('total'))
async def show_total(message: types.Message):
    db_data = get_expenses()
    user_id = str(message.from_user.id)

    if user_id in db_data:
        users_expenses = db_data[user_id]
        total = 0

        text = ''
        for s in users_expenses:
            text += f"{s['name']} - {s['amount']}тг\n"
            total += int(s['amount'])
        text += f'\n Сумма - {total}'
        await message.answer(text)
    else:
        await message.answer('Список пустой (')        


@dp.message(Command('delete'))
async def process_delete(message: types.Message):
    user_id = str(message.from_user.id)
    db_data = get_expenses()
    user_expenses = db_data.get(user_id, [])

    if user_expenses:
        builder = InlineKeyboardBuilder()

        for index, expense in enumerate(user_expenses):
            builder.button(
                text=f"{expense['name']} ({expense['amount']}тг)",
                callback_data=f'delete_{index}'
            )
        builder.adjust(1)

        await message.answer("Выбери трату для удаления:", reply_markup=builder.as_markup())
    else:
        await message.answer("Нечего удалять")    


@dp.callback_query(F.data.startswith('delete_'))
async def process_delete_callback(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    delete_index = int(callback.data.split('_')[1])
    db_data = get_expenses()
    user_expenses = db_data[user_id]

    #Удаление выбранной записи
    user_expenses.pop(delete_index)

    #Сохранение изменения
    save_expenses(db_data)

    await callback.answer("Удалено!")
    await callback.message.edit_text("Трата успешно удалена!")


@dp.message()
async def add_expense(message: types.Message):

    if not message.text:
        return

    #Делим строку на части
    lines = message.text.split('\n')
    
    for line in lines:
        new = line.split()
        #Проверка на нужное количество элементов одной строки
        if len(new) != 2:
            await message.answer('Строка должна состоять из двух частей, название и цена!!!')
            return
        #Проверка второго элемента строки, число или нет
        try:
            int(new[1])
        except ValueError:
            await message.answer(f'{new[1]} - не является числом')
            return
        
    #Записать историю в переменную expenses    
    db_data = get_expenses()
    user_id = str(message.from_user.id)

    if user_id not in db_data:
        db_data[user_id] = []

    #Добавление новых трат
    for line in lines:
        new = line.split()
        text = {'name': new[0], 'amount': new[1]}
        db_data[user_id].append(text)
        
    save_expenses(db_data)

    await message.answer('Успешно записано')


async def main():
    await dp.start_polling(bot)

asyncio.run(main())