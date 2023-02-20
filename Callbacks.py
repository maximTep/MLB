import telebot
from Dialogues import Dialogues
from CallbackData import CallbackData


class Callbacks:
    def __init__(self, bot: telebot.TeleBot, dialogues: Dialogues):
        self.bot = bot
        self.dialogues = dialogues
        self.user_id = self.dialogues.user_id

    def __set_user_id__(self, user_id):
        self.user_id = user_id

    def main_callback(self, call):
        self.bot.answer_callback_query(call.id)
        # START
        if call.data == CallbackData.HOW_IT_WORKS:
            self.dialogues.how_it_works()
        elif call.data == CallbackData.MY_PROFILE:
            self.dialogues.my_profile()
        elif call.data == CallbackData.SEE_PEOPLE:
            self.dialogues.see_people()
        elif call.data == CallbackData.MY_MATCHES:
            self.dialogues.my_matches()
        elif call.data == CallbackData.ABOUT_CREATORS:
            self.dialogues.about_creators()
        elif call.data == CallbackData.DROP_PAIRS_AND_MATCHES:
            self.dialogues.drop_pairs_and_matches() #TODO TODO TODO TODO: DELETE!!!!!!!!!!!!!!!!!!!!!!!!!!
        elif call.data == CallbackData.TO_MAIN_MENU:
            self.dialogues.menu(self.dialogues.last_message)

        # REGISTER SEX
        elif call.data == CallbackData.SEX_MALE:
            self.dialogues.register_sex_end(False)
        elif call.data == CallbackData.SEX_FEMALE:
            self.dialogues.register_sex_end(True)

        # REGISTER PREFERABLES
        elif call.data == CallbackData.PREFERABLES_MALE:
            self.dialogues.register_preferables_end(True, False)
        elif call.data == CallbackData.PREFERABLES_FEMALE:
            self.dialogues.register_preferables_end(False, True)
        elif call.data == CallbackData.PREFERABLES_ALL:
            self.dialogues.register_preferables_end(True, True)

        # MY PROFILE
        elif call.data == CallbackData.EDIT_DESCRIPTION:
            self.dialogues.edit_description()
        elif call.data == CallbackData.EDIT_PHOTO:
            self.dialogues.edit_photo()
        elif call.data == CallbackData.EDIT_SEX:
            self.dialogues.edit_sex()
        elif call.data == CallbackData.EDIT_PREFERABLES:
            self.dialogues.edit_preferables()
        elif call.data == CallbackData.TO_MAIN_MENU:
            self.dialogues.menu(self.dialogues.last_message)

        # SEE PEOPLE
        elif call.data == CallbackData.LIKE:
            self.dialogues.see_people_decision(True)
        elif call.data == CallbackData.DISLIKE:
            self.dialogues.see_people_decision(False)
        elif call.data == CallbackData.TO_MAIN_MENU:
            self.dialogues.menu(self.dialogues.last_message)

        # TO MAIN MENU
        elif call.data == CallbackData.TO_MAIN_MENU:
            self.dialogues.menu(self.dialogues.last_message)
