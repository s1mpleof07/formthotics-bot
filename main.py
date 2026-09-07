"""
Formthotics Ukraine — Telegram Bot для партнерів-лікарів
Запуск: pip install python-telegram-bot --break-system-packages && python3 bot.py
"""

import logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup,
    ReplyKeyboardRemove, KeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters
)

# ── CONFIG ────────────────────────────────────────────
BOT_TOKEN = "8949754941:AAGA4E5gl6ZZCUoOd94p3P-bKUrnNXxS_UA"
MANAGER_CHAT_ID = 642551073

# Course info
COURSE_DATE = "19–20 вересня 2026"
COURSE_CITY = "Уточнюється"
COURSE_LECTURER = "Дмитро Кущик"

# ── LOGGING ───────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ── CONVERSATION STATES ──────────────────────────────
(REG_NAME, REG_PHONE, REG_CITY, REG_SPEC, REG_CONFIRM,
 CONTACT_MSG) = range(6)

# ── USER STORAGE (in-memory) ─────────────────────────
users = {}  # chat_id -> {name, phone, city, spec, registered_at}

# ── SPECIALIZATIONS ──────────────────────────────────
SPECS = [
    "Ортопед / травматолог",
    "Реабілітолог",
    "Фізичний терапевт",
    "Подолог",
    "Кінезіолог / остеопат",
    "Педіатр / дитячий ортопед",
    "Інша спеціалізація"
]

# ═════════════════════════════════════════════════════
# MAIN MENU
# ═════════════════════════════════════════════════════

def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Про систему Formthotics", callback_data="about")],
        [InlineKeyboardButton("Курси та навчання", callback_data="courses")],
        [InlineKeyboardButton("Матеріали для лікарів", callback_data="materials")],
        [InlineKeyboardButton("Записатись на курс", callback_data="register")],
        [InlineKeyboardButton("Зв'язок з менеджером", callback_data="contact")],
    ])

WELCOME_TEXT = """Вітаємо у Formthotics Ukraine!

Ми — офіційний дистриб'ютор Formthotics в Україні. Клінічно доведена система індивідуального ортезування стопи з Нової Зеландії.

Цей бот допоможе вам:
— Дізнатись про систему та моделі устілок
— Переглянути корисні матеріали і відео
— Записатись на сертифікований курс
— Зв'язатись з менеджером

Оберіть що вас цікавить:"""

async def start(update: Update, context):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Save user
    if chat_id not in users:
        users[chat_id] = {"first_name": user.first_name, "username": user.username}
    
    # Notify manager about new user
    try:
        await context.bot.send_message(
            MANAGER_CHAT_ID,
            f"👤 Новий користувач бота:\n"
            f"Ім'я: {user.first_name} {user.last_name or ''}\n"
            f"Username: @{user.username or 'немає'}\n"
            f"ID: {chat_id}"
        )
    except:
        pass
    
    await update.message.reply_text(WELCOME_TEXT, reply_markup=main_menu_kb())

async def menu(update: Update, context):
    await update.message.reply_text("Головне меню:", reply_markup=main_menu_kb())

# ═════════════════════════════════════════════════════
# ABOUT SYSTEM
# ═════════════════════════════════════════════════════

async def about(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Що таке Formthotics", callback_data="about_what")],
        [InlineKeyboardButton("Як працює система", callback_data="about_how")],
        [InlineKeyboardButton("Моделі устілок", callback_data="about_models")],
        [InlineKeyboardButton("Покази до ортезування", callback_data="about_indications")],
        [InlineKeyboardButton("Переваги для лікаря", callback_data="about_benefits")],
        [InlineKeyboardButton("« Головне меню", callback_data="back_main")],
    ])
    
    await query.edit_message_text(
        "Про систему Formthotics\n\nОберіть розділ:",
        reply_markup=kb
    )

