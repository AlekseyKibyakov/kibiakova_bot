
from aiogram import types
from aiogram.utils import executor
from buttons import b_consult, b_discount, b_event, b_human,\
    b_mentor, markup_main, markup_cancel, b_add_event, b_del_event
import db_interaction as db
from aiogram.dispatcher import FSMContext
from sqlalchemy.exc import DataError, PendingRollbackError
import re
from models import Event, User
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import settings
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

token = settings['TELEGRAM_TOKEN']
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form_user(StatesGroup):
    event = State()
    name = State()
    email = State()
    phone = State()

class Form_add_event(StatesGroup):
    title = State()
    date = State()
    

class Form_del_event(StatesGroup):
    title = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message): 
    await bot.send_video(message.from_user.id, 'BAACAgIAAxkBAAEd8epkAyWVtN5sFVOi_y5jOTxqYiyWJQACNCsAApyHGUgznH_o1v82qy4E', reply_markup=markup_main)


@dp.callback_query_handler(text='main_menu', state="*")
async def main_menu(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'This is Start Page!', reply_markup=types.ReplyKeyboardRemove())
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(b_consult, b_mentor, b_event, b_human, b_discount)
    if message.from_user.id == 6067195831 or message.from_user.username == '@hanna_kibia_coach':
        markup.add(b_add_event)
        markup.add(b_del_event)
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    
    #to do
    await bot.send_message(message.from_user.id, '*Start page info*', reply_markup=markup)
    

@dp.callback_query_handler(text='del_event')
async def delete_event(message: types.Message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Choose the event')
    for event in db.get_events_from_db():
        markup.add(types.KeyboardButton(event.title))
    await bot.send_message(message.from_user.id, 'Choose which event to delete.', reply_markup=markup)
    await Form_del_event.title.set()


@dp.message_handler(state=Form_del_event.title)
async def get_event_title(message: types.Message, state: FSMContext):
    
    db.delete_event(message.text)

    await state.finish()


@dp.callback_query_handler(text='add_event')
async def add_event(message: types.Message):
    await Form_add_event.title.set()
    await bot.send_message(message.from_user.id, 'What is the event`s title?')


@dp.message_handler(state=Form_add_event.title)
async def get_event_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text
    await Form_add_event.next()
    await bot.send_message(message.from_user.id, 'Enter the date of the event in year-month-date format (e.g. 2023-01-20).', reply_markup=markup_cancel)


@dp.message_handler(state=Form_add_event.date)
async def get_event_date(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['date'] = message.text
            event = Event(title=data['title'], date=data['date'])
            db.add_item_to_db(item=event)
            
            await message.reply(f"Event {data['title']} created.")
        await state.finish()
    except BaseException:
        db.close_session()
        await Form_add_event.date.set()
        await bot.send_message(message.from_user.id, 'You typed something wrong. Try again.', reply_markup=markup_cancel)


@dp.callback_query_handler(text='consult')
async def consult(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        #to do
        '*Consult info*',
        reply_markup=markup_main
    )
    

@dp.callback_query_handler(text='mentor')
async def mentor(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        '*Mentoring info*',
        reply_markup=markup_main
    )


@dp.callback_query_handler(text='human')
async def human(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        'Text me in Telegram: @example\n\
My phone number: 12345\n\
My e-mail: example@gmail.com', 
        reply_markup=markup_main
    )


@dp.callback_query_handler(text='discount')
async def discount(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        '*Discount*',
        reply_markup=markup_main
    )

        
@dp.callback_query_handler(text='event')
async def event(message: types.Message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Choose the event')
    for event in db.get_events_from_db():
        markup.add(types.KeyboardButton(event.title))
    await Form_user.event.set()
    await bot.send_message(message.from_user.id, 'Choose the event to sign up for', reply_markup=markup)

        
@dp.message_handler(state=Form_user.event)
async def get_event(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['event'] = message.text
    if db.update_user_events(message.from_user.id, data['event']):
        await state.finish()
        await bot.send_message(message.from_user.id, 'Done!')
    else:
        await Form_user.next()
        await bot.send_message(message.from_user.id, 'What`s your name? Send your name and surname.', reply_markup=markup_cancel)


@dp.message_handler(state=Form_user.name)
async def get_name(message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['first_name'] = message.text.split(' ')[1]
            data['last_name'] = message.text.split(' ')[0]
            await Form_user.next()
            await bot.send_message(message.from_user.id, 'Nice to meet you! Text your e-mail address.', reply_markup=markup_cancel)
    except BaseException:
        await Form_user.name.set()
        await bot.send_message(message.from_user.id, 'You typed something wrong. Try again.', reply_markup=markup_cancel)
    

async def _check_message(message, state: FSMContext):
    user_id = message.from_user.id
    _state = state.storage.data[f'{user_id}'][f'{user_id}']['state']
    if _state == 'Form_user:email':
        email_match = re.match(r'[\w0-9]{2,}\@+[\w]+\.{1}[\w]{2,}', message.text)
        return email_match
    elif _state == 'Form_user:phone':
        phone_match = re.match(r'\+?\d{8,}$', message.text)
        return phone_match


@dp.message_handler(state=Form_user.email)
async def get_email(message, state: FSMContext):
    if await _check_message(message, state):
        async with state.proxy() as data:
            data['email'] = message.text
            await Form_user.next()
            await bot.send_message(message.from_user.id, 'Nice! Last step, give me your phone number in format +1111111111', reply_markup=markup_cancel)
    else:
        await bot.send_message(message.from_user.id, 'You typed something wrong. Try again.', reply_markup=markup_cancel)
        await Form_user.email.set()
    
   
@dp.message_handler(state=Form_user.phone)
async def get_phone(message, state: FSMContext):
    if await _check_message(message, state):
        async with state.proxy() as data:
            data['phone'] = message.text
            user = User(
                tg_id=str(message.from_user.id),
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone=data['phone'],
            )
            for e in db.get_events_from_db():
                if e.title == data['event']:
                    event = e
                    break
            db.add_item_to_db(user, event)
            db.commit_session()
            db.close_session()
            await state.finish()
            await bot.send_message(message.from_user.id, 'Done!')
    else:
        await bot.send_message(message.from_user.id, 'You typed something wrong. Try again.', reply_markup=markup_cancel)
        await Form_user.phone.set()
    

if __name__ == '__main__':
    executor.start_polling(dp)