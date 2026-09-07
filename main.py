"""
Formthotics Ukraine — Telegram Bot для лікарів-партнерів
"""

import logging
import os
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InputMediaPhoto
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters
)

# ── CONFIG ─────────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8949754941:AAGA4E5gl6ZZCUoOd94p3P-bKUrnNXxS_UA")
MANAGER_CHAT_ID = int(os.environ.get("MANAGER_CHAT_ID", "642551073"))

COURSE_DATE = "19–20 вересня 2026"
COURSE_LECTURER = "Дмитро Кущик"
SITE_URL = "https://formthotics.com.ua"
PHONE = "+38 093 07 97 090"

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")

logging.basicConfig(
    format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO
)
log = logging.getLogger(__name__)

(REG_NAME, REG_PHONE, REG_CITY, REG_SPEC, REG_CONFIRM, CONTACT_MSG) = range(6)

users = {}

SPECS = [
    ("🦴", "Ортопед / травматолог"),
    ("🏃", "Реабілітолог"),
    ("💪", "Фізичний терапевт"),
    ("👣", "Подолог"),
    ("🧘", "Кінезіолог / остеопат"),
    ("🧒", "Педіатр / дитячий ортопед"),
    ("⚕️", "Інша спеціалізація"),
]


def img(name):
    """Return open file handle for image, or None."""
    p = os.path.join(IMG, f"{name}.jpg")
    return p if os.path.exists(p) else None


# ═══════════════════════════════════════════════════════
#  MAIN MENU
# ═══════════════════════════════════════════════════════

def kb_main():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📋  Про систему", callback_data="about"),
            InlineKeyboardButton("🎓  Навчання", callback_data="courses"),
        ],
        [
            InlineKeyboardButton("🎬  Матеріали", callback_data="materials"),
            InlineKeyboardButton("🤝  Партнерство", callback_data="partner"),
        ],
        [InlineKeyboardButton("✍️  Записатись на курс", callback_data="register")],
        [InlineKeyboardButton("💬  Зв'язок з менеджером", callback_data="contact")],
    ])


WELCOME = f"""<b>FORMTHOTICS UKRAINE</b>
<i>Індивідуальні ортези стопи з Нової Зеландії</i>

━━━━━━━━━━━━━━━━━━━━

Вітаємо! Ми — офіційний дистриб'ютор <b>Formthotics</b> в Україні.

Клінічно доведена медична система індивідуального ортезування стопи від Foot Science International.

<b>40+</b> років  ·  <b>30+</b> країн  ·  <b>100+</b> партнерів в Україні

━━━━━━━━━━━━━━━━━━━━

📅 <b>Найближчий курс: {COURSE_DATE}</b>
Лектор — {COURSE_LECTURER}

Оберіть розділ:"""


async def start(update: Update, context):
    u = update.effective_user
    cid = update.effective_chat.id
    users.setdefault(cid, {"first_name": u.first_name, "username": u.username})

    try:
        await context.bot.send_message(
            MANAGER_CHAT_ID,
            f"👤 <b>Новий користувач бота</b>\n\n"
            f"Ім'я: {u.first_name} {u.last_name or ''}\n"
            f"Telegram: @{u.username or '—'}\n"
            f"ID: <code>{cid}</code>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.warning(f"manager notify failed: {e}")

    photo = img("course_banner")
    if photo:
        with open(photo, "rb") as f:
            await update.message.reply_photo(
                photo=f, caption=WELCOME,
                parse_mode=ParseMode.HTML, reply_markup=kb_main()
            )
    else:
        await update.message.reply_text(
            WELCOME, parse_mode=ParseMode.HTML, reply_markup=kb_main()
        )


async def menu_cmd(update: Update, context):
    await update.message.reply_text(
        "<b>Головне меню</b>\n\nОберіть розділ:",
        parse_mode=ParseMode.HTML, reply_markup=kb_main()
    )


async def show(query, text, kb, photo_name=None):
    """Edit message — swap to photo if needed, else edit text."""
    photo = img(photo_name) if photo_name else None
    has_photo = bool(query.message.photo)

    try:
        if photo and has_photo:
            with open(photo, "rb") as f:
                await query.edit_message_media(
                    media=InputMediaPhoto(f, caption=text, parse_mode=ParseMode.HTML),
                    reply_markup=kb
                )
        elif has_photo:
            await query.edit_message_caption(
                caption=text, parse_mode=ParseMode.HTML, reply_markup=kb
            )
        else:
            await query.edit_message_text(
                text, parse_mode=ParseMode.HTML, reply_markup=kb,
                disable_web_page_preview=True
            )
    except Exception as e:
        log.warning(f"show failed: {e}")
        await query.message.reply_text(
            text, parse_mode=ParseMode.HTML, reply_markup=kb,
            disable_web_page_preview=True
        )


# ═══════════════════════════════════════════════════════
#  ABOUT
# ═══════════════════════════════════════════════════════

async def about(update: Update, context):
    q = update.callback_query
    await q.answer()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💡  Що таке Formthotics", callback_data="a_what")],
        [InlineKeyboardButton("⚙️  Протокол — 6 кроків", callback_data="a_how")],
        [InlineKeyboardButton("🎨  15 моделей устілок", callback_data="a_models")],
        [InlineKeyboardButton("🩺  Покази до ортезування", callback_data="a_ind")],
        [InlineKeyboardButton("« Головне меню", callback_data="home")],
    ])
    text = """<b>📋  ПРО СИСТЕМУ FORMTHOTICS</b>
━━━━━━━━━━━━━━━━━━━━

Оберіть що вас цікавить:"""
    await show(q, text, kb, "product")


