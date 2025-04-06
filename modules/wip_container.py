# modules/wip_container.py

import asyncio
import aiocron
from telethon import events
from telethon.tl.types import ReplyKeyboardMarkup
from telethon.types import ReplyInlineMarkup
from service.bot import bot
from loguru import logger


# ID бота, з яким треба взаємодіяти (можеш зробити конфігурованим)
TARGET_BOT_ID = 1976201765  # або @your_bot_username


def start_module():
    logger.info("WIP module started")

    state = {
        "checked_mail": False,
        "claimed_mail": False,
        "claimed_reward": False,
    }

    @bot.on(events.NewMessage(chats=TARGET_BOT_ID))
    async def handle_bot_message(event):
        text = event.raw_text
        logger.info(f"📩 Bot says: {text[:50]}...")

        # --- 1. Check for Mail 📩🔴 button ---
        if (
            not state["checked_mail"]
            and event.buttons
            and "Main Menu" in event.raw_text
            and type(event.reply_markup) == ReplyKeyboardMarkup
        ):
            for i, row in enumerate(event.buttons):
                for j, btn in enumerate(row):
                    if "Mail 📩🔴" in btn.text:
                        logger.info(f"📬 Clicking 'Mail 📩🔴' button: {btn.text}")
                        await event.click(i, j)
                        return
                    else:
                        state["claimed_mail"] = True

            state["checked_mail"] = True

        # --- 2. Click 'Claim' inline button after Mail ---
        if (
            not state["claimed_mail"]
            and event.buttons
            and type(event.reply_markup) == ReplyInlineMarkup
        ):
            for i, row in enumerate(event.buttons):
                for j, btn in enumerate(row):
                    if "Claim" in btn.text:
                        logger.info(f"🎁 Clicking '{btn.text}'")
                        await event.click(i, j)
                        return

            state["claimed_mail"] = True

        # --- 3. Click 'Rewards' button ---
        if (
            state["checked_mail"]
            and not state["claimed_reward"]
            and event.buttons
            and type(event.reply_markup) == ReplyKeyboardMarkup
        ):
            for i, row in enumerate(event.buttons):
                for j, btn in enumerate(row):
                    if "Rewards" in btn.text:
                        logger.info(f"🏆 Clicking '{btn.text}'")
                        await event.click(i, j)
                        return

        # --- 4. Inside Rewards → Click 'Daily Bonus' ---
        if (
            not state["claimed_reward"]
            and event.buttons
            and type(event.reply_markup) == ReplyKeyboardMarkup
        ):
            for i, row in enumerate(event.buttons):
                for j, btn in enumerate(row):
                    if "Daily" in btn.text:
                        logger.info(f"💰 Clicking '{btn.text}'")
                        await event.click(i, j)
                        return

        # --- 5. After Bonus claimed → Click 'Back' ---
        if not state["claimed_reward"] and (event.buttons or "already" in event.raw_text):
            logger.info(f"🔙 Clicking 'Back'")
            await bot.send_message(TARGET_BOT_ID, "Back 🔙")
            state["claimed_reward"] = True
            return

        # --- 6. Finished ---
        if state["checked_mail"] and state["claimed_reward"]:
            logger.info("✅ Flow completed. Back to main menu!")

    @bot.on(events.CallbackQuery)
    async def handle_inline_callback(event):
        logger.info(f"📲 Inline callback clicked: {event.data.decode(errors='ignore')}")
        await event.answer("👌")

    @bot.on(events.CallbackQuery)
    async def handle_inline_callback(event):
        logger.info(f"Inline button clicked: data={event.data.decode()}")
        await event.answer("👍")
