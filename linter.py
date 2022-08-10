from dataclasses import dataclass
from pathlib import Path
import yaml
from typing import List, Dict
from os.path import exists


@dataclass
class Buttons:
    text: str = ""
    next: str = ""


@dataclass
class Message:
    message: str = ""
    attachment: str = ""
    write: str = ""
    next: str = ""
    validate: str = ""
    wrong: str = ""
    buttons: List[Buttons] = None
    format: List[str] = None


class Linter:
    def __init__(self, config="dialog.yml") -> None:
        self.config = Path(config)
        self.dialogs: Dict[str, Message] = dict()
        self.read_config()
        self.user_data = {}
        self.waiting_answer = {}

    def read_config(self) -> dict:
        with self.config.open() as c:
            dialogs = yaml.safe_load(c.read())
            self.convert_config(dialogs)
            return dialogs

    def convert_config(self, dialogs) -> List[Message]:
        for name, values in dialogs["dialogs"].items():
            if "buttons" in values:
                values["buttons"] = list(map(lambda x: Buttons(**x), values["buttons"]))
            self.dialogs[name] = Message(**values)
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

        if len(nexts) + 1 != len(self.dialogs):
            raise NameError("count of next messages invalid")


dialog_to_lint = Linter()

dialog_to_lint.lint_data()