async def a_what(update: Update, context):
    q = update.callback_query
    await q.answer()
    text = """<b>💡  ЩО ТАКЕ FORMTHOTICS</b>
━━━━━━━━━━━━━━━━━━━━

Медична система індивідуального ортезування стопи від <b>Foot Science International</b> (Нова Зеландія).

На відміну від стандартних устілок з аптеки, Formthotics формується <b>безпосередньо на стопі пацієнта</b> у вашому кабінеті за 20 хвилин.

<b>Матеріал Formax</b>
При нагріванні до 85°C набуває пластичності і точно запам'ятовує форму стопи — як відбиток. Кожна пара унікальна.

━━━━━━━━━━━━━━━━━━━━
<b>Ключові факти</b>

⏱  <b>20 хв</b> — від огляду до готових ортезів
🌡  <b>85°C</b> — температура формування Formax
📅  <b>1–2 роки</b> — рекомендований термін експлуатації
🌍  <b>30+ країн</b> — клінічна практика лікарів
🔬  <b>40+ років</b> — досліджень і розробок"""
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️  Як працює протокол", callback_data="a_how")],
        [InlineKeyboardButton("✍️  Записатись на курс", callback_data="register")],
        [InlineKeyboardButton("« Назад", callback_data="about")],
    ])
    await show(q, text, kb, "product")


async def a_how(update: Update, context):
    q = update.callback_query
    await q.answer()
    text = """<b>⚙️  ПРОТОКОЛ У КАБІНЕТІ</b>
━━━━━━━━━━━━━━━━━━━━

<b>1 ▸ Діагностика</b>  <i>10 хв</i>
Візуальна оцінка постави і ходи з подоскопом. 6 функціональних тестів — біомеханічний, міофасціальний, неврологічний аспекти.

<b>2 ▸ Вибір заготівок</b>  <i>5 хв</i>
Модель під ступінь деформації, тип взуття, вік, вагу, активність.

<b>3 ▸ Формування</b>  <i>15 хв</i>
Розігрів до 85°C. Матеріал набуває пластичності і формується на стопі в нейтральному положенні.

<b>4 ▸ Корекція</b>  <i>повторний візит</i>
Оцінка ходи і постави. Функціональні клини переднього і заднього відділу.

<b>5 ▸ Перевірка у взутті</b>
Остаточна оцінка коли пацієнт взутий.

<b>6 ▸ Результат</b>  <i>1–7 днів</i>
Полегшення болю. Адаптація 3–4 тижні.

━━━━━━━━━━━━━━━━━━━━
⏱  <b>Весь цикл — 20–40 хвилин</b>"""
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎨  15 моделей устілок", callback_data="a_models")],
        [InlineKeyboardButton("✍️  Записатись на курс", callback_data="register")],
        [InlineKeyboardButton("« Назад", callback_data="about")],
    ])
    await show(q, text, kb, "lecture")


