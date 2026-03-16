import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatMemberStatus, ParseMode
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/your_channel")

PROXY_LINK = "tg://proxy?server=89.124.81.114&port=1488&secret=b924ebf8af227a940cdcec7606fb7d45"

dp = Dispatcher()


def kb_not_subscribed():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="📢 Подписаться на канал", url=CHANNEL_LINK))
    kb.row(InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_sub"))
    return kb.as_markup()


def kb_proxy():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🔌 Подключить прокси", url=PROXY_LINK))
    return kb.as_markup()


async def is_user_subscribed(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in {
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR,
        }
    except Exception as e:
        logging.exception("Subscription check failed: %s", e)
        return False


@dp.message(CommandStart())
async def cmd_start(message: Message, bot: Bot) -> None:
    subscribed = await is_user_subscribed(bot, message.from_user.id)

    if subscribed:
        await message.answer(
            "✅ Подписка подтверждена.\n\n"
            "Нажми кнопку ниже, чтобы подключить прокси в Telegram.",
            reply_markup=kb_proxy(),
        )
    else:
        await message.answer(
            "Для того чтобы воспользоваться ботом и получить доступ к прокси, "
            "подпишись на канал 17teen Exchange.",
            reply_markup=kb_not_subscribed(),
        )


@dp.callback_query(F.data == "check_sub")
async def callback_check_sub(callback: CallbackQuery, bot: Bot) -> None:
    await callback.answer()

    subscribed = await is_user_subscribed(bot, callback.from_user.id)

    if callback.message is None:
        return

    if subscribed:
        await callback.message.edit_text(
            "✅ Подписка подтверждена.\n\n"
            "Нажми кнопку ниже, чтобы подключить прокси в Telegram.",
            reply_markup=kb_proxy(),
        )
    else:
        await callback.message.edit_text(
            "Для того чтобы воспользоваться ботом и получить доступ к прокси, "
            "подпишись на канал 17teen Exchange.",
            reply_markup=kb_not_subscribed(),
        )


async def main() -> None:
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не задан")

    if not CHANNEL_ID:
        raise ValueError("CHANNEL_ID не задан")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())