import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from dotenv import load_dotenv
import database
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
    user_id = str(message.from_user.id)
    users_expenses = database.get_user_expenses(user_id)

    if users_expenses:
        total = 0

        text = ''
        for s in users_expenses:
            text += f"{s['name']} - {s['amount']}тг, {s['category']}\n"
            total += int(s['amount'])
        text += f'\n Сумма - {total}'
        await message.answer(text)
    else:
        await message.answer('Список пустой (')        


@dp.message(Command('reset'))
async def process_reset(message: types.Message):
    user_id = str(message.from_user.id)
    
    database.clear_expenses(user_id)

    await message.answer('Успешно очищено')


@dp.message(Command('delete'))
async def process_delete(message: types.Message):
    user_id = str(message.from_user.id)
    user_expenses = database.get_user_expenses(user_id)

    if user_expenses:
        builder = InlineKeyboardBuilder()

        for expense in user_expenses:
            builder.button(
                text=f"{expense['name']} ({expense['amount']}тг, {expense['category']})",
                callback_data=f"delete_{expense['id']}"
            )
        builder.adjust(1)

        await message.answer("Выбери трату для удаления:", reply_markup=builder.as_markup())
    else:
        await message.answer("Нечего удалять")    


@dp.callback_query(F.data.startswith('delete_'))
async def process_delete_callback(callback: types.CallbackQuery):
    delete_id = int(callback.data.split('_')[1])

    database.delete_expense(delete_id)

    await callback.answer("Удалено!")
    await callback.message.edit_text("Трата успешно удалена!")


@dp.message(Command('max'))
async def get_max_expense(message: types.Message):
    user_id = str(message.from_user.id)
    max_expense = database.get_extreme_expense(user_id, order='DESC')

    if max_expense is None:
        await message.answer('Список пуст!!!!!!!!!!!!')
        return

    result = f"Максимальная трата:\n\n{max_expense['name']} - {max_expense['amount']}тг, {max_expense['category']}"
    await message.answer(result)


@dp.message(Command('min'))
async def get_min_expense(message: types.Message):
    user_id = str(message.from_user.id)
    min_expense = database.get_extreme_expense(user_id, order='ASC')

    if min_expense is None:
        await message.answer('Список пуст блять пж!!!!')
        return

    result = f"Минимальная:\n\n{min_expense['name']} - {min_expense['amount']}тг, {min_expense['category']}"
    await message.answer(result)

@dp.message()
async def process_add_expense(message: types.Message):

    if not message.text:
        return

    #Делим строку на части
    lines = message.text.split('\n')
    
    for line in lines:
        new = line.split()
        #Проверка на нужное количество элементов одной строки
        if len(new) != 3:
            await message.answer('Строка должна состоять из трех частей, название, цена, категория!!!')
            return
        #Проверка второго элемента строки, число или нет
        try:
            int(new[1])
        except ValueError:
            await message.answer(f'{new[1]} - не является числом')
            return
        
    #Записать историю в переменную expenses    
    user_id = str(message.from_user.id)

    #Добавление новых трат
    for line in lines:
        new = line.split()
        name = new[0]
        amount = int(new[1])
        category = new[2]
        database.add_expense(user_id, name, amount, category)

    await message.answer('Успешно записано')


async def main():
    database.init_db()
    await dp.start_polling(bot)

asyncio.run(main())