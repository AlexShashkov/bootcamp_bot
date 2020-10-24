from vk_api.keyboard import VkKeyboard, VkKeyboardColor

#
# Главные блоки
#

class KeyBoard:
    def __init__(self, bot, db):
        self.keyboard = None
        self.calls = {}
        self.bot = bot
        self.db = db

    def checkCommand(self, event):
        """Проверить на наличие команды в своем списке"""
        call = event.obj.payload.get('type')
        if call in self.calls:
            self.calls[call](event)
            return True
        else:
            return False

    def setCurrentKeyboard(self, event, keyboard):
        """Установить клавиатуру в бд"""
        user_id = event.obj.user_id
        self.db.update("Students", "current_keyboard", f"'{keyboard}'", f"WHERE user_id='{user_id}'")
        self.db.connection.commit()

    def getMainMenuKeyboard(self, event):
        user_id = event.obj.user_id
        self.db.select("Students", "subscribed", f"WHERE user_id='{user_id}'")
        res = self.db.cursor.fetchone()

        if res != None:
            if res[0] == '1':
                return "main_uns_keyboard"
            else:
                return "main_sub_keyboard"
        else:
            self.bot.writeMsg(event.obj.user_id, "Пожалуйста, отправьте скриншот адмнистраторам.\nОшибка: у пользователя нет статуса о подписке")
            return "NULL"


class KeyboardMessage(KeyBoard):
    """Клавиатура-сообщение"""
    def __init__(self, bot, db):
        super().__init__(bot, db)
        settings = dict(one_time=False, inline=True)
        self.keyboard = VkKeyboard(**settings)


class KeyboardMain(KeyBoard):
    """Фиксированная клавиатура"""
    def __init__(self, bot, db):
        super().__init__(bot, db)
        settings = dict(one_time=False, inline=False)
        self.keyboard = VkKeyboard(**settings)

#
#  Главное меню
# 


class KeyboardMainMenu(KeyboardMain):
    """Главный блок для главного меню"""
    def __init__(self, bot, db):
        super().__init__(bot, db)
        self.calls = {
            "info_call" : self.infoCall,
            "notes_call" : self.notesCall,
            "game_call" : self.gameCall,
            "exit_call" : self.exitCall
        }

        self.name = None

        self.keyboard.add_callback_button(label='Мой профиль', color=VkKeyboardColor.SECONDARY, payload={"type": "info_call"})       #payload={"type": "show_snackbar", "text": "Ты лох"})
        self.keyboard.add_line()

    def infoCall(self, event):
        """Событие вызова профиля пользователя"""
        user_id = event.obj.user_id
        self.db.select("Students", "user_id", f"WHERE user_id='{user_id}'")
        res1 = self.db.cursor.fetchone()
        self.db.select("Students", "full_name", f"WHERE user_id='{user_id}'")
        res2 = self.db.cursor.fetchone()
        self.db.select("Students", "code", f"WHERE user_id='{user_id}'")
        res3 = self.db.cursor.fetchone()

        if res1 != None and res2 != None and res3 != None:
            text = f"""
id = {res1[0]}
Имя - {res2[0]}
Группа - {res3[0]}
"""
        print(text)
        self.bot.sendKeyboard(user_id, "inforamtion_edit_keyboard", text)
        self.bot.sendKeyboard(user_id, self.name)

    def notesCall(self, event):
        """Событие вызова записей пользователя"""
        user_id = event.obj.user_id
        self.bot.sendKeyboard(user_id, self.name, "Тут что-то будет про записи 🤔🤔🤔")

    def gameCall(self, event):
        """Событие вызова игры"""
        user_id = event.obj.user_id
        self.bot.sendKeyboard(user_id, "main_game_start", "Запускаю игру")
        self.setCurrentKeyboard(event, "main_game_start")

    def exitCall(self, event):
        """Выход пользователя из системы"""
        self.bot.sendKeyboard(event.obj.user_id, "main_login_keyboard", "Удачи! 🐉")
        self.setCurrentKeyboard(event, "main_login_keyboard")


class KeyboardMainMenuSub(KeyboardMainMenu):
    """Главное меню с подпиской"""
    def __init__(self, bot, db):
        super().__init__(bot, db)
        self.name = "main_sub_keyboard"
        self.calls["sub_call"] = self.subCall
        self.keyboard.add_callback_button(label='Подписаться на новости', color=VkKeyboardColor.POSITIVE, payload={"type" : "sub_call"})
        self.keyboard.add_line()
        self.keyboard.add_callback_button(label='Мои записи', color=VkKeyboardColor.PRIMARY, payload={"type": "notes_call"})
        self.keyboard.add_line()
        self.keyboard.add_callback_button(label='Мини игра', color=VkKeyboardColor.PRIMARY, payload={"type": "game_call"})
        self.keyboard.add_line()
        self.keyboard.add_openlink_button('Управление подписками на сообщения', 'https://vk.com/public199323686?w=app5898182_-199323686')
        self.keyboard.add_line()
        self.keyboard.add_callback_button(label='Выход', color=VkKeyboardColor.NEGATIVE, payload={"type": "exit_call"})

    def subCall(self, event):
        """Подписаться на новости"""
        self.db.update("Students", "subscribed", "'1'", f"WHERE user_id = '{event.obj.user_id}'")
        self.db.connection.commit()
        self.bot.sendKeyboard(event.obj.user_id, "main_uns_keyboard", "Вы подписались на новости группы")
        self.setCurrentKeyboard(event, "main_uns_keyboard")