async def about_what(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    text = """Що таке Formthotics

Formthotics — це медична система індивідуального ортезування стопи від Foot Science International (Нова Зеландія).

На відміну від стандартних устілок з аптеки, Formthotics формується безпосередньо на стопі пацієнта прямо у кабінеті лікаря за 20 хвилин.

Матеріал Formax при нагріванні до 85°C набуває пластичності і точно запам'ятовує форму стопи — як відбиток. Кожна пара унікальна.

Ключові факти:
— 40+ років клінічних досліджень
— 30+ країн використовують систему
— 100+ партнерів-лікарів в Україні
— 95% лікарів продовжують замовляти постійно
— 15 моделей устілок під будь-який діагноз"""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Як працює система", callback_data="about_how")],
        [InlineKeyboardButton("Записатись на курс", callback_data="register")],
        [InlineKeyboardButton("« Про систему", callback_data="about")],
    ])
    
    await query.edit_message_text(text, reply_markup=kb)

async def about_how(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    text = """Як працює система — 6 кроків

1. Діагностика (10 хв)
Візуальна оцінка постави і ходи з подоскопом. 6 функціональних тестів: біомеханічний, міофасціальний, неврологічний аспекти.

2. Підбір моделі (5 хв)
Модель підбирається під ступінь деформації, тип взуття, вік, вагу та активність пацієнта.

3. Формування (15 хв)
Заготівка розігрівається до 85°C. Матеріал Formax набуває пластичності і формується прямо на стопі.

4. Корекція (повторний візит)
Оцінюється хода і постава. За потреби — корекція функціональними клинами.

5. Перевірка у взутті
Ефективність оцінюється коли пацієнт взутий.

6. Результат (1-7 днів)
Пацієнт відчуває полегшення. Рекомендований термін експлуатації 1-2 роки — залежно від інтенсивності використання.

Весь цикл — 20-40 хвилин у вашому кабінеті."""

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Моделі устілок", callback_data="about_models")],
        [InlineKeyboardButton("Записатись на курс", callback_data="register")],
        [InlineKeyboardButton("« Про систему", callback_data="about")],
    ])
    
    await query.edit_message_text(text, reply_markup=kb)

async def about_models(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    text = """Модельний ряд Formthotics — 15 моделей

Кожен колір = рівень жорсткості і призначення:

Рожева — м'яка, тонка. Модельне взуття, перші користувачі. Больовий синдром, артрит.

Бежева — пружна. Максимальний ефект при мінімальному об'ємі у взутті.

Шок-стоп (пісочно-чорна) — двошарова. Діабетична стопа, шпора, подагра, переломи.

Червоно-блакитна — середня жорсткість. Перевантаження ОРА, бігуни.

Блакитна — ковзани, лижі, жорстке спортивне взуття.

Чорно-бежева — перфорація. Фітнес, гіпергідроз стопи.

Зелена — вузьке модельне взуття.

Рожево-червона — вага 80+ кг, інтенсивний спорт.

Червона — найжорсткіша. Максимальні навантаження.

Junior / Uni — дитячі від 2 років. Вальгус, плоскостопість у дітей.

3/4 Комфорт — для вузького і відкритого взуття, бутс."""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Покази до ортезування", callback_data="about_indications")],
        [InlineKeyboardButton("Записатись на курс", callback_data="register")],
        [InlineKeyboardButton("« Про систему", callback_data="about")],
    ])
    
    await query.edit_message_text(text, reply_markup=kb)

async def about_indications(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    text = """Покази до ортезування

Стопа і гомілка:
— Плоскостопість (поздовжня, поперечна)
— Вальгусна деформація п'яти
— П'яткова шпора / підошовний фасциїт
— Неврома Мортона
— Тендовагініт ахіллового сухожилля
— Натоптиші і сухі мозолі

Суглоби та хребет:
— Болі в колінних і кульшових суглобах
— Болі в попереку і крижах
— Перекіс тазу, грижі дисків
— Сколіоз, порушення постави і ходи

Особливі групи:
— Діти від 2 років (вальгус, плоскостопість)
— Спортсмени (всі рівні навантажень)
— Діабетична стопа (профілактика)
— Вагітність (набряки, плоскостопість)
— Реабілітація після травм і операцій
— Мінно-вибухові поранення стопи"""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Переваги для лікаря", callback_data="about_benefits")],
        [InlineKeyboardButton("Записатись на курс", callback_data="register")],
        [InlineKeyboardButton("« Про систему", callback_data="about")],
    ])
    
    await query.edit_message_text(text, reply_markup=kb)

