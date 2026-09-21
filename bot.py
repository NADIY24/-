# -*- coding: utf-8 -*-
"""
Forma Ánima — квиз-бот "Архетип вашего бренда"
Полный перенос веб-квиза (12 вопросов, 12 архетипов по Юнгу) в Telegram-бота.
Бот бесплатный — работает как лид-магнит, в конце ведёт на платный "Разбор проекта".

Запуск:
    pip install -r requirements.txt
    export BOT_TOKEN="ваш_токен_от_BotFather"
    python bot.py
"""

import asyncio
import io
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from PIL import Image, ImageDraw

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "PASTE_YOUR_TOKEN_HERE")

TELEGRAM_CONTACT_URL = "https://t.me/nadiya_dsgn"
MAX_CONTACT_URL = "https://max.ru/u/f9LHodD0cOJIpZMCsKBfDxeAIGWfkagEDyz-TSOhGqJn5E7uIBSp1bIe-tk"
CODE_WORD = "АРХЕТИП"

DISCLAIMER = (
    "Это игровая модель для эксперимента с образом бренда, а не научный "
    "психологический инструмент — результат не является диагностикой личности "
    "или гарантией. Типология архетипов основана на классической концепции "
    "К. Г. Юнга («Структура личности и архетипы по Юнгу»)."
)

# ---------------------------------------------------------------------------
# Вопросы: 12 штук, каждый с 4 вариантами, код варианта = код архетипа
# ---------------------------------------------------------------------------

QUESTIONS = [
    {
        "text": "Если бы ваш бренд пришёл на важную встречу, что на нём надето?",
        "options": [
            ("Смокинг безупречного кроя — ничего лишнего", "A"),
            ("Наряд, подчёркивающий и притягивающий взгляд", "S"),
            ("Дерзкий крой, которого ещё не видели", "B"),
            ("Простая одежда без единой лишней детали, только суть", "F"),
        ],
    },
    {
        "text": "Какой звук ассоциируется с вашим брендом?",
        "options": [
            ("Барабанная дробь перед победой", "G"),
            ("Смех и звон бокалов среди своих", "Fr"),
            ("Неожиданный джазовый импровиз", "Cr"),
            ("Смех и хлопки в ладоши", "Pl"),
        ],
    },
    {
        "text": "Какое место ближе всего атмосфере бренда?",
        "options": [
            ("Дорога, где никогда не были раньше", "Ex"),
            ("Место, где происходит необъяснимое", "Mg"),
            ("Дом, где всем спокойно и тепло", "Cg"),
            ("Солнечная поляна без единой тучи", "In"),
        ],
    },
    {
        "text": "Как ваш бренд реагирует на критику или конкурентов?",
        "options": [
            ("Не реагирует — уровень другой", "A"),
            ("Очаровывает и переманивает", "S"),
            ("Делает ровно наоборот назло", "B"),
            ("Молчит и продолжает быть собой", "F"),
        ],
    },
    {
        "text": "В какой момент работы вы чувствуете себя максимально живым?",
        "options": [
            ("Когда получается победить и доказать делом", "G"),
            ("Когда все свои рядом и всё по-честному", "Fr"),
            ("Когда рождается то, чего не было ни у кого", "Cr"),
            ("Когда все вокруг смеются вместе с вами", "Pl"),
        ],
    },
    {
        "text": "Чего ваш бренд больше всего хочет для клиента?",
        "options": [
            ("Показать мир по-новому", "Ex"),
            ("Подарить ощущение чуда и перемены", "Mg"),
            ("Позаботиться и защитить", "Cg"),
            ("Дать простую, честную радость", "In"),
        ],
    },
    {
        "text": "Какая метафора ближе всего вашему делу?",
        "options": [
            ("Родовое поместье, передающееся из поколения в поколение", "A"),
            ("Будуар, куда попадают немногие", "S"),
            ("Андеграундная студия художника", "B"),
            ("Тихий кабинет с видом в сад", "F"),
        ],
    },
    {
        "text": "Что должен почувствовать клиент, увидев ваш логотип?",
        "options": [
            ("«Хочу быть первым, у кого это есть»", "G"),
            ("«Здесь просто и по-честному»", "Fr"),
            ("«Это невозможно было придумать без души»", "Cr"),
            ("«С этим точно не соскучишься»", "Pl"),
        ],
    },
    {
        "text": "Если бы бренд был напитком, что это?",
        "options": [
            ("Крепкий кофе в дорожном термосе", "Ex"),
            ("Коктейль с дымом и загадкой", "Mg"),
            ("Тёплое какао, приготовленное с любовью", "Cg"),
            ("Чистая родниковая вода", "In"),
        ],
    },
    {
        "text": "Чем вы категорически не готовы поступиться ради денег?",
        "options": [
            ("Статусом и репутацией", "A"),
            ("Чувственностью и вкусом", "S"),
            ("Смелостью говорить не как все", "B"),
            ("Внутренним спокойствием и достоинством", "F"),
        ],
    },
    {
        "text": "Как бренд празднует успех?",
        "options": [
            ("Запуском того, что докажет всем", "G"),
            ("Посиделками с близкими без пафоса", "Fr"),
            ("Работой над следующим необычным проектом", "Cr"),
            ("Вечеринкой с шутками до утра", "Pl"),
        ],
    },
    {
        "text": "Что чаще всего говорит клиент после покупки?",
        "options": [
            ("«Это открыло мне новый мир»", "Ex"),
            ("«Со мной как будто что-то произошло»", "Mg"),
            ("«Наконец кто-то обо мне позаботился»", "Cg"),
            ("«Всё оказалось именно так, как обещали — просто и честно»", "In"),
        ],
    },
]

