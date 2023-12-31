import asyncio
import logging
from enum import Enum

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import Message

from magic_filter import F
from aiogram.filters import MagicData


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
    ReplyKeyboardRemove
)

from aiogram.utils.keyboard import InlineKeyboardBuilder
from pymongo import MongoClient



class MenuCallback(CallbackData, prefix="my"):
    job_id: int

class Action(str, Enum):
    post = "post"

class AdminAction(CallbackData, prefix="my"):
    action: Action



class JobForm(StatesGroup):
    job_name = State()
    job_description = State()
    job_location = State()
    job_price = State()



# Bot token can be obtained via https://t.me/BotFather
TOKEN = "6297179747:AAGoroCZy8Mr8zTR11SP7EVQk6AKcqHtz-k"

MONGODB_URI = 'mongodb+srv://PeopleService:PlutoniumSpeck12@telegrambot.wx5fzvy.mongodb.net/'

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

async def create_post():
    postmenu_builder = InlineKeyboardBuilder()

# Add 'Post a Job' button
    postjob_button = InlineKeyboardButton(text="Post a Job", callback_data=.pack())
    postmenu_builder.row(postjob_button)

    postmenu_markup = postmenu_builder.as_markup()
    return postmenu_markup


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
async def command_menu_handler(message: Message):
    """
    This handler receive messages with /menu command
    This will display options for the user to select as BUTTONS and will be
    the main navigation menu for the user.
    """

    menu_markup = await create_menu()
    
    await message.answer("'''",reply_markup=menu_markup)
    

@router.message(Command(commands=["menu"]))
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


@router.message(Command("post"))
async def command_postjob(message: Message, state: FSMContext) -> None:
    await state.set_state(JobForm.job_name)
    postmenu_markup = await create_post()
    await message.answer(
        "Let's post a new job! What's the job name?", reply_markup=postmenu_markup
    )

@router.message(JobForm.job_name)
async def process_job_name(message: Message, state: FSMContext) -> None:
    await state.update_data(job_name=message.text)
    await state.set_state(JobForm.job_description)
    await message.answer("Great! What's the job description?")

@router.message(JobForm.job_description)
async def process_job_description(message: Message, state: FSMContext) -> None:
    await state.update_data(job_description=message.text)
    await state.set_state(JobForm.job_location)
    await message.answer("Alright. Where is the job located?")

@router.message(JobForm.job_location)
async def process_job_location(message: Message, state: FSMContext) -> None:
    await state.update_data(job_location=message.text)
    await state.set_state(JobForm.job_price)
    await message.answer("Fantastic. How much does the job pay?")

@router.message(JobForm.job_price)
async def process_job_price(message: Message, state: FSMContext) -> None:
    await state.update_data(job_price=message.text)
    data = await state.get_data()  # get all data from state context
    print(data)
    await state.clear()  # clear state context
    # Here you can add job data to database
    # jobs_collection.insert_one(data)
    await message.answer("Job successfully posted!")





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