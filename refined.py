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
)

from aiogram.utils.keyboard import InlineKeyboardBuilder
from pymongo import MongoClient
