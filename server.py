"""Сервер Telegram бота, запускаемый непосредственно"""
import logging
import os

os.environ['API_TOKEN'] = '7356608678:AAGeOohOBkWXvVaZDYg7V0U7Y-l55PPVDt0'

import aiohttp
from aiogram import Bot, Dispatcher, executor, types
from gsheets import get_service, get_data, append_data, update_data, delete_data

import exceptions
import expenses
from categories import Categories
'''from middlewares import AccessMiddleware'''


logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("API_TOKEN")

if not API_TOKEN:
    raise ValueError("No API token provided")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

service = get_service()



@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """Отправляет приветственное сообщение и помощь по боту"""
    logging.info("Received /start or /help command")
    await message.answer(
        "Hello, I am your MControl Bot! What do you want to do today?\n\n"
        "Add Expenses: 250 Taxi\n"
        "Today's statistics: /today\n"
        "Current month's statistics: /month\n"
        "Last added expenses: /expenses\n"
        "Categories: /categories")

@dp.message_handler(commands=['data'])
async def send_data(message: types.Message):
    """Fetches and sends data from Google Sheets"""
    logging.info("Received /data command")
    data = get_data(service)
    response = "Data from Google Sheets:\n"
    for row in data:
        response += ", ".join(row) + "\n"
    await message.answer(response)

@dp.message_handler(lambda message: message.text.startswith('/add '))
async def add_data(message: types.Message):
    """Adds a new row to Google Sheets"""
    logging.info(f"Received add command: {message.text}")
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Usage: /add <name> <amount>")
        return
    name, amount = parts[1], parts[2]
    append_data(service, [[name, amount, 'expense']])
    await message.answer(f"Added {name} with amount {amount} to Google Sheets")

@dp.message_handler(lambda message: message.text.startswith('/del '))
async def del_expense(message: types.Message):
    """Удаляет одну запись о расходе по её идентификатору"""
    logging.info(f"Received delete command: {message.text}")
    try:
        row_id = int(message.text[5:])
        delete_data(service, f'Worksheet!A{row_id}:C{row_id}')
        answer_message = "Удалил"
    except ValueError:
        answer_message = "Неверный формат команды. Используйте /del <row_id>"
    await message.answer(answer_message)


@dp.message_handler(commands=['categories'])
async def categories_list(message: types.Message):
    """Отправляет список категорий расходов"""
    logging.info("Received /categories command")
    categories = Categories().get_all_categories()
    answer_message = "Категории трат:\n\n* " +\
            ("\n* ".join([c.name+' ('+", ".join(c.aliases)+')' for c in categories]))
    await message.answer(answer_message)


@dp.message_handler(commands=['today'])
async def today_statistics(message: types.Message):
    """Отправляет сегодняшнюю статистику трат"""
    logging.info("Received /today command")
    answer_message = expenses.get_today_statistics()
    await message.answer(answer_message)


@dp.message_handler(commands=['month'])
async def month_statistics(message: types.Message):
    """Отправляет статистику трат текущего месяца"""
    logging.info("Received /month command")
    answer_message = expenses.get_month_statistics()
    await message.answer(answer_message)


@dp.message_handler(commands=['expenses'])
async def list_expenses(message: types.Message):
    """Отправляет последние несколько записей о расходах"""
    logging.info("Received /expenses command")
    last_expenses = expenses.last()
    if not last_expenses:
        await message.answer("Расходы ещё не заведены")
        return

    last_expenses_rows = [
        f"{expense.amount} руб. на {expense.category_name} — нажми "
        f"/del{expense.id} для удаления"
        for expense in last_expenses]
    answer_message = "Последние сохранённые траты:\n\n* " + "\n\n* "\
            .join(last_expenses_rows)
    await message.answer(answer_message)


@dp.message_handler()
async def add_expense(message: types.Message):
    """Добавляет новый расход"""
    logging.info(f"Received message to add expense: {message.text}")
    try:
        expense = expenses.add_expense(message.text)
    except exceptions.NotCorrectMessage as e:
        logging.error(f"Error adding expense: {e}")
        await message.answer(str(e))
        return
    answer_message = (
        f"Добавлены траты {expense.amount} руб на {expense.category_name}.\n\n"
        f"{expenses.get_today_statistics()}")
    await message.answer(answer_message)


if __name__ == '__main__':
    logging.info("Starting bot...")
    executor.start_polling(dp, skip_updates=True)