async def about_benefits(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    text = """Переваги для лікаря-партнера

Готовий протокол
Покроковий алгоритм від діагностики до корекції. Працюєте з першого дня після навчання.

Прозора фінансова модель
Закупка 2 600 грн, продаж від 6 000 грн. Прибуток від 3 400 грн з кожної пари. Без прихованих витрат.

Лояльні пацієнти
Задоволений пацієнт повертається і рекомендує. Зміцнює вашу репутацію як спеціаліста.

Навчання і сертифікат
2-денний сертифікований тренінг. Сертифікат спеціаліста Formthotics.

Розтермінування обладнання
Сушка ~$600 — 3 рівних платежі. Покриваєте з перших пар.

Підтримка
Telegram-чат партнерів, консультації по складних випадках, маркетингові матеріали."""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Записатись на курс", callback_data="register")],
        [InlineKeyboardButton("Зв'язок з менеджером", callback_data="contact")],
        [InlineKeyboardButton("« Про систему", callback_data="about")],
    ])
    
    await query.edit_message_text(text, reply_markup=kb)

# ═════════════════════════════════════════════════════
# COURSES
# ═════════════════════════════════════════════════════

async def courses(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    text = f"""Курси та навчання

Найближчий курс:
{COURSE_DATE}
Лектор: {COURSE_LECTURER}
Формат: офлайн, 2 дні, практика

Дмитро Кущик — кінезіолог, засновник Школи функціональної кінезіології, автор методики роботи з м'язово-фасціальними ланцюгами.

Після навчання — сертифікат спеціаліста і готовий протокол для роботи з першого дня.

Місця обмежені."""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Програма курсу", callback_data="course_program")],
        [InlineKeyboardButton("Записатись на курс", callback_data="register")],
        [InlineKeyboardButton("Зв'язок з менеджером", callback_data="contact")],
        [InlineKeyboardButton("« Головне меню", callback_data="back_main")],
    ])
    
    await query.edit_message_text(text, reply_markup=kb)

async def course_program(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    text = f"""Програма курсу {COURSE_DATE}

День перший — Теорія + практика:
01. Будова стопи та її розвиток
02. Анатомія та функція м'язів стопи
03. Стопа в статиці та патерні кроку
04. Візуальна діагностика дисфункцій
05. 6 функціональних тестів
06. Практика діагностики на учасниках

День другий — Клініка + ортезування:
07. Найпоширеніші проблеми стопи
08. Покази до ортезування
09. Коли устілка не потрібна?
10. Вплив ортезів на здоров'я
11. Підбір, формування і корекція ортезів
12. Адаптація сформованих ортезів

Лектор: {COURSE_LECTURER}
Сертифікат спеціаліста після завершення."""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Записатись на курс", callback_data="register")],
        [InlineKeyboardButton("« Курси", callback_data="courses")],
    ])
    
    await query.edit_message_text(text, reply_markup=kb)

# ═════════════════════════════════════════════════════
# MATERIALS
# ═════════════════════════════════════════════════════

async def materials(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Відео: Чому стандартна устілка не лікує", callback_data="mat_video1")],
        [InlineKeyboardButton("Відео: 6 функціональних тестів", callback_data="mat_video2")],
        [InlineKeyboardButton("Відео: Що відчуває пацієнт", callback_data="mat_video3")],
        [InlineKeyboardButton("Презентація системи", callback_data="mat_pres")],
        [InlineKeyboardButton("Сайт formthotics.com.ua", callback_data="mat_site")],
        [InlineKeyboardButton("« Головне меню", callback_data="back_main")],
    ])
    
    await query.edit_message_text(
        "Корисні матеріали для лікарів\n\nОберіть що вас цікавить:",
        reply_markup=kb
    )

