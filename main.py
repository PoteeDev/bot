from dataclasses import dataclass
from pathlib import Path
import yaml
from typing import List, Dict
from os.path import exists
import os
import telebot
from telebot import types
import json

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))
databaseAddress = os.getenv("DATABASE")
if not databaseAddress:
    print("Enviroment virable DATABASE in not defined")


@dataclass
class Buttons:
    text: str
    next: str


@dataclass
class Validate:
    key: str = ""
    wrong: str = ""
    rule: str = ""


@dataclass
class Message:
    message: str = ""
    attachment: str = ""
    write: str = ""
    next: str = ""
    validate: Validate = None
    wrong: str = ""
    buttons: List[Buttons] = None
    format: List[str] = None


class ValidateRules:
    def __init__(self) -> None:
        pass

    def team_rule(self, text, teams) -> int:
        if text in teams:
            return True
        else:
            return False


class Dialogs:
    def __init__(self, config="dialog.yml") -> None:
        self.config = Path(config)
        self.dialogs: Dict[str, Message] = dict()
        self.read_config()
        self.user_data = {}
        self.waiting_answer = {}
        self.rules = ValidateRules()

    def read_config(self) -> dict:
        if not os.path.exists(databaseAddress):
            self.make_json(databaseAddress, {})
        with self.config.open() as c:
            dialogs = yaml.safe_load(c.read())
            self.convert_config(dialogs)
            self.check_data()
            return self.dialogs

    def check_data(self):
        nexts = list()
        for name, message in self.dialogs.items():

            if not message.buttons and not message.attachment and not message.message:
                raise NameError(f"not any attachments to message in block: {name}")
            if message.buttons:
                for button in message.buttons:
                    if not button.text:
                        raise NameError(
                            "in block " + str(name) + " there is not any paceholder"
                        )
                    if not button.next:
                        raise NameError(
                            "in button block " + str(name) + " there is not any next"
                        )

                    if button.next not in self.dialogs:
                        raise NameError(
                            "in button block "
                            + str(name)
                            + " not existing next "
                            + str(button.text)
                        )
                nexts.append(name)
            if message.next:
                nexts.append(name)
                if message.next not in self.dialogs and not message.buttons:
                    raise NameError(
                        f"in block {name} next value {message.next} invalid"
                    )
            if message.attachment:
                if not exists(message.attachment):
                    raise NameError(
                        f"attachment '{message.attachment}' does not exist "
                    )
            # if message.validate:
            #     if not message.validate.key:
            #         raise NameError(
            #             f"message validate '{message}' does not have input what to validate "
            #         )
            #     if not message.validate.rule:
            #         raise NameError(
            #             f"message validate '{message}' does not have rule how to validate "
            #         )

        if len(nexts) + 1 != len(self.dialogs):
            raise NameError("count of next messages invalid")

    def convert_config(self, dialogs) -> List[Message]:
        for name, values in dialogs["dialogs"].items():
            if "buttons" in values:
                values["buttons"] = list(map(lambda x: Buttons(**x), values["buttons"]))
            if "validate" in values:
                values["validate"] = Validate(**values["validate"])
            self.dialogs[name] = Message(**values)
        return self.dialogs

    def _print_all_messages(self):
        for key, message in self.dialogs.items():
            if message.message:
                print(key, message.message, sep="\t")
            if message.buttons:
                print(message.buttons)

    def _print_sequence(self):
        message_key = list(self.dialogs.keys())[0]
        while True:
            message = self.dialogs[message_key]
            print(message.message)
            if not message.next:
                break

            if message.buttons:
                print(message.buttons)
                message_key = message.buttons[0].next
            else:
                message_key = message.next

    def generate_message(self, chat_id):
        message = self.dialogs[self.user_data[chat_id]["stage"]]
        args = {"chat_id": chat_id}
        if message.buttons:
            markup = types.ReplyKeyboardMarkup(
                resize_keyboard=True,
                one_time_keyboard=True,
            )
            for buttons in message.buttons:
                markup.add(buttons.text)
            args["reply_markup"] = markup
        if message.format and message.message:
            values = list(map(lambda x: self.user_data[chat_id][x], message.format))
            message.message = message.message.format(*values)
        if message.attachment:
            with open(message.attachment, "rb") as p:
                bot.send_photo(**args, photo=p, caption=message.message)
        else:
            bot.send_message(**args, text=message.message)
        self.make_json(databaseAddress, self.user_data)

    def change_state(self, chat_id, state):
        self.make_json(databaseAddress, self.user_data)
        if state not in self.dialogs:
            raise NameError("There is no such stage in dialogs, check config file :)")
        self.user_data[chat_id]["prev_stage"] = self.user_data[chat_id]["stage"]
        self.user_data[chat_id]["stage"] = state
        self.generate_message(chat_id)

    def make_json(self, name_file, massiv):
        with open(name_file, "w") as fw:
            json.dump(massiv, fw, indent=2, ensure_ascii=False)

    def load_json(self, name_file):
        with open(name_file, "r") as fr:
            return json.load(fr)

    def process_user(self, chat_id, text):
        self.user_data = self.load_json(databaseAddress)
        if chat_id not in self.user_data:
            self.user_data[chat_id] = {"stage": "hello"}
            self.generate_message(chat_id)
            return
        print(self.user_data)
        message = self.dialogs[self.user_data[chat_id]["stage"]]
        if message.validate:
            if message.validate.rule == "user_check":
                teams = []
                print(self.user_data)
                for _user in list(self.user_data):
                    print(self.user_data[_user])
                    if self.user_data[_user].get("entity"):
                        teams.append(self.user_data[_user].get("entity"))

                if not self.rules.team_rule(text, teams):
                    bot.send_message(chat_id, message.validate.wrong)
                else:
                    self.user_data[chat_id][message.write] = text
                    self.change_state(chat_id, message.next)
                    return
        if message.write:
            self.user_data[chat_id][message.write] = text

        if message.buttons:
            for button in message.buttons:
                if text == button.text:
                    self.change_state(chat_id, button.next)
                    return
            bot.send_message(chat_id, "попробуйте еще раз, используйте клавиатуру")

        if message.next:
            self.change_state(chat_id, message.next)


dialogs = Dialogs()


@bot.message_handler(content_types=["text"])
def get_text_messages(message):
    dialogs.process_user(str(message.from_user.id), message.text)
    print(message.from_user.id)


bot.polling(none_stop=True, interval=0)
