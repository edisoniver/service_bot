import asyncio
import logging

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import Message


#Job processing

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage


from aiogram.types import CallbackQuery


from pymongo import MongoClient


from random import randint
from aiogram.filters.callback_data import CallbackData
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
)

from aiogram.utils.keyboard import InlineKeyboardBuilder
from pymongo import MongoClient



class MenuCallback(CallbackData, prefix="my"):
    job_id: int

class JobPost(StatesGroup):
    name = State()  # Will be represented in storage as 'JobPost:name'
    price = State()  # Will be represented in storage as 'JobPost:price'
    description = State()  # Will be represented in storage as 'JobPost:description'

class PostJobCallbackData(CallbackData, prefix="Post"):
    answer: str


# Bot token can be obtained via https://t.me/BotFather
TOKEN = "5711704328:AAGxfN-riOFSxajQ2ZGoPaoZ4OwxuGvpZZE"

MONGODB_URI = 'mongodb+srv://PeopleService:PlutoniumSpeck12@telegrambot.wx5fzvy.mongodb.net/'

client = MongoClient('mongodb+srv://PeopleService:PlutoniumSpeck12@telegrambot.wx5fzvy.mongodb.net')
db = client['PeoplesService']  # Replace with your database name
jobs_collection = db['Jobs']  # Replace with your collection name

# All handlers should be attached to the Router (or Dispatcher)
router = Router()

# builder = InlineKeyboardBuilder()
# # Add five buttons with different fruits and prices
# builder.button(text="Apple - $0.5", callback_data=MyCallback(fruit="apple", price=0.5).pack())
# builder.button(text="Pear - $0.6", callback_data=MyCallback(fruit="pear", price=0.6).pack())
# builder.button(text="Mango - $1.2", callback_data=MyCallback(fruit="mango", price=1.2).pack())
# builder.button(text="Banana - $0.4", callback_data=MyCallback(fruit="banana", price=0.4).pack())
# builder.button(text="Pineapple - $1.5", callback_data=MyCallback(fruit="pineapple", price=1.5).pack())
# # Convert the keyboard builder into an actual InlineKeyboardMarkup object
# markup = builder.as_markup()








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

@router.message(Command(commands=["random"]))
async def command_random_handler(message: Message) -> None:
    """
    This handler receive messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.reply("Some text here", reply_markup=markup)


@router.message(Command(commands=["help"]))
async def command_help_handler(message: Message) -> None:
    """
    This handler receive messages with `/help` command
    This will display options for the user to select as BUTTONS and explain how the user will navigate.

    This will include the purpose of the applications and our mission statement.
    """

    await message.reply("Some text here", reply_markup=markup)




# menu_builder = InlineKeyboardBuilder()
# # Add five buttons with different fruits and prices
# menu_builder.button(text="Lawn Mowing", callback_data=MenuCallback(job_id=1).pack())
# menu_builder.button(text="Pool Cleaning", callback_data=MenuCallback(job_id=2).pack())
# menu_markup = menu_builder.as_markup()


async def create_menu():
    menu_builder = InlineKeyboardBuilder()

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



@router.message(Command(commands=["menu"]))
async def command_menu_handler(message: Message) -> None:
    """
    This handler receive messages with /menu command
    This will display options for the user to select as BUTTONS and will be
    the main navigation menu for the user.
    """

    menu_markup = await create_menu()
    await message.answer("Menu",reply_markup=menu_markup)


# def my_callback_filter(query: types.CallbackQuery):
#     callback_data = MyCallback.unpack(query.data)
#     return callback_data.fruit in ["apple", "pear", "mango", "banana", "pineapple"]

# MENU CALL BACK FUNCTIONS
def menu_callback_filter(query: types.CallbackQuery):
    callback_data = MenuCallback.unpack(query.data)
    return callback_data.job_id in [1,2]
#callback_data.job_name in ["20"],  callback_data.Price in ["20"],callback_data.Description in ["Unkept lawn need it mowed for inspection"]

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