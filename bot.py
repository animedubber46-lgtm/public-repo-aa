# (c) @ᴀɴᴏɴʏᴍᴏᴜꜱ
# Anonymous Developer 
# Telegram Channel @ᴀɴᴏɴʏᴍᴏᴜꜱ

"""
Apache License 2.0
Copyright (c) 2022 @RknDeveloper

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

# extra imports
import time, os, logging, logging.config
from aiohttp import web
from datetime import datetime
from pytz import timezone

# pyrogram imports
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from pyrogram.types import (
    BotCommand,
    BotCommandScopeDefault,
    BotCommandScopeChat,
)

# bots imports
from RknDeveloper.web_support import web_server
from configs import rkn1

# logging print 
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)


USER_COMMANDS = [
    BotCommand("start", "Start the bot"),
]

ADMIN_COMMANDS = [
    BotCommand("start", "Start the bot"),
    BotCommand("stats", "Bot statistics"),
    BotCommand("broadcast", "Broadcast a message to all users"),
    BotCommand("restart", "Restart the bot"),
    BotCommand("acceptall", "Accept all pending join requests for a channel"),
    BotCommand("addsticker", "Add a sticker pack (sent on join requests)"),
    BotCommand("rsticker", "Remove the current sticker pack"),
    BotCommand("addbuttons", "Set custom buttons on join-request messages"),
    BotCommand("removebuttons", "Remove custom buttons from join-request messages"),
    BotCommand("autoapproveon", "Auto-accept every join request"),
    BotCommand("autoapproveoff", "Stop auto-accepting join requests"),
]


class Bot(Client):
    def __init__(self):
        super().__init__(
            "auto-approver",
            api_id=rkn1.API_ID,
            api_hash=rkn1.API_HASH,
            bot_token=rkn1.BOT_TOKEN,
            plugins=dict(root='RknDeveloper')
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username
        self.uptime = rkn1.BOT_UPTIME

        if rkn1.WEBHOOK:
            app = web.AppRunner(await web_server())
            await app.setup()
            bind_address = "0.0.0.0"
            await web.TCPSite(app, bind_address, rkn1.PORT).start()

        await self._set_bot_commands()

        logging.info(f"{me.first_name} Restarted.....")
        logging.info(rkn1.LOGO)

        for id in rkn1.ADMIN:
            try:
                await self.send_message(id, f"**__{me.first_name}  Restarted......__**")
            except:
                pass

        if rkn1.LOG_CHANNEL:
            try:
                curr = datetime.now(timezone("Asia/Kolkata"))
                date = curr.strftime('%d %B, %Y')
                time_ = curr.strftime('%I:%M:%S %p')
                await self.send_message(
                    rkn1.LOG_CHANNEL,
                    f"**__{me.mention} Iꜱ Rᴇsᴛᴀʀᴛᴇᴅ !!**\n\n"
                    f"📅 Dᴀᴛᴇ : `{date}`\n"
                    f"⏰ Tɪᴍᴇ : `{time_}`\n"
                    f"🌐 Tɪᴍᴇᴢᴏɴᴇ : `Asia/Kolkata`\n\n"
                    f"🉐 Vᴇʀsɪᴏɴ : `v{__version__} (Layer {layer})`"
                )
            except:
                print("Pʟᴇᴀꜱᴇ Mᴀᴋᴇ Tʜɪꜱ Iꜱ Aᴅᴍɪɴ Iɴ Yᴏᴜʀ Lᴏɢ Cʜᴀɴɴᴇʟ")

    async def _set_bot_commands(self):
        try:
            await self.set_bot_commands(USER_COMMANDS, scope=BotCommandScopeDefault())
            for admin_id in rkn1.ADMIN:
                try:
                    await self.set_bot_commands(ADMIN_COMMANDS, scope=BotCommandScopeChat(chat_id=admin_id))
                except Exception as e:
                    logging.warning(f"Could not set admin commands for {admin_id}: {e}")
            logging.info("Bot commands set successfully.")
        except Exception as e:
            logging.warning(f"Could not set bot commands: {e}")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot Stopped 🙄")


bot = Bot()
bot.run()


# @ᴀɴᴏɴʏᴍᴏᴜꜱ