async def mat_video(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    videos = {
        "mat_video1": {
            "title": "Чому стандартна устілка не лікує",
            "desc": "Дмитро Кущик пояснює різницю між стандартною устілкою і системою Formthotics. Чому один підхід маскує симптом, а інший усуває причину.",
        },
        "mat_video2": {
            "title": "6 функціональних тестів",
            "desc": "Як за 3 хвилини оцінити стан всього опорно-рухового апарату пацієнта через стопу. Біомеханічний, міофасціальний та неврологічний аспекти.",
        },
        "mat_video3": {
            "title": "Що відчуває пацієнт після устілок",
            "desc": "Конкретні результати з клінічного досвіду: перший день, тиждень, місяць. Чому болі в коліні і попереку часто проходять після корекції стопи.",
        },
    }
    
    v = videos.get(query.data, videos["mat_video1"])
    
    text = f"""{v['title']}

{v['desc']}

Відео буде доступне після публікації. Щоб отримати сповіщення — залиште заявку або зв'яжіться з менеджером."""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Записатись на курс", callback_data="register")],
        [InlineKeyboardButton("Зв'язок з менеджером", callback_data="contact")],
        [InlineKeyboardButton("« Матеріали", callback_data="materials")],
    ])
    
    await query.edit_message_text(text, reply_markup=kb)

async def mat_pres(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    text = """Презентація системи Formthotics

Повна презентація включає:
— Що таке Formthotics і як працює
— Покази до ортезування
— 15 моделей устілок з описом
— 6 кроків протоколу
— Фінансова модель для лікаря
— Умови партнерства

Щоб отримати презентацію у PDF — зв'яжіться з менеджером або залиште заявку, і ми надішлемо особисто."""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Зв'язок з менеджером", callback_data="contact")],
        [InlineKeyboardButton("« Матеріали", callback_data="materials")],
    ])
    
    await query.edit_message_text(text, reply_markup=kb)

async def mat_site(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Відкрити formthotics.com.ua", url="https://formthotics.com.ua")],
        [InlineKeyboardButton("« Матеріали", callback_data="materials")],
    ])
    
    await query.edit_message_text(
        "Сайт Formthotics Ukraine\n\nНа сайті — повна інформація про систему, курс, покази до ортезування та форма реєстрації.",
        reply_markup=kb
    )

# ═════════════════════════════════════════════════════
# REGISTRATION FLOW
# ═════════════════════════════════════════════════════

async def register_start(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        f"Запис на курс {COURSE_DATE}\n\n"
        "Заповніть коротку форму — менеджер зв'яжеться з вами протягом 2 годин.\n\n"
        "Введіть ваше ім'я та прізвище:"
    )
    return REG_NAME

async def reg_name(update: Update, context):
    context.user_data["name"] = update.message.text.strip()
    
    # Request phone with button
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("Надіслати номер телефону", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    
    await update.message.reply_text(
        "Натисніть кнопку щоб надіслати номер автоматично, або введіть вручну:",
        reply_markup=kb
    )
    return REG_PHONE

async def reg_phone(update: Update, context):
    if update.message.contact:
        context.user_data["phone"] = update.message.contact.phone_number
    else:
        context.user_data["phone"] = update.message.text.strip()
    
    await update.message.reply_text(
        "Ваше місто:",
        reply_markup=ReplyKeyboardRemove()
    )
    return REG_CITY

async def reg_city(update: Update, context):
    context.user_data["city"] = update.message.text.strip()
    
    # Specialization keyboard
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(spec, callback_data=f"spec_{i}")]
        for i, spec in enumerate(SPECS)
    ])
    
    await update.message.reply_text(
        "Оберіть вашу спеціалізацію:",
        reply_markup=kb
    )
    return REG_SPEC

