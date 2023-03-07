from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton



b_event = InlineKeyboardButton('Sign up for an event', callback_data='event')
b_consult = InlineKeyboardButton('Consultation', callback_data='consult')
b_mentor = InlineKeyboardButton('Mentoring', callback_data='mentor')
b_human = InlineKeyboardButton('Wanna speak with Hanna', callback_data='human')
b_discount = InlineKeyboardButton('Get discount', callback_data='discount')
b_main = InlineKeyboardButton('Start page 🚀', callback_data='main_menu')
b_cancel = InlineKeyboardButton('Cancel', callback_data='main_menu')
b_add_event = InlineKeyboardButton('Add new event (me only)', callback_data='add_event')
b_del_event = InlineKeyboardButton('Delete event (me only)', callback_data='del_event')
markup_cancel = InlineKeyboardMarkup(row_width=1).add(b_cancel)
markup_main = InlineKeyboardMarkup(row_width=1).add(b_main)