async def a_models(update: Update, context):
    q = update.callback_query
    await q.answer()
    text = """<b>🎨  МОДЕЛЬНИЙ РЯД — 15 МОДЕЛЕЙ</b>
━━━━━━━━━━━━━━━━━━━━
<i>Кожен колір — рівень жорсткості і призначення</i>

🩷  <b>Рожева</b>
М'яка, тонка. Модельне взуття, перші користувачі, стояча робота

🤎  <b>Бежева</b>
Пружна. Максимум ефекту при мінімумі об'єму

⚫  <b>Шок-стоп</b>  <i>двошарова</i>
Діабетична стопа, шпора, подагра, гострі запалення

🔴🔵  <b>Червоно-блакитна</b>
Середня жорсткість. Перевантаження ОРА, бігуни

🔵  <b>Блакитна</b>
Ковзани, лижі, жорстке спортивне взуття

🟤  <b>Чорно-бежева</b>  <i>перфорація</i>
Фітнес, туризм, гіпергідроз стопи

🟢  <b>Зелена</b>
Вузьке і модельне взуття

❤️  <b>Рожево-червона</b>
Вага 80+ кг, інтенсивний спорт

🔺  <b>Червона</b>
Найжорсткіша. Максимальні навантаження

🧒  <b>Junior / Uni</b>
Діти від 2 років. Вальгус, плоскостопість

▫️  <b>3/4 Комфорт</b>
Туфлі, балетки, бутси"""
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🩺  Покази до ортезування", callback_data="a_ind")],
        [InlineKeyboardButton("✍️  Записатись на курс", callback_data="register")],
        [InlineKeyboardButton("« Назад", callback_data="about")],
    ])
    await show(q, text, kb, "product")


async def a_ind(update: Update, context):
    q = update.callback_query
    await q.answer()
    text = """<b>🩺  ПОКАЗИ ДО ОРТЕЗУВАННЯ</b>
━━━━━━━━━━━━━━━━━━━━

<b>👣  Стопа і гомілка</b>
• Плоскостопість поздовжня і поперечна
• Вальгусна деформація п'яти
• П'яткова шпора, підошовний фасциїт
• Неврома Мортона
• Тендовагініт ахіллового сухожилля
• Натоптиші і сухі мозолі

<b>🦴  Суглоби та хребет</b>
• Болі в колінних і кульшових суглобах
• Болі в попереку і крижах
• Перекіс тазу, грижі дисків
• Сколіоз, порушення постави і ходи

<b>❤️  Особливі групи</b>
• Діти від 2 років — вальгус, плоскостопість
• Спортсмени — всі рівні навантажень
• Діабетична стопа — профілактика
• Вагітність — набряки, плоскостопість
• Реабілітація після травм і операцій
• Мінно-вибухові поранення стопи"""
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤝  Умови партнерства", callback_data="partner")],
        [InlineKeyboardButton("✍️  Записатись на курс", callback_data="register")],
        [InlineKeyboardButton("« Назад", callback_data="about")],
    ])
    await show(q, text, kb, "product")


# ═══════════════════════════════════════════════════════
#  COURSES
# ═══════════════════════════════════════════════════════

async def courses(update: Update, context):
    q = update.callback_query
    await q.answer()
    text = f"""<b>🎓  НАВЧАННЯ ТА СЕРТИФІКАЦІЯ</b>
━━━━━━━━━━━━━━━━━━━━

📅  <b>{COURSE_DATE}</b>
👤  Лектор — <b>{COURSE_LECTURER}</b>
📍  Формат — офлайн, 2 дні, практика
📜  Сертифікат спеціаліста

━━━━━━━━━━━━━━━━━━━━

<b>Дмитро Кущик</b> — кінезіолог, засновник Школи функціональної кінезіології, автор методики роботи з м'язово-фасціальними ланцюгами.

Авторський підхід поєднує кінезіологію з клінічним ортезуванням — ви отримуєте системне розуміння як стопа впливає на весь опорно-руховий апарат.

━━━━━━━━━━━━━━━━━━━━
⚡️  <i>Місця обмежені — практика в невеликих групах</i>"""
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📖  Програма курсу", callback_data="c_program")],
        [InlineKeyboardButton("✍️  Записатись на курс", callback_data="register")],
        [InlineKeyboardButton("💬  Задати питання", callback_data="contact")],
        [InlineKeyboardButton("« Головне меню", callback_data="home")],
    ])
    await show(q, text, kb, "kushchyk")