class KeyboardMainMenuUnsub(KeyboardMainMenu):
    """Главное меню с отпиской"""
    def __init__(self, bot, db):
        super().__init__(bot, db)
        self.name = "main_uns_keyboard"
        self.calls["unsub_call"] = self.unsubCall
        self.keyboard.add_callback_button(label='Мои записи', color=VkKeyboardColor.PRIMARY, payload={"type": "notes_call"})
        self.keyboard.add_line()
        self.keyboard.add_callback_button(label='Мини игра', color=VkKeyboardColor.PRIMARY, payload={"type": "game_call"})
        self.keyboard.add_line()
        self.keyboard.add_callback_button(label='Отписаться от новостей', color=VkKeyboardColor.PRIMARY, payload={"type" : "unsub_call"})
        self.keyboard.add_line()
        self.keyboard.add_openlink_button('Управление подписками на сообщения', 'https://vk.com/public199323686?w=app5898182_-199323686')
        self.keyboard.add_line()
        self.keyboard.add_callback_button(label='Выход', color=VkKeyboardColor.NEGATIVE, payload={"type": "exit_call"})

    def unsubCall(self, event):
        """Отписаться от новостей"""
        self.db.update("Students", "subscribed", "'0'", f"WHERE user_id = '{event.obj.user_id}'")
        self.db.connection.commit()
        self.bot.sendKeyboard(event.obj.user_id, "main_sub_keyboard", "Вы отписались от новостей группы")
        self.setCurrentKeyboard(event, "main_sub_keyboard")


#
#   Игра
#

class GameKeyboardMenu(KeyboardMain):
    """Клавиатура для игры"""
    def __init__(self, bot, db, game):
        super().__init__(bot, db)

        self.calls = {
            "new_call" : self.newGameCall,
            "continue_call" : self.continueCall,
            "back_call" : self.backCall
        }

        self.game  = game
        self.name = "main_game_start"
        self.keyboard.add_callback_button(label='Новая игра', color=VkKeyboardColor.POSITIVE, payload={"type" : "new_call"})
        self.keyboard.add_line()
        self.keyboard.add_callback_button(label='Продолжить игру', color=VkKeyboardColor.PRIMARY, payload={"type": "continue_call"})
        self.keyboard.add_line()
        self.keyboard.add_callback_button(label='В меню', color=VkKeyboardColor.NEGATIVE, payload={"type": "back_call"})

    def newGameCall(self, event):
        """Событие новой игры"""
        user_id = event.obj.user_id
        self.bot.sendKeyboard(user_id, "main_game", "Начинаю игру")
        self.game.gameManager(user_id, "newgame")
        self.setCurrentKeyboard(event, "main_game")

    def continueCall(self, event):
        """Событие продолжения игры"""
        user_id = event.obj.user_id
        self.bot.sendKeyboard(user_id, "main_game_start", "Продолжаю игру")
        self.setCurrentKeyboard(event, "main_game_start")

    def backCall(self, event):
        """Событие возврата в меню"""
        user_id = event.obj.user_id
        keyboard = self.getMainMenuKeyboard(event)
        self.bot.sendKeyboard(user_id, keyboard, "Возвращаю в меню")
        self.setCurrentKeyboard(event, keyboard)


class GameKeyboard(KeyboardMain):
    """Клавиатура для игры"""
    def __init__(self, bot, db, game):
        super().__init__(bot, db)

        self.calls = {
            "forward_call" : self.forwardCall,
            "left_call" : self.leftCall,
            "right_call" : self.rightCall,
            "stay_call" : self.stayCall,
            "back_call" : self.backCall,
            "menu_call" : self.menuCall
        }

        self.game  = game
        self.name = "main_game"
        self.keyboard.add_callback_button(label='Вверх', color=VkKeyboardColor.POSITIVE, payload={"type" : "forward_call"})
        self.keyboard.add_line()
        self.keyboard.add_callback_button(label='Налево', color=VkKeyboardColor.PRIMARY, payload={"type": "left_call"})
        self.keyboard.add_callback_button(label='Направо', color=VkKeyboardColor.PRIMARY, payload={"type": "right_call"})
        self.keyboard.add_line()
        self.keyboard.add_callback_button(label='Вниз', color=VkKeyboardColor.POSITIVE, payload={"type": "back_call"})
        self.keyboard.add_line()
        self.keyboard.add_callback_button(label='Прислушаться', color=VkKeyboardColor.PRIMARY, payload={"type": "stay_call"})
        self.keyboard.add_line()
        self.keyboard.add_callback_button(label='В меню', color=VkKeyboardColor.NEGATIVE, payload={"type": "menu_call"})

    def forwardCall(self, event):
        user_id = event.obj.user_id
        self.bot.sendKeyboard(user_id, "main_game", "Идем вверх")
        self.game.gameManager(user_id, "move", "up")

    def leftCall(self, event):
        user_id = event.obj.user_id
        self.bot.sendKeyboard(user_id, "main_game", "Идем налево")
        self.game.gameManager(user_id, "move", "left")

    def rightCall(self, event):
        user_id = event.obj.user_id
        self.bot.sendKeyboard(user_id, "main_game", "Идем направо")
        self.game.gameManager(user_id, "move", "right")

    def stayCall(self, event):
        user_id = event.obj.user_id
        self.bot.sendKeyboard(user_id, "main_game", "Остаемся на месте")
        self.game.gameManager(user_id, "stay")

    def backCall(self, event):
        user_id = event.obj.user_id
        self.bot.sendKeyboard(user_id, "main_game", "Идем вниз")
        self.game.gameManager(user_id, "move", "down")

    def menuCall(self, event):
        user_id = event.obj.user_id
        self.bot.sendKeyboard(user_id, "main_game_start", "Возвращаю в меню")
        self.setCurrentKeyboard(event, "main_game_start")

