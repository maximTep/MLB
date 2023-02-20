import telebot
from telebot import types
from datetime import datetime
import re
import Texts
from DataBase import DataBase
from CallbackData import CallbackData
from Suggestions import Suggestions


class Dialogues:
    def __init__(self, bot: telebot.TeleBot, database: DataBase, user_id):
        self.bot = bot
        self.database = database
        self.user_id = user_id
        self.last_message: telebot.types.Message
        self.last_pair_id: int
        self.suggestions: Suggestions = Suggestions(self.user_id, self.database)

    def __set_last_message__(self, last_message: telebot.types.Message):
        self.last_message = last_message

    def __set_user_id__(self, user_id):
        self.user_id = user_id

    def __is_start__(self, message: telebot.types.Message):
        self.__set_last_message__(message)
        if message.text == "/start":
            self.start(message)
            return True
        return False

    def first_handler(self, message: telebot.types.Message):
        self.__set_last_message__(message)
        if message.text == "/start":
            if message.from_user.username is None:
                self.bot.send_message(self.user_id, Texts.has_no_tg_username_msg)
                return
            self.database.add_user({"user_tg_id": self.user_id})
            self.database.update_user_tg_username(self.user_id, message.from_user.username)
            self.start(message)
        elif str(message.chat.id) == Texts.admin_chat_id:
            if message.text is not None and message.text[0:3] == '/bc':
                self.broadcast(message)
            elif message.caption is not None and message.caption[0:3] == '/bc':
                self.broadcast(message)
            else:
                self.bot.send_message(self.user_id, Texts.idle_msg)
        else:
            self.bot.send_message(self.user_id, Texts.idle_msg)

    def broadcast(self, message: telebot.types.Message):
        if str(message.chat.id) != Texts.admin_chat_id:
            self.bot.send_message(self.user_id, Texts.idle_msg)
            return
        ids = self.database.get_users_ids()
        if message.photo is None:
            text = message.text[3::]
            for id in ids:
                try:
                    self.bot.send_message(id, text)
                except:
                    pass
        elif len(message.photo) == 4:
            text = message.caption[3::]
            photo = message.photo[-1].file_id
            for id in ids:
                try:
                    self.bot.send_photo(id, photo, text)
                except:
                    pass
        else:
            pass

    def start(self, message: telebot.types.Message):
        self.bot.clear_step_handler(message)
        self.__set_last_message__(message)

        self.bot.send_message(self.user_id, text=Texts.hello_msg, parse_mode="HTML")
        if self.database.is_user_registered(self.user_id):
            self.menu(message)
        else:
            self.register()

    def register(self):
        self.bot.send_message(self.user_id, text=Texts.register_msg)
        self.ask_register_description()
        
    def ask_register_description(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text=Texts.to_main_menu_btn,
                callback_data=CallbackData.TO_MAIN_MENU
            ),
        )
        if self.database.is_user_registered(self.user_id):
            self.bot.send_message(self.user_id, text=Texts.ask_description_msg, reply_markup=keyboard)
        else:
            self.bot.send_message(self.user_id, text=Texts.ask_description_msg)
        self.bot.register_next_step_handler(self.last_message, self.accept_register_description)

    def accept_register_description(self, message: telebot.types.Message):
        if self.__is_start__(message):
            return
        self.__set_last_message__(message)

        description = message.text
        if len(description) > 1024:
            self.bot.send_message(self.user_id, text=Texts.description_declined_msg)
            self.bot.register_next_step_handler(self.last_message, self.accept_register_description)
            return
        self.database.update_user_description(self.user_id, description)
        self.bot.send_message(self.user_id, text=Texts.description_accepted_msg)
        if not self.database.is_user_registered(self.user_id):
            self.ask_register_photo()
        else:
            self.menu(self.last_message)

    def ask_register_photo(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text=Texts.to_main_menu_btn,
                callback_data=CallbackData.TO_MAIN_MENU
            ),
        )
        if self.database.is_user_registered(self.user_id):
            self.bot.send_message(self.user_id, text=Texts.ask_photo_msg, reply_markup=keyboard)
        else:
            self.bot.send_message(self.user_id, text=Texts.ask_photo_msg)
        self.bot.register_next_step_handler(self.last_message, self.accept_register_photo)

    def accept_register_photo(self, message):
        if self.__is_start__(message): return
        self.__set_last_message__(message)

        try:
            file_info = self.bot.get_file(message.photo[-1].file_id)
            photo = self.bot.download_file(file_info.file_path)
            src_photo = f'Photos/' + f'{self.user_id}.jpeg'
            with open(src_photo, 'wb') as new_file:
                new_file.write(photo)
        except Exception:
            self.bot.send_message(self.user_id, text=Texts.photo_declined_msg)
            self.bot.register_next_step_handler(self.last_message, self.accept_register_photo)
            return
        self.bot.send_message(self.user_id, text=Texts.photo_accepted_msg)
        if not self.database.is_user_registered(self.user_id):
            self.register_sex()
        else:
            self.menu(self.last_message)

    def register_sex(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text=Texts.sex_male,
                callback_data=CallbackData.SEX_MALE
            ),
            types.InlineKeyboardButton(
                text=Texts.sex_female,
                callback_data=CallbackData.SEX_FEMALE
            ),
        )
        self.bot.send_message(self.user_id, text=Texts.sex_msg, reply_markup=keyboard)

    def register_sex_end(self, is_female: bool):
        self.database.update_user_sex(self.user_id, is_female)
        if not self.database.is_user_registered(self.user_id):
            self.register_preferables()
        else:
            self.menu(self.last_message)
        
    def register_preferables(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text=Texts.preferables_male_btn,
                callback_data=CallbackData.PREFERABLES_MALE
            ),
            types.InlineKeyboardButton(
                text=Texts.preferables_female_btn,
                callback_data=CallbackData.PREFERABLES_FEMALE
            ),
            types.InlineKeyboardButton(
                text=Texts.preferables_all_btn,
                callback_data=CallbackData.PREFERABLES_ALL
            ),
        )
        self.bot.send_message(self.user_id, text=Texts.preferables_msg, reply_markup=keyboard)

    def register_preferables_end(self, is_finds_male: bool, is_finds_female: bool):
        self.database.update_user_preferables(self.user_id, is_finds_male, is_finds_female)
        self.suggestions.clear_suggestions()
        if not self.database.is_user_registered(self.user_id):
            self.end_register()
        else:
            self.menu(self.last_message)

    def end_register(self):
        self.database.register_user(self.user_id)
        self.bot.send_message(self.user_id, text=Texts.register_ended_msg)
        self.menu(self.last_message)

    def menu(self, message: telebot.types.Message):
        self.bot.clear_step_handler(message)
        self.__set_last_message__(message)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text=Texts.my_profie_btn,
                callback_data=CallbackData.MY_PROFILE
            ),
            types.InlineKeyboardButton(
                text=Texts.see_people_btn,
                callback_data=CallbackData.SEE_PEOPLE
            ),
            types.InlineKeyboardButton(
                text=Texts.my_matches_btn,
                callback_data=CallbackData.MY_MATCHES
            ),
            types.InlineKeyboardButton(
                text=Texts.how_it_works_btn,
                callback_data=CallbackData.HOW_IT_WORKS
            ),
            types.InlineKeyboardButton(
                text=Texts.about_creators_btn,
                callback_data=CallbackData.ABOUT_CREATORS
            ),
            # types.InlineKeyboardButton(
            #     text="Drop pairs and matches",
            #     callback_data=CallbackData.DROP_PAIRS_AND_MATCHES
            # ),
            row_width=1
        )
        self.bot.send_message(self.user_id, text=Texts.menu_msg, reply_markup=keyboard)

    def drop_pairs_and_matches(self): # TODO TODO TODO TODO DELETE!!!!!!!!
        if self.user_id == 438007761:
            self.database.drop_pairs_and_matches()

    def my_profile(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text=Texts.edit_description_btn,
                callback_data=CallbackData.EDIT_DESCRIPTION
            ),
            types.InlineKeyboardButton(
                text=Texts.edit_photo_btn,
                callback_data=CallbackData.EDIT_PHOTO
            ),
            types.InlineKeyboardButton(
                text=Texts.edit_sex_btn,
                callback_data=CallbackData.EDIT_SEX
            ),
            types.InlineKeyboardButton(
                text=Texts.edit_preferables_btn,
                callback_data=CallbackData.EDIT_PREFERABLES
            ),
            types.InlineKeyboardButton(
                text=Texts.to_main_menu_btn,
                callback_data=CallbackData.TO_MAIN_MENU
            ),
            row_width=1
        )
        user_description = self.database.get_user_description(self.user_id)
        with open(f"Photos/{self.user_id}.jpeg", "rb") as user_photo:
                self.bot.send_photo(self.user_id, user_photo, caption=user_description, reply_markup=keyboard)

    def edit_description(self):
        self.ask_register_description()

    def edit_photo(self):
        self.ask_register_photo()
    
    def edit_sex(self):
        self.register_sex()
    
    def edit_preferables(self):
        self.register_preferables()

    def see_people(self):
        if not self.database.is_user_enabled(self.user_id):
            self.bot.send_message(self.user_id, text=Texts.ban_msg)
        else:
            self.see_people_step()

    def see_people_step(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text=Texts.like_btn,
                callback_data=CallbackData.LIKE
            ),
            types.InlineKeyboardButton(
                text=Texts.dislike_btn,
                callback_data=CallbackData.DISLIKE
            ),
            types.InlineKeyboardButton(
                text=Texts.to_main_menu_btn,
                callback_data=CallbackData.TO_MAIN_MENU
            ),
        )
        # pair_id = self.suggestions.get_pair_suggestion_id()
        pair_id = self.database.__get_pair_suggestion_id_deprecated__(self.user_id)
        if pair_id is None:
            self.see_people_end()
            return
        self.last_pair_id = pair_id
        pair_description = self.database.get_user_description(pair_id)
        with open(f"Photos/{pair_id}.jpeg", "rb") as pair_photo:
            self.bot.send_photo(self.user_id, pair_photo, caption=pair_description, reply_markup=keyboard)

    def see_people_decision(self, is_liked: bool):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text=Texts.see_people_next,
                callback_data=CallbackData.SEE_PEOPLE
            ),
            types.InlineKeyboardButton(
                text=Texts.to_main_menu_btn,
                callback_data=CallbackData.TO_MAIN_MENU
            ),
        )
        self.database.add_pair_or_update(self.user_id, self.last_pair_id, is_liked)
        is_liked_reverse = self.database.is_user_likes_observable(self.last_pair_id, self.user_id)
        is_match_exists = (self.database.is_match_exists(self.user_id, self.last_pair_id)
                           or self.database.is_match_exists(self.last_pair_id, self.user_id))
        if not is_liked_reverse or not is_liked or is_match_exists:
            self.see_people_step()
        else:
            self.database.add_match(self.last_pair_id, self.user_id)
            self.bot.send_message(self.user_id, text=Texts.match_msg)
            self.bot.send_message(self.last_pair_id, text=Texts.match_msg)
            pair_description = self.database.get_user_description(self.last_pair_id)
            user_description = self.database.get_user_description(self.user_id)
            with open(f"Photos/{self.last_pair_id}.jpeg", "rb") as pair_photo:
                self.bot.send_photo(self.user_id, pair_photo, caption=pair_description)
            with open(f"Photos/{self.user_id}.jpeg", "rb") as user_photo:
                self.bot.send_photo(self.last_pair_id, user_photo, caption=user_description)
            pair_tg_username = self.database.get_user_tg_username(self.last_pair_id)
            user_tg_username = self.database.get_user_tg_username(self.user_id)
            self.bot.send_message(self.user_id, text=f"@{pair_tg_username}", reply_markup=keyboard)
            self.bot.send_message(self.last_pair_id, text=f"@{user_tg_username}", reply_markup=keyboard)
            
    def see_people_end(self):
        self.bot.send_message(self.user_id, text=Texts.see_people_end_msg)
        self.menu(self.last_message)

    def my_matches(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text=Texts.to_main_menu_btn,
                callback_data=CallbackData.TO_MAIN_MENU
            ),
        )
        matches_tg_user_names = self.database.get_user_matches_tg_user_names(self.user_id)
        msg_text = Texts.my_matches
        for match_tg_user_name in matches_tg_user_names:
            msg_text += "\n@" + match_tg_user_name
        self.bot.send_message(self.user_id, text=msg_text, reply_markup=keyboard)

    def how_it_works(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text=Texts.to_main_menu_btn,
                callback_data=CallbackData.TO_MAIN_MENU
            ),
        )
        self.bot.send_message(self.user_id, text=Texts.how_it_works_msg, reply_markup=keyboard)
    
    def about_creators(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text=Texts.to_main_menu_btn,
                callback_data=CallbackData.TO_MAIN_MENU
            ),
        )
        self.bot.send_message(self.user_id, text=Texts.about_creators_msg, reply_markup=keyboard)
    