async def reg_spec(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    spec_idx = int(query.data.replace("spec_", ""))
    context.user_data["spec"] = SPECS[spec_idx]
    
    # Confirmation
    d = context.user_data
    text = (
        f"Перевірте ваші дані:\n\n"
        f"Ім'я: {d['name']}\n"
        f"Телефон: {d['phone']}\n"
        f"Місто: {d['city']}\n"
        f"Спеціалізація: {d['spec']}\n\n"
        f"Курс: {COURSE_DATE}\n\n"
        "Все вірно?"
    )
    
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Підтвердити", callback_data="reg_confirm"),
            InlineKeyboardButton("Скасувати", callback_data="reg_cancel"),
        ]
    ])
    
    await query.edit_message_text(text, reply_markup=kb)
    return REG_CONFIRM

async def reg_confirm(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    d = context.user_data
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # Save to users dict
    users[chat_id] = {
        "name": d["name"],
        "phone": d["phone"],
        "city": d["city"],
        "spec": d["spec"],
        "username": user.username,
    }
    
    # Notify manager
    manager_text = (
        f"📋 Нова заявка на курс з Telegram-бота\n\n"
        f"👤 Ім'я: {d['name']}\n"
        f"📞 Телефон: {d['phone']}\n"
        f"📍 Місто: {d['city']}\n"
        f"🏥 Спеціалізація: {d['spec']}\n"
        f"📱 Telegram: @{user.username or 'немає'}\n"
        f"🔢 Chat ID: {chat_id}\n\n"
        f"Курс: {COURSE_DATE}"
    )
    
    try:
        await context.bot.send_message(MANAGER_CHAT_ID, manager_text)
    except Exception as e:
        logger.error(f"Failed to notify manager: {e}")
    
    # Confirm to user
    await query.edit_message_text(
        "Заявку прийнято!\n\n"
        f"Менеджер зв'яжеться з вами протягом 2 годин і підтвердить ваше місце на курсі {COURSE_DATE}.\n\n"
        "Якщо маєте додаткові питання — натисніть /menu",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Головне меню", callback_data="back_main")]
        ])
    )
    return ConversationHandler.END

async def reg_cancel(update: Update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Реєстрацію скасовано. Ви завжди можете повернутись.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Головне меню", callback_data="back_main")]
        ])
    )
    return ConversationHandler.END

# ═════════════════════════════════════════════════════
# CONTACT MANAGER
# ═════════════════════════════════════════════════════

async def contact_start(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Зателефонувати: +38 093 07 97 090", url="tel:+380930797090")],
        [InlineKeyboardButton("Написати у Viber", url="viber://chat?number=%2B380930797090")],
        [InlineKeyboardButton("Написати повідомлення менеджеру", callback_data="contact_write")],
        [InlineKeyboardButton("« Головне меню", callback_data="back_main")],
    ])
    
    await query.edit_message_text(
        "Зв'язок з менеджером\n\n"
        "Оберіть зручний спосіб або напишіть повідомлення — менеджер відповість якнайшвидше.",
        reply_markup=kb
    )

async def contact_write_start(update: Update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Напишіть ваше питання або повідомлення — я передам менеджеру:"
    )
    return CONTACT_MSG

async def contact_write_msg(update: Update, context):
    user = update.effective_user
    msg = update.message.text
    
    # Forward to manager
    try:
        await context.bot.send_message(
            MANAGER_CHAT_ID,
            f"💬 Повідомлення від користувача бота:\n\n"
            f"Від: {user.first_name} {user.last_name or ''}\n"
            f"Username: @{user.username or 'немає'}\n"
            f"ID: {update.effective_chat.id}\n\n"
            f"Повідомлення:\n{msg}"
        )
    except Exception as e:
        logger.error(f"Failed to forward message: {e}")
    
    await update.message.reply_text(
        "Повідомлення надіслано менеджеру. Очікуйте відповідь.\n\n"
        "Натисніть /menu щоб повернутись до головного меню.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Головне меню", callback_data="back_main")]
        ])
    )
    return ConversationHandler.END