async def c_program(update: Update, context):
    q = update.callback_query
    await q.answer()
    text = f"""<b>📖  ПРОГРАМА КУРСУ</b>
<i>{COURSE_DATE}</i>
━━━━━━━━━━━━━━━━━━━━

<b>ДЕНЬ ПЕРШИЙ</b>  ·  <i>теорія + практика</i>

<code>01</code>  Будова стопи та її розвиток
<code>02</code>  Анатомія та функція м'язів стопи
<code>03</code>  Стопа в статиці та патерні кроку
<code>04</code>  Візуальна діагностика дисфункцій
<code>05</code>  6 функціональних тестів
<code>06</code>  Практика діагностики на учасниках

━━━━━━━━━━━━━━━━━━━━

<b>ДЕНЬ ДРУГИЙ</b>  ·  <i>клініка + ортезування</i>

<code>07</code>  Найпоширеніші проблеми стопи
<code>08</code>  Покази до ортезування
<code>09</code>  Коли устілка не потрібна?
<code>10</code>  Вплив ортезів на здоров'я
<code>11</code>  Підбір, формування, корекція
<code>12</code>  Адаптація сформованих ортезів

━━━━━━━━━━━━━━━━━━━━
📜  <b>Сертифікат спеціаліста Formthotics</b>
Готовий протокол для роботи з першого дня"""
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✍️  Записатись на курс", callback_data="register")],
        [InlineKeyboardButton("« Навчання", callback_data="courses")],
    ])
    await show(q, text, kb, "lecture")


# ═══════════════════════════════════════════════════════
#  PARTNERSHIP
# ═══════════════════════════════════════════════════════

async def partner(update: Update, context):
    q = update.callback_query
    await q.answer()
    text = """<b>🤝  УМОВИ ПАРТНЕРСТВА</b>
━━━━━━━━━━━━━━━━━━━━

<b>💰  Прозора фінансова модель</b>
Закупка <b>2 600 грн</b> → продаж від <b>6 000 грн</b>
Прибуток від <b>3 400 грн</b> з кожної пари

<b>📋  Готовий протокол</b>
Покроковий алгоритм від діагностики до корекції. Працюєте з першого дня після навчання.

<b>🎓  Навчання і сертифікат</b>
2-денний тренінг з практикою. Сертифікат спеціаліста Formthotics.

<b>🔄  Розтермінування обладнання</b>
Сушка для устілок — 3 рівних платежі. Покриваєте вартість з перших пар.

<b>🛟  Повний супровід</b>
Telegram-чат партнерів, консультації по складних випадках, маркетингові матеріали.

━━━━━━━━━━━━━━━━━━━━
<b>Що потрібно для старту</b>

✔️  Пройти 2-денне навчання
✔️  Сушка для устілок <i>(є розтермінування)</i>
✔️  Стартовий набір заготівок

━━━━━━━━━━━━━━━━━━━━
📊  <b>95%</b> лікарів після навчання продовжують замовляти постійно"""
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✍️  Записатись на курс", callback_data="register")],
        [InlineKeyboardButton("💬  Обговорити з менеджером", callback_data="contact")],
        [InlineKeyboardButton("« Головне меню", callback_data="home")],
    ])
    await show(q, text, kb, "group")


# ═══════════════════════════════════════════════════════
#  MATERIALS
# ═══════════════════════════════════════════════════════

async def materials(update: Update, context):
    q = update.callback_query
    await q.answer()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📸  Фото з останнього курсу", callback_data="m_photos")],
        [InlineKeyboardButton("🎬  Відео від лектора", callback_data="m_video")],
        [InlineKeyboardButton("📊  Презентація системи", callback_data="m_pres")],
        [InlineKeyboardButton("🌐  Сайт formthotics.com.ua", url=SITE_URL)],
        [InlineKeyboardButton("« Головне меню", callback_data="home")],
    ])
    text = """<b>🎬  МАТЕРІАЛИ ДЛЯ ЛІКАРІВ</b>
━━━━━━━━━━━━━━━━━━━━

Оберіть що вас цікавить:"""
    await show(q, text, kb, "lecture")