#
# Авторизация
#

class KeyboardLogin(KeyboardMain):
    """Кнопка входа"""
    def __init__(self, bot, db):
        super().__init__(bot, db)
        self.name = "main_login_keyboard"
        self.calls = {
            "login_call" : self.loginCall,
        }
        self.keyboard.add_callback_button(label='Заполнить профиль', color=VkKeyboardColor.POSITIVE, payload={"type": "login_call"})

    def loginCall(self, event):
        """Событие вызова авторизации"""
        # NOTE: Лучше заменить на MINI APPS
        user_id = event.obj.user_id
        self.bot.writeMsg(user_id, "Поиск в базе")
        self.db.select("Students", "user_id", f"WHERE user_id='{user_id}' AND full_name IS NOT NULL")
        res = self.db.cursor.fetchone()
        print("наш ")
        print(res)
        if res == None:
            self.bot.writeMsg(user_id, "Для начала введи свое полное имя")
            self.db.insert("Pending", "user_id, act", f"'{user_id}', 'REGISTER_NAME'")
            self.db.connection.commit()
        else:
            keyboard = self.getMainMenuKeyboard(event)
            self.bot.sendKeyboard(user_id, keyboard, "Вы успешно авторизовались!")
            self.setCurrentKeyboard(event, keyboard)


#
#   Редактирование профиля
#


class KeyboardMainEditProfile(KeyboardMain):
    """Клавиатура с кнопками для редактирования профиля"""
    def __init__(self, bot, db):
        super().__init__(bot, db)
        self.name = "main_info_edit_keyboard"
        self.calls = {
            "info_edit_name_call" : self.editNameCall,
            "info_edit_group_call" : self.editGroupCall,
            "to_menu_call" : self.toMenuCall
        }
        self.keyboard.add_callback_button(label='Редактировать имя', color=VkKeyboardColor.PRIMARY , payload={"type": "info_edit_name_call"})
        self.keyboard.add_line()
        self.keyboard.add_callback_button(label='Редактировать группу', color=VkKeyboardColor.PRIMARY , payload={"type": "info_edit_group_call"})
        self.keyboard.add_line()
        self.keyboard.add_callback_button(label='В меню', color=VkKeyboardColor.PRIMARY , payload={"type": "to_menu_call"})

    def editNameCall(self, event):
        """Редактирование имени пользователя"""
        self.bot.sendKeyboard(event.obj.user_id, "cancel_keyboard", "Введи свое полное имя")
        self.db.update("Pending", "act", "'EDIT_NAME'", f"WHERE user_id = '{event.obj.user_id}'")
        self.db.connection.commit()

    def editGroupCall(self, event):
        """Редактирование группы пользователя"""
        self.bot.sendKeyboard(event.obj.user_id, "cancel_keyboard", "Введи шифр группы")
        self.db.update("Pending", "act", "'EDIT_CODE'", f"WHERE user_id = '{event.obj.user_id}'")
        self.db.connection.commit()

    def toMenuCall(self, event):
        keyboard = self.getMainMenuKeyboard(event)
        self.bot.sendKeyboard(event.obj.user_id, keyboard)
        self.setCurrentKeyboard(event, keyboard)



#
# Побочные кнопки в виде сообщений
# NOTE: Так как можно привязать только одну ГЛАВНУЮ клавиатуру,
# Функции для кнопок сообщений будут реализованы в классе 
# ButtonHandler
#


class KeyboardEditProfile(KeyboardMessage):
    def __init__(self, bot, db):
        super().__init__(bot, db)
        self.keyboard.add_callback_button(label='Редактировать профиль 📝', color=VkKeyboardColor.PRIMARY, payload={"type": "info_edit_call"})

class CancelLastInput(KeyboardMessage):
    def __init__(self, bot, db):
        super().__init__(bot, db)
        self.keyboard.add_callback_button(label='Отменить', color=VkKeyboardColor.NEGATIVE, payload={"type": "cancel_call", "exception": "1"})