# ═════════════════════════════════════════════════════
# BACK TO MAIN MENU
# ═════════════════════════════════════════════════════

async def back_main(update: Update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Головне меню:", reply_markup=main_menu_kb())

# ═════════════════════════════════════════════════════
# MANAGER REPLY (manager can reply to users via bot)
# ═════════════════════════════════════════════════════

async def manager_reply(update: Update, context):
    """Manager replies to user by replying to forwarded message in bot chat."""
    if update.effective_chat.id != MANAGER_CHAT_ID:
        return
    
    if not update.message.reply_to_message:
        return
    
    # Extract user chat ID from the forwarded message
    original = update.message.reply_to_message.text or ""
    
    import re
    match = re.search(r"ID: (\d+)", original)
    if match:
        user_chat_id = int(match.group(1))
        try:
            await context.bot.send_message(
                user_chat_id,
                f"Відповідь від менеджера Formthotics:\n\n{update.message.text}"
            )
            await update.message.reply_text(f"Відповідь надіслано користувачу {user_chat_id}")
        except Exception as e:
            await update.message.reply_text(f"Помилка надсилання: {e}")

# ═════════════════════════════════════════════════════
# FALLBACK
# ═════════════════════════════════════════════════════

async def fallback(update: Update, context):
    await update.message.reply_text(
        "Не зрозумів команду. Натисніть /menu щоб відкрити головне меню.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Головне меню", callback_data="back_main")]
        ])
    )

async def cancel(update: Update, context):
    await update.message.reply_text(
        "Дію скасовано.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Головне меню", callback_data="back_main")]
        ])
    )
    return ConversationHandler.END

# ═════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Registration conversation
    reg_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(register_start, pattern="^register$")],
        states={
            REG_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_name)],
            REG_PHONE: [
                MessageHandler(filters.CONTACT, reg_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, reg_phone),
            ],
            REG_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_city)],
            REG_SPEC: [CallbackQueryHandler(reg_spec, pattern="^spec_")],
            REG_CONFIRM: [
                CallbackQueryHandler(reg_confirm, pattern="^reg_confirm$"),
                CallbackQueryHandler(reg_cancel, pattern="^reg_cancel$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("menu", menu)],
        per_message=False,
    )
    
    # Contact conversation
    contact_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(contact_write_start, pattern="^contact_write$")],
        states={
            CONTACT_MSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact_write_msg)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("menu", menu)],
        per_message=False,
    )
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(reg_conv)
    app.add_handler(contact_conv)
    
    # Callback handlers
    app.add_handler(CallbackQueryHandler(about, pattern="^about$"))
    app.add_handler(CallbackQueryHandler(about_what, pattern="^about_what$"))
    app.add_handler(CallbackQueryHandler(about_how, pattern="^about_how$"))
    app.add_handler(CallbackQueryHandler(about_models, pattern="^about_models$"))
    app.add_handler(CallbackQueryHandler(about_indications, pattern="^about_indications$"))
    app.add_handler(CallbackQueryHandler(about_benefits, pattern="^about_benefits$"))
    app.add_handler(CallbackQueryHandler(courses, pattern="^courses$"))
    app.add_handler(CallbackQueryHandler(course_program, pattern="^course_program$"))
    app.add_handler(CallbackQueryHandler(materials, pattern="^materials$"))
    app.add_handler(CallbackQueryHandler(mat_video, pattern="^mat_video"))
    app.add_handler(CallbackQueryHandler(mat_pres, pattern="^mat_pres$"))
    app.add_handler(CallbackQueryHandler(mat_site, pattern="^mat_site$"))
    app.add_handler(CallbackQueryHandler(contact_start, pattern="^contact$"))
    app.add_handler(CallbackQueryHandler(back_main, pattern="^back_main$"))
    
    # Manager reply handler
    app.add_handler(MessageHandler(
        filters.REPLY & filters.Chat(MANAGER_CHAT_ID),
        manager_reply
    ))
    
    # Fallback for unknown messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))
    
    print("Bot started! Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
