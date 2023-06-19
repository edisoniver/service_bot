import asyncio
import logging
from pymongo import MongoClient
from enum import Enum

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import Message

from magic_filter import F
from aiogram.filters import MagicData

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from aiogram.types import CallbackQuery

from random import randint
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.callback_answer import CallbackAnswer
from aiogram.types import (
    CallbackGame,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonPollType,
    LoginUrl,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)

from aiogram.utils.keyboard import InlineKeyboardBuilder


TOKEN = "6297179747:AAGoroCZy8Mr8zTR11SP7EVQk6AKcqHtz-k"

MONGODB_URI = 'mongodb+srv://PeopleService:PlutoniumSpeck12@telegrambot.wx5fzvy.mongodb.net/'

class MenuCallback(CallbackData, prefix="my"):
    job_id: int

class Action(str, Enum):
    post = "post"

class AdminAction(CallbackData, prefix="my"):
    action: Action







client = MongoClient('mongodb+srv://PeopleService:PlutoniumSpeck12@telegrambot.wx5fzvy.mongodb.net')
db = client['PeoplesService']  # Replace with your database name
jobs_collection = db['Jobs']  # Replace with your collection name

# All handlers should be attached to the Router (or Dispatcher)
router = Router()

@router.message(Command(commands=["start"]))
async def command_start_handler(message: Message) -> None:
    """
    This handler receive messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, <b>{message.from_user.full_name}!</b>")
    await message.answer(f"Welcome to a global service app. To get started, please do /help for more ")


@router.message(Command(commands=["menu"]))
async def command_menu_handler(message: Message) -> None:
    """
    This handler receive messages with /menu command
    This will display options for the user to select as BUTTONS and will be
    the main navigation menu for the user.
    """

    menu_markup = await create_menu()
    
    await message.answer("Menu",reply_markup=menu_markup)

async def create_menu():
    menu_builder = InlineKeyboardBuilder()

# Add 'Post a Job' button
    post_job_button = InlineKeyboardButton(text="Post a Job", callback_data=AdminAction(action=Action.post).pack())
    menu_builder.row(post_job_button)


    # Fetch jobs from database
    loop = asyncio.get_running_loop()
    cursor = await loop.run_in_executor(None, jobs_collection.find, {})
    jobs = [job for job in cursor]

    # Add buttons with job names and their IDs
    for job in jobs:
        button = InlineKeyboardButton(text=job["job_name"], callback_data=MenuCallback(job_id=job['job_id']).pack())
        price = InlineKeyboardButton(text=str(f"""${job["price"]}"""), callback_data=MenuCallback(job_id=job['job_id']).pack())
        menu_builder.row(button, price)
    menu_markup = menu_builder.as_markup()

    return menu_markup

@router.callback_query(MenuCallback.filter())
async def menu_callback_filter(query: types.CallbackQuery):
    print("MENU CALLBACK FILTER")
    callback_data = MenuCallback.unpack(query.data)
    return callback_data.job_id 


@router.callback_query(menu_callback_filter)
async def my_menu_handler(query: types.CallbackQuery):
    """
    This handler will respond with the fruit name and its price selected by the user.


    access MongoDB, match ID with database and query and filter information. 
    Output data here.
    """
    callback_data = MenuCallback.unpack(query.data) # This outputs JOB_ID.

    #Database query below

    x = jobs_collection.find_one({"job_id": int(callback_data.job_id)})

    price = x['price']
    job_name = x['job_name']
    description = x['job_description']
    location = x['location']


    await query.message.answer(f"""
JOBDETAILS: {job_name} ${price}
DESCRIPTION: {description}                      
LOCATION: {location}                               
""")
    

    await query.answer()


async def main() -> None:
    # Dispatcher is a root router
    storage = MemoryStorage()
    dp = Dispatcher()
    # ... and all other routers should be attached to Dispatcher
    dp.include_router(router)

    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode="HTML")
    # And the run events dispatching
    await dp.start_polling(bot)




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())