async def m_photos(update: Update, context):
    q = update.callback_query
    await q.answer()

    photos = []
    for n in ("group", "lecture", "cert1"):
        p = img(n)
        if p:
            photos.append(p)

    if photos:
        media = []
        for i, p in enumerate(photos):
            cap = "<b>Курс Formthotics</b>\nДмитро Кущик · Практика на учасниках" if i == 0 else None
            media.append(InputMediaPhoto(open(p, "rb"), caption=cap, parse_mode=ParseMode.HTML))
        try:
            await q.message.reply_media_group(media=media)
        except Exception as e:
            log.warning(f"media group failed: {e}")

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✍️  Записатись на курс", callback_data="register")],
        [InlineKeyboardButton("« Матеріали", callback_data="materials")],
    ])
    await q.message.reply_text(
        "<b>📸  Фото з останнього курсу</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
        "Практика на учасниках, розбір клінічних випадків, вручення сертифікатів.\n\n"
        f"Наступний курс — <b>{COURSE_DATE}</b>",
        parse_mode=ParseMode.HTML, reply_markup=kb
    )


async def m_video(update: Update, context):
    q = update.callback_query
    await q.answer()
    text = """<b>🎬  ВІДЕО ВІД ЛЕКТОРА</b>
━━━━━━━━━━━━━━━━━━━━

<b>1 ▸ Чому стандартна устілка не лікує</b>
<i>Різниця між аптечною устілкою і медичною системою. Чому один підхід маскує симптом, а інший усуває причину.</i>

<b>2 ▸ 6 функціональних тестів</b>
<i>Як за 3 хвилини оцінити стан всього ОРА через стопу. Біомеханічний, міофасціальний, неврологічний аспекти.</i>

<b>3 ▸ Що відчуває пацієнт після устілок</b>
<i>Конкретні результати: перший день, тиждень, місяць. Чому болі в коліні і попереку проходять після корекції стопи.</i>

━━━━━━━━━━━━━━━━━━━━
📩  Щоб отримати відео — залиште заявку або напишіть менеджеру"""
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬  Отримати відео", callback_data="contact")],
        [InlineKeyboardButton("✍️  Записатись на курс", callback_data="register")],
        [InlineKeyboardButton("« Матеріали", callback_data="materials")],
    ])
    await show(q, text, kb, "kushchyk")


async def m_pres(update: Update, context):
    q = update.callback_query
    await q.answer()
    text = """<b>📊  ПРЕЗЕНТАЦІЯ СИСТЕМИ</b>
━━━━━━━━━━━━━━━━━━━━

Повна презентація включає:

▸  Що таке Formthotics і як працює
▸  Покази до ортезування
▸  15 моделей устілок з описом
▸  6 кроків клінічного протоколу
▸  Фінансова модель для лікаря
▸  Умови партнерства

━━━━━━━━━━━━━━━━━━━━
📩  Щоб отримати презентацію у PDF — напишіть менеджеру, надішлемо особисто"""
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬  Отримати презентацію", callback_data="contact")],
        [InlineKeyboardButton("🌐  Сайт з деталями", url=SITE_URL)],
        [InlineKeyboardButton("« Матеріали", callback_data="materials")],
    ])
    await show(q, text, kb, "product")


# ═══════════════════════════════════════════════════════
#  REGISTRATION
# ═══════════════════════════════════════════════════════

async def reg_start(update: Update, context):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text(
        f"<b>✍️  ЗАПИС НА КУРС</b>\n"
        f"<i>{COURSE_DATE}</i>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Заповніть коротку форму — менеджер зв'яжеться протягом 2 годин "
        "і підтвердить ваше місце.\n\n"
        "<b>Крок 1 з 4</b>\n"
        "Введіть ваше <b>ім'я та прізвище</b>:",
        parse_mode=ParseMode.HTML
    )
    return REG_NAME


async def reg_name(update: Update, context):
    context.user_data["name"] = update.message.text.strip()
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📱  Надіслати мій номер", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await update.message.reply_text(
        "<b>Крок 2 з 4</b>\n"
        "Ваш <b>номер телефону</b>\n\n"
        "<i>Натисніть кнопку нижче або введіть вручну</i>",
        parse_mode=ParseMode.HTML, reply_markup=kb
    )
    return REG_PHONE


