import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from dotenv import load_dotenv
import database
import analytics
import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

logging.basicConfig(level=logging.INFO)

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()    

class AddExpenseForm(StatesGroup):
    name = State()
    amount = State()
    category = State()


@dp.message(Command('start'))
async def cmd_start(message: types.Message):

    builder = ReplyKeyboardBuilder()

    builder.button(text="➕ Добавить трату")
    builder.button(text="📊 Всего")
    builder.button(text="📈 Аналитика")
    builder.button(text='🗑 Удалить выбранное')
    builder.button(text="🗑 Сбросить историю")
    builder.button(text='Мин')
    builder.button(text='Макс')

    builder.adjust(2)

    await message.answer(
        "Главное меню:", 
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


@dp.message(Command('add'))
@dp.message(F.text == '➕ Добавить трату')
async def start_add_expense(message: types.Message, state: FSMContext):
    await state.set_state(AddExpenseForm.name)
    await message.answer('Введите название траты')


@dp.message(AddExpenseForm.name)
async def process_name(message: types.Message, state:FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddExpenseForm.amount)
    await message.answer('Введите сумму траты')


@dp.message(AddExpenseForm.amount)
async def process_amount(message: types.Message, state: FSMContext):
    try:
        float(message.text)
    except ValueError:
        await message.answer('Сумма должна состоять из чисел')
        return

    await state.update_data(amount=message.text)
    await state.set_state(AddExpenseForm.category)

    builder = InlineKeyboardBuilder()
    builder.button(text="Еда", callback_data="category_Еда")
    builder.button(text="Транспорт", callback_data="category_Транспорт")
    builder.button(text="Развлечения", callback_data="category_Развлечения")
    builder.adjust(2)

    await message.answer("Выбери категорию:", reply_markup=builder.as_markup())


@dp.callback_query(AddExpenseForm.category, F.data.startswith('category_'))
async def process_cateory_callback(callback: types.CallbackQuery, state: FSMContext):
    category = callback.data.split('_')[1]

    user_data = await state.get_data()
    user_id = str(callback.from_user.id)

    database.add_expense(user_id, user_data['name'], float(user_data['amount']), category)

    await state.clear()

    await callback.answer("Записано!")
    await callback.message.edit_text(
        f"Успешно добавлено: {user_data['name']} ({user_data['amount']}тг, {category})"
    )


@dp.message(Command('total'))
@dp.message(F.text == "📊 Всего")
async def show_total(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 За сегодня", callback_data="total_today")
    builder.button(text="🗓 За этот месяц", callback_data="total_month")
    builder.button(text="♾ За всё время", callback_data="total_all")
    builder.adjust(1)

    await message.answer("За какой период показать траты?", reply_markup=builder.as_markup())


@dp.callback_query(F.data.startswith('total_'))
async def process_total_callback(callback: types.CallbackQuery):
    # 1. Извлекаем период из callback.data ('today', 'month' или 'all')
    period = callback.data.split('_')[1]
    user_id = str(callback.from_user.id)

    # 2. Запрашиваем из базы траты СТРОГО за этот период
    users_expenses = database.get_expense_by_period(user_id, period)

    # 3. Если траты за период есть — считаем сумму и формируем текст
    if users_expenses:
        total = 0
        text = ''
        for s in users_expenses:
            text += f"{s['name']} - {s['amount']}тг ({s['category']})\n"
            total += int(s['amount'])
        text += f'\n<b>Итого:</b> {total}тг'
        
        await callback.answer()
        await callback.message.edit_text(text, parse_mode="HTML")
    else:
        await callback.answer("За этот период трат нет!", show_alert=True)           


@dp.message(Command('reset'))
@dp.message(F.text == '🗑 Сбросить историю')
async def process_reset(message: types.Message):
    user_id = str(message.from_user.id)
    
    database.clear_expenses(user_id)

    await message.answer('Успешно очищено')


@dp.message(Command('delete'))
@dp.message(F.text == '🗑 Удалить выбранное')
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
@dp.message(F.text == 'Макс')
async def get_max_expense(message: types.Message):
    user_id = str(message.from_user.id)
    max_expense = database.get_extreme_expense(user_id, order='DESC')

    if max_expense is None:
        await message.answer('Список пуст!!!!!!!!!!!!')
        return

    result = f"Максимальная трата:\n\n{max_expense['name']} - {max_expense['amount']}тг, {max_expense['category']}"
    await message.answer(result)


@dp.message(Command('min'))
@dp.message(F.text == 'Мин')
async def get_min_expense(message: types.Message):
    user_id = str(message.from_user.id)
    min_expense = database.get_extreme_expense(user_id, order='ASC')

    if min_expense is None:
        await message.answer('Список пуст блять пж!!!!')
        return

    result = f"Минимальная:\n\n{min_expense['name']} - {min_expense['amount']}тг, {min_expense['category']}"
    await message.answer(result)


@dp.message(Command('analytics'))
@dp.message(F.text == '📈 Аналитика')
async def get_analytics(message: types.Message):
    user_id = str(message.from_user.id)
    user_expenses = database.get_user_expenses(user_id)

    if not user_expenses:
        await message.answer('Список пуст')
        return
    
    expenses_by_categories = analytics.analyze_expenses(user_expenses)
    result = ''
    for category, amount in expenses_by_categories.items():
        result += f'{category}: {amount}тг\n'

    await message.answer(result)

    
@dp.message()
async def process_unknown_message(message: types.Message):
    await message.answer("Я не понимаю эту команду. Напишите /add чтобы добавить трату или /total для просмотра списка.")


async def main():
    database.init_db()
    await dp.start_polling(bot)

asyncio.run(main())