# ---------------------------------------------------------------------------
# 12 архетипов по Юнгу
# ---------------------------------------------------------------------------

ARCHETYPES = {
    "A": {
        "name": "Правитель",
        "desc": (
            "Ваш бренд — это наследие и порядок. Он не гонится за трендами, "
            "потому что сам их переживёт. Дорогой, но никогда не кричащий об "
            "этом — статус читается в деталях, а не в громкости."
        ),
        "colors": [
            ("#0B1F3A", "тёмно-синий"),
            ("#C9A227", "старое золото"),
            ("#6E1423", "бордо"),
            ("#F5F0E6", "кремовый"),
        ],
        "fonts": ["Playfair Display", "Cormorant / EB Garamond"],
        "prompt": (
            "Luxury heraldic emblem logo, dark navy and antique gold color "
            "palette, classic serif typography, symmetrical crest-like "
            "composition, timeless regal elegance, minimal ornamental "
            "details, flat vector, on cream background"
        ),
    },
    "S": {
        "name": "Любовник",
        "desc": (
            "Бренд, который не продаёт — он притягивает. Работает через "
            "чувственность, тайну и обещание близости. Клиент выбирает его "
            "не разумом, а первым впечатлением."
        ),
        "colors": [
            ("#0D0D0D", "чёрный"),
            ("#B76E79", "розовое золото"),
            ("#7A0C2E", "тёмно-красный"),
            ("#E8C4C4", "пудровый"),
        ],
        "fonts": ["Bodoni Moda", "Italiana"],
        "prompt": (
            "Sensual luxury logo mark, black and rose gold color palette, "
            "elegant italic serif typography, fluid curved lines suggesting "
            "intimacy, minimal seductive elegance, flat vector, on black "
            "background"
        ),
    },
    "B": {
        "name": "Бунтарь",
        "desc": (
            "Ломает правила красиво. Дерзость, поданная с безупречным "
            "вкусом — не хаос ради хаоса, а точный удар по привычным "
            "ожиданиям ниши."
        ),
        "colors": [
            ("#0D0D0D", "чёрный"),
            ("#FF3B30", "алый акцент"),
            ("#E5E5E5", "светло-серый"),
        ],
        "fonts": ["Anton (Google Fonts)", "Inter"],
        "prompt": (
            "Bold rebellious logo, black background with one striking red "
            "accent, brutalist display typography, asymmetric confident "
            "composition, edgy yet refined, flat vector, on black background"
        ),
    },
    "F": {
        "name": "Мудрец",
        "desc": (
            "Сила в сдержанности и знании. Ничего лишнего — только суть, "
            "пространство и воздух. Такой бренд не убеждает, он просто есть, "
            "и этого достаточно."
        ),
        "colors": [
            ("#E8E4DC", "бежевый"),
            ("#A9A9A9", "серый"),
            ("#FFFFFF", "белый"),
            ("#1A1A1A", "почти чёрный"),
        ],
        "fonts": ["Jost (Google Fonts)", "Inter"],
        "prompt": (
            "Minimalist quiet wisdom logo, beige gray and white color "
            "palette, thin refined sans-serif typography, generous negative "
            "space, understated elegance, flat vector, on light background"
        ),
    },
    "G": {
        "name": "Герой",
        "desc": (
            "Амбиция и статус через достижения. Бренд для тех, кто хочет "
            "быть первым, а не одним из. Символика силы, движения вперёд и "
            "заслуженной победы."
        ),
        "colors": [
            ("#0D0D0D", "чёрный"),
            ("#C9A227", "золото"),
            ("#B3121B", "алый"),
        ],
        "fonts": ["Archivo Black (Google Fonts)", "Inter Bold"],
        "prompt": (
            "Powerful winner's emblem logo, black gold and red color "
            "palette, bold strong typography, dynamic upward composition, "
            "status and achievement symbolism, flat vector, on black "
            "background"
        ),
    },
    "Fr": {
        "name": "Свой парень",
        "desc": (
            "Бренд как хороший друг — простой, тёплый, без пафоса и "
            "дистанции. Ему верят не потому что он статусный, а потому что "
            "с ним по-настоящему."
        ),
        "colors": [
            ("#E8A87C", "персиковый"),
            ("#FFF4E0", "кремовый"),
            ("#F2C14E", "тёплый жёлтый"),
            ("#4A7C6B", "мягкий зелёный"),
        ],
        "fonts": ["Nunito / Quicksand", "Inter"],
        "prompt": (
            "Warm friendly brand logo, peach cream and soft green color "
            "palette, rounded approachable sans-serif typography, simple "
            "welcoming mark, no luxury cues, flat vector, on cream "
            "background"
        ),
    },
    "Cr": {
        "name": "Творец",
        "desc": (
            "Бренд живёт фантазией и самовыражением. Он не боится "
            "нестандартных сочетаний — потому что настоящая ценность "
            "рождается там, где правила отходят в сторону."
        ),
        "colors": [
            ("#2FA8A0", "бирюзовый"),
            ("#E8703A", "оранжевый"),
            ("#E85D9E", "розовый"),
            ("#FBF3E7", "кремовый"),
        ],
        "fonts": ["Caveat (рукописный)", "Inter"],
        "prompt": (
            "Creative expressive brand logo, vibrant teal orange and pink "
            "color palette, organic hand-drawn typography mixed with clean "
            "sans-serif, playful artistic composition, flat vector, on "
            "cream background"
        ),
    },
    "Pl": {
        "name": "Шут",
        "desc": (
            "Бренд не воспринимает себя слишком серьёзно. Он заряжает "
            "энергией, шутит и приглашает повеселиться вместе — и именно в "
            "этом его сила."
        ),
        "colors": [
            ("#F4C542", "жёлтый"),
            ("#FF6F91", "розовый"),
            ("#3DCCC7", "бирюзовый"),
            ("#FFFFFF", "белый"),
        ],
        "fonts": ["Baloo 2 / Fredoka", "Inter"],
        "prompt": (
            "Playful fun brand logo, bright yellow pink and turquoise color "
            "palette, bold rounded display typography, energetic joyful "
            "composition, flat vector, on white background"
        ),
    },
    "Ex": {
        "name": "Искатель",
        "desc": (
            "Свобода, подлинность, жажда нового опыта. Бренд для тех, кто "
            "не сидит на месте и ищет настоящее, а не витрину."
        ),
        "colors": [
            ("#C1663B", "терракотовый"),
            ("#8A9A5B", "хаки"),
            ("#D9C8A9", "песочный"),
            ("#3B3A36", "тёмный уголь"),
        ],
        "fonts": ["Big Shoulders / Barlow Condensed", "Inter"],
        "prompt": (
            "Adventurous explorer brand logo, terracotta khaki and sand "
            "color palette, rugged condensed typography, compass or "
            "journey-inspired mark, authentic outdoor feel, flat vector, on "
            "textured cream background"
        ),
    },
    "Mg": {
        "name": "Маг",
        "desc": (
            "Трансформация и ощущение чуда. Бренд обещает не просто вещь, а "
            "перемену состояния того, кто ею владеет — «до» и «после»."
        ),
        "colors": [
            ("#2D1B4E", "тёмно-фиолетовый"),
            ("#0D0D0D", "чёрный"),
            ("#C0A875", "тёплое золото"),
            ("#0F5C4A", "изумрудный"),
        ],
        "fonts": ["Cinzel Decorative", "Inter"],
        "prompt": (
            "Mystical transformative brand logo, deep purple black and gold "
            "color palette, elegant alchemical symbolism, subtle glow or "
            "radiant mark, sense of magic and metamorphosis, flat vector, "
            "on black background"
        ),
    },
    "Cg": {
        "name": "Опекун",
        "desc": (
            "Забота, надёжная защита, внимание к комфорту другого. Бренд, "
            "который ставит благополучие клиента выше всего остального."
        ),
        "colors": [
            ("#D8A48F", "пудровый терракот"),
            ("#F5EFE6", "кремовый"),
            ("#9CAF88", "шалфей"),
            ("#E9C4C0", "пудрово-розовый"),
        ],
        "fonts": ["Lora", "Inter"],
        "prompt": (
            "Warm caregiving brand logo, soft terracotta sage green and "
            "cream color palette, gentle rounded serif typography, "
            "nurturing protective symbolism, flat vector, on cream "
            "background"
        ),
    },
    "In": {
        "name": "Простодушный",
        "desc": (
            "Чистота, простота, оптимизм и доверие с первого взгляда. "
            "Бренд без второго дна — то, что видишь, то и получаешь."
        ),
        "colors": [
            ("#FFFFFF", "белый"),
            ("#BFE3F2", "светло-голубой"),
            ("#FDE9A8", "мягкий жёлтый"),
            ("#E8E8E8", "светло-серый"),
        ],
        "fonts": ["Poppins Light / Quicksand", "Inter"],
        "prompt": (
            "Pure innocent brand logo, white sky blue and soft yellow color "
            "palette, clean simple sans-serif typography, minimal "
            "optimistic mark, light and airy feel, flat vector, on white "
            "background"
        ),
    },
}