async def reg_phone(update: Update, context):
    if update.message.contact:
        context.user_data["phone"] = update.message.contact.phone_number
    else:
        context.user_data["phone"] = update.message.text.strip()
    await update.message.reply_text(
        "<b>Крок 3 з 4</b>\nВаше <b>місто</b>:",
        parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove()
    )
    return REG_CITY


async def reg_city(update: Update, context):
    context.user_data["city"] = update.message.text.strip()
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{e}  {s}", callback_data=f"sp_{i}")]
        for i, (e, s) in enumerate(SPECS)
    ])
    await update.message.reply_text(
        "<b>Крок 4 з 4</b>\nОберіть вашу <b>спеціалізацію</b>:",
        parse_mode=ParseMode.HTML, reply_markup=kb
    )
    return REG_SPEC


async def reg_spec(update: Update, context):
    q = update.callback_query
    await q.answer()
    i = int(q.data.replace("sp_", ""))
    context.user_data["spec"] = SPECS[i][1]
    d = context.user_data
    text = (
        "<b>ПЕРЕВІРТЕ ДАНІ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤  <b>Ім'я</b>\n{d['name']}\n\n"
        f"📞  <b>Телефон</b>\n{d['phone']}\n\n"
        f"📍  <b>Місто</b>\n{d['city']}\n\n"
        f"🏥  <b>Спеціалізація</b>\n{d['spec']}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📅  Курс: <b>{COURSE_DATE}</b>"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅  Підтвердити заявку", callback_data="rc_ok")],
        [InlineKeyboardButton("❌  Скасувати", callback_data="rc_no")],
    ])
    await q.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)
    return REG_CONFIRM


async def reg_ok(update: Update, context):
    q = update.callback_query
    await q.answer()
    d = context.user_data
    cid = update.effective_chat.id
    u = update.effective_user
    users[cid] = {**d, "username": u.username}

    try:
        await context.bot.send_message(
            MANAGER_CHAT_ID,
            "🔥 <b>НОВА ЗАЯВКА НА КУРС</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤  <b>{d['name']}</b>\n"
            f"📞  <code>{d['phone']}</code>\n"
            f"📍  {d['city']}\n"
            f"🏥  {d['spec']}\n\n"
            f"💬  Telegram: @{u.username or '—'}\n"
            f"🆔  <code>{cid}</code>\n\n"
            f"📅  Курс: {COURSE_DATE}\n\n"
            "<i>Відповідайте на це повідомлення щоб написати клієнту</i>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.error(f"manager notify failed: {e}")

    await q.edit_message_text(
        "✅  <b>ЗАЯВКУ ПРИЙНЯТО</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Дякуємо! Менеджер зв'яжеться з вами <b>протягом 2 годин</b> "
        f"і підтвердить місце на курсі {COURSE_DATE}.\n\n"
        f"📞  {PHONE}\n"
        f"🌐  formthotics.com.ua\n\n"
        "<i>Маєте питання — тисніть /menu</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠  Головне меню", callback_data="home")]
        ])
    )
    return ConversationHandler.END


async def reg_no(update: Update, context):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        "Реєстрацію скасовано.\n\nВи завжди можете повернутись.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠  Головне меню", callback_data="home")]
        ])
    )
    return ConversationHandler.END


# ═══════════════════════════════════════════════════════
#  CONTACT
# ═══════════════════════════════════════════════════════

async def contact(update: Update, context):
    q = update.callback_query
    await q.answer()
    text = f"""<b>💬  ЗВ'ЯЗОК З МЕНЕДЖЕРОМ</b>
━━━━━━━━━━━━━━━━━━━━

Оберіть зручний спосіб зв'язку:

📞  <b>{PHONE}</b>
<i>Телефон · Viber · Telegram</i>

🌐  <b>formthotics.com.ua</b>

✉️  <b>admin@maximusgroup.com.ua</b>

━━━━━━━━━━━━━━━━━━━━
<i>Або напишіть повідомлення прямо тут — менеджер відповість якнайшвидше</i>"""
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📞  Зателефонувати", url=f"tel:{PHONE.replace(' ', '')}")],
        [InlineKeyboardButton("✍️  Написати повідомлення", callback_data="c_write")],
        [InlineKeyboardButton("🌐  Відкрити сайт", url=SITE_URL)],
        [InlineKeyboardButton("« Головне меню", callback_data="home")],
    ])
    await show(q, text, kb, "logo")


