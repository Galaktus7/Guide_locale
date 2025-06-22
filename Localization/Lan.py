from telebot import types
import json
import os
from Config import bot, Alex_id

# ========================== Отображаемые имена языков (с флагами) ==========================
language_display_names = {
    "русский": "🇷🇺Русский",
    "английский": "🇬🇧English",
    "украинский": "🇺🇦Українська",
}

# ========================== Локализация текстов из JSON ==========================

class LocalizedString:
    def __init__(self, key: str, format_queue=None):
        self.key = key
        self.__format_queue = format_queue or []

    def __str__(self):
        return self.localize()

    def localize(self, code: str = "ru"):
        string = translator.get_string(self.key, code)
        if string is None:
            string = self.key
        for fmt in self.__format_queue:
            string = fmt(string)
        return string

    def format(self, *args, **kwargs):
        def fmt(s): return s.format(*args, **kwargs)
        copy = LocalizedString(self.key, self.__format_queue.copy())
        copy.__format_queue.append(fmt)
        return copy

class Translator:
    def __init__(self, default_locale="ru"):
        self.locales = {}
        self.default_locale = default_locale

    def load_locale(self, code, root_dir):
        """
        Загружает все JSON-файлы из поддиректорий root_dir/ и складывает их в self.locales[code]
        """
        self.locales.setdefault(code, {})

        lang_dir = os.path.join(root_dir)
        for dirpath, _, filenames in os.walk(lang_dir):
            for filename in filenames:
                if filename.endswith(f"{code}.json"):
                    full_path = os.path.join(dirpath, filename)
                    try:
                        with open(full_path, encoding="utf-8") as f:
                            self.locales[code].update(json.load(f))
                    except Exception as e:
                        print(f"[Warning] Failed to load {full_path}: {e}")

    def get_string(self, key, code):
        return self.locales.get(code, {}).get(key)

# === Использование ===

translator = Translator()

LOCALE_DIR = "Localization"

# Загрузим все языки (можно автоматизировать)
for lang_code in ["ru", "en", "uk"]:
    translator.load_locale(lang_code, LOCALE_DIR)

user_language_preferences = {}
chat_language_preferences = {}


def lt(target_id: int, key: str, force_lang: str = None) -> str:
    if force_lang:
        code = force_lang
    else:
        lang = (chat_language_preferences.get(target_id, "русский")
                if target_id < 0 else
                user_language_preferences.get(target_id, "русский"))
        code = {"русский": "ru", "английский": "en", "украинский": "uk"}.get(lang, "ru")
    return LocalizedString(key).localize(code)


def localized_language_name(lang_key: str) -> str:
    return language_display_names.get(lang_key, language_display_names["русский"])

# ========================== Проверка админа ==========================


def is_user_admin(chat_id, user_id):
    if user_id == Alex_id:
        return True
    try:
        return bot.get_chat_member(chat_id, user_id).status in ("administrator", "creator")
    except:
        return False

# ========================== /admin_locale ==========================

@bot.message_handler(commands=["admin_locale"])
def admin_set_language(message):
    user_id = message.from_user.id

    if message.chat.type == "private":
        bot.reply_to(message, lt(user_id, "only_in_groups"))
        return

    chat_id = message.chat.id
    if not is_user_admin(chat_id, user_id):
        bot.reply_to(message, lt(user_id, "only_admin"))
        return

    current = chat_language_preferences.get(chat_id, "русский")

    # Строим inline-клавиатуру с флагами
    kb = types.InlineKeyboardMarkup()
    for key in ["русский", "английский", "украинский"]:
        kb.add(types.InlineKeyboardButton(
            text=localized_language_name(key),
            callback_data=f"adminset_{key}"
        ))

    # Текст заголовка локализуем по чату
    bot.reply_to(
        message,
        lt(chat_id, "current_group_language")
           .format(lang=localized_language_name(current)),
        reply_markup=kb
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("adminset_"))
def handle_admin_language_buttons(call):
    from Other_code.Core_project.Handlers import get_info_btn0, create_menu_keyboard

    chat_id = call.message.chat.id
    user_id  = call.from_user.id
    username = call.from_user.username or ""

    if not is_user_admin(chat_id, user_id):
        bot.answer_callback_query(call.id, lt(user_id, "only_admin"))
        return

    selected = call.data.split("_", 1)[1].lower()
    chat_language_preferences[chat_id] = selected

    # Подтверждение по чату
    bot.answer_callback_query(
        call.id,
        lt(chat_id, "group_language_set")
           .format(lang=localized_language_name(selected))
    )
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=lt(chat_id, "current_group_language_set").format(lang=localized_language_name(selected))
    )

    if selected == "украинский":
        bot.send_message(chat_id, lt(chat_id, "ua_gratitude"))

    # btn0
    text, kb2 = get_info_btn0(chat_id, username), create_menu_keyboard(chat_id)
    bot.send_message(chat_id, text, reply_markup=kb2)

# ========================== /set_l ==========================


@bot.message_handler(commands=["set_l"])
def set_language(message):
    if message.chat.type != "private":
        bot.reply_to(message, lt(message.chat.id, "private_only_language_change"))
        return

    user_id = message.from_user.id
    current = user_language_preferences.get(user_id, "русский")

    kb = types.InlineKeyboardMarkup()
    for key in ["русский", "английский", "украинский"]:
        kb.add(types.InlineKeyboardButton(
            text=localized_language_name(key),
            callback_data=key
        ))

    bot.send_message(
        user_id,
        lt(user_id, "current_user_language").format(lang=localized_language_name(current)),
        reply_markup=kb
    )


@bot.callback_query_handler(func=lambda call: call.data in ["русский", "английский", "украинский"])
def handle_language_buttons(call):
    from Other_code.Core_project.Handlers import get_info_btn0, create_menu_keyboard

    user_id = call.from_user.id
    username = call.from_user.username or ""
    selected = call.data.lower()

    user_language_preferences[user_id] = selected

    bot.answer_callback_query(
        call.id,
        lt(user_id, "language_set").format(lang=localized_language_name(selected))
    )
    bot.edit_message_text(
        chat_id=user_id,
        message_id=call.message.message_id,
        text=lt(user_id, "current_language_set").format(lang=localized_language_name(selected))
    )

    if selected == "украинский":
        bot.send_message(user_id, lt(user_id, "ua_gratitude"))

    # btn0
    text, kb2 = get_info_btn0(user_id, username), create_menu_keyboard(user_id)
    bot.send_message(user_id, text, reply_markup=kb2)