# ---------------------------------------------------------------------------
# Хранилище состояния квиза по пользователю (в памяти — этого достаточно для
# лид-магнита; при желании потом заменить на Redis/БД)
# ---------------------------------------------------------------------------

user_state: dict[int, dict] = {}


def contact_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Написать в Telegram", url=TELEGRAM_CONTACT_URL)],
            [InlineKeyboardButton(text="Написать в MAX", url=MAX_CONTACT_URL)],
        ]
    )


def question_keyboard(q_index: int) -> InlineKeyboardMarkup:
    options = QUESTIONS[q_index]["options"]
    rows = [
        [InlineKeyboardButton(text=text, callback_data=f"ans:{q_index}:{code}")]
        for text, code in options
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Начать", callback_data="start_quiz")]]
    )


def restart_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Пройти заново", callback_data="start_quiz")]]
    )


def compute_result(answers: list[str]) -> str:
    tally: dict[str, int] = {}
    for code in answers:
        tally[code] = tally.get(code, 0) + 1
    best_code = max(ARCHETYPES.keys(), key=lambda c: tally.get(c, 0))
    return best_code


def generate_palette_image(colors: list[tuple[str, str]]) -> bytes:
    """Рисует ряд цветных квадратиков-образцов палитры и возвращает PNG-байты."""
    swatch_size = 160
    width = swatch_size * len(colors)
    image = Image.new("RGB", (width, swatch_size), "#FFFFFF")
    draw = ImageDraw.Draw(image)
    for i, (hexv, _label) in enumerate(colors):
        x0 = i * swatch_size
        draw.rectangle([x0, 0, x0 + swatch_size, swatch_size], fill=hexv)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def format_caption(code: str) -> str:
    a = ARCHETYPES[code]
    colors_lines = "\n".join(f"{hexv} — {label}" for hexv, label in a["colors"])
    return (
        f"<b>Архетип вашего бренда: {a['name']}</b>\n\n"
        f"{a['desc']}\n\n"
        f"<b>Палитра</b>\n{colors_lines}"
    )


def format_result_body(code: str) -> str:
    a = ARCHETYPES[code]
    fonts_lines = "\n".join(f"• {f}" for f in a["fonts"])
    return (
        f"<b>Шрифты</b>\n{fonts_lines}\n\n"
        f"<b>Промт для генерации логотипа нейросетью</b>\n"
        f"<code>{a['prompt']}</code>\n\n"
        f"Допишите в начало или конец промта название бренда и известные вам "
        f"характеристики будущего логотипа (символ, форма, отрасль, надпись) — "
        f"если они уже есть. Это сделает результат точнее.\n\n"
        f"— — —\n"
        f"<b>Хотите не догадываться, а точно попасть в образ?</b>\n"
        f"Разбор проекта: 1–2 часа созвона, разбираем архетип «{a['name']}» и "
        f"как встроить его в айдентику, палитру и логотип именно вашего "
        f"бренда. Время созвона — удобное вам.\n\n"
        f"−20% по этому квизу — напишите кодовое слово «{CODE_WORD}», и я "
        f"сразу закреплю скидку."
    )


bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user_state.pop(message.from_user.id, None)
    intro = (
        "<b>Какой архетип у вашего бренда?</b>\n\n"
        "12 простых вопросов — и вы получите архетип бренда по классической "
        "модели Юнга (от Правителя до Простодушного), палитру, шрифты и "
        "готовый промт для генерации логотипа нейросетью.\n\n"
        f"<i>{DISCLAIMER}</i>"
    )
    await message.answer(intro, reply_markup=start_keyboard())


@dp.callback_query(F.data == "start_quiz")
async def start_quiz(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    user_state[user_id] = {"index": 0, "answers": []}
    await ask_question(callback, 0)
    await callback.answer()


async def ask_question(callback: CallbackQuery, index: int) -> None:
    q = QUESTIONS[index]
    text = f"Вопрос {index + 1} из {len(QUESTIONS)}\n\n{q['text']}"
    await callback.message.answer(text, reply_markup=question_keyboard(index))


@dp.callback_query(F.data.startswith("ans:"))
async def handle_answer(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    _, q_index_str, code = callback.data.split(":")
    q_index = int(q_index_str)

    state = user_state.setdefault(user_id, {"index": 0, "answers": []})
    state["answers"].append(code)
    next_index = q_index + 1

    await callback.answer()

    if next_index < len(QUESTIONS):
        state["index"] = next_index
        await ask_question(callback, next_index)
    else:
        result_code = compute_result(state["answers"])
        archetype = ARCHETYPES[result_code]

        palette_bytes = generate_palette_image(archetype["colors"])
        palette_photo = BufferedInputFile(palette_bytes, filename="palette.png")
        await callback.message.answer_photo(
            palette_photo, caption=format_caption(result_code)
        )

        await callback.message.answer(
            format_result_body(result_code), reply_markup=contact_keyboard()
        )
        await callback.message.answer(
            "Хотите пройти ещё раз?", reply_markup=restart_keyboard()
        )
        user_state.pop(user_id, None)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