async def c_write_start(update: Update, context):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text(
        "<b>✍️  ПОВІДОМЛЕННЯ МЕНЕДЖЕРУ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Напишіть ваше питання — передам менеджеру:",
        parse_mode=ParseMode.HTML
    )
    return CONTACT_MSG


async def c_write_msg(update: Update, context):
    u = update.effective_user
    try:
        await context.bot.send_message(
            MANAGER_CHAT_ID,
            "💬 <b>ПОВІДОМЛЕННЯ ВІД КОРИСТУВАЧА</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤  {u.first_name} {u.last_name or ''}\n"
            f"💬  @{u.username or '—'}\n"
            f"🆔  <code>{update.effective_chat.id}</code>\n\n"
            f"<b>Текст:</b>\n{update.message.text}\n\n"
            "<i>Відповідайте на це повідомлення щоб написати клієнту</i>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.error(f"forward failed: {e}")

    await update.message.reply_text(
        "✅  Повідомлення надіслано менеджеру.\n\nОчікуйте відповідь найближчим часом.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠  Головне меню", callback_data="home")]
        ])
    )
    return ConversationHandler.END


# ═══════════════════════════════════════════════════════
#  HOME / MANAGER REPLY / FALLBACK
# ═══════════════════════════════════════════════════════

async def home(update: Update, context):
    q = update.callback_query
    await q.answer()
    await show(q, WELCOME, kb_main(), "course_banner")


async def manager_reply(update: Update, context):
    if update.effective_chat.id != MANAGER_CHAT_ID:
        return
    if not update.message.reply_to_message:
        return
    import re
    src = update.message.reply_to_message.text or ""
    m = re.search(r"🆔\s*(\d+)", src) or re.search(r"ID:\s*(\d+)", src)
    if m:
        uid = int(m.group(1))
        try:
            await context.bot.send_message(
                uid,
                f"<b>💬  Відповідь від Formthotics Ukraine</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                f"{update.message.text}",
                parse_mode=ParseMode.HTML
            )
            await update.message.reply_text(f"✅ Надіслано користувачу {uid}")
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка: {e}")


async def fallback(update: Update, context):
    await update.message.reply_text(
        "Не зрозумів команду.\n\nНатисніть кнопку нижче або /menu",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠  Головне меню", callback_data="home")]
        ])
    )


async def cancel(update: Update, context):
    await update.message.reply_text(
        "Дію скасовано.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠  Головне меню", callback_data="home")]
        ])
    )
    return ConversationHandler.END


# ═══════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    reg = ConversationHandler(
        entry_points=[CallbackQueryHandler(reg_start, pattern="^register$")],
        states={
            REG_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_name)],
            REG_PHONE: [
                MessageHandler(filters.CONTACT, reg_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, reg_phone),
            ],
            REG_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_city)],
            REG_SPEC: [CallbackQueryHandler(reg_spec, pattern="^sp_")],
            REG_CONFIRM: [
                CallbackQueryHandler(reg_ok, pattern="^rc_ok$"),
                CallbackQueryHandler(reg_no, pattern="^rc_no$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("menu", menu_cmd)],
        per_message=False,
    )

    con = ConversationHandler(
        entry_points=[CallbackQueryHandler(c_write_start, pattern="^c_write$")],
        states={CONTACT_MSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, c_write_msg)]},
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("menu", menu_cmd)],
        per_message=False,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_cmd))
    app.add_handler(reg)
    app.add_handler(con)

    for pat, fn in [
        ("^about$", about), ("^a_what$", a_what), ("^a_how$", a_how),
        ("^a_models$", a_models), ("^a_ind$", a_ind),
        ("^courses$", courses), ("^c_program$", c_program),
        ("^partner$", partner),
        ("^materials$", materials), ("^m_photos$", m_photos),
        ("^m_video$", m_video), ("^m_pres$", m_pres),
        ("^contact$", contact), ("^home$", home),
    ]:
        app.add_handler(CallbackQueryHandler(fn, pattern=pat))

    app.add_handler(MessageHandler(
        filters.REPLY & filters.Chat(MANAGER_CHAT_ID), manager_reply
    ))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))

    log.info("Bot started")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
