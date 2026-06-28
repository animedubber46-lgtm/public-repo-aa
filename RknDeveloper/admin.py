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

# pyrogram imports
from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from pyrogram.raw import functions

# bots imports
import os, sys, time, asyncio, logging, datetime, pytz
from RknDeveloper.database import rkn_botz
from configs import rkn1

logger = logging.getLogger(__name__)


@Client.on_message(filters.command(["stats", "status"]) & filters.user(rkn1.ADMIN))
async def get_stats(bot, message):
    total_users = await rkn_botz.total_users_count()
    total_chats = await rkn_botz.total_chats_count()
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - bot.uptime))    
    start_t = time.time()
    rkn = await message.reply('**ᴘʀᴏᴄᴇssɪɴɢ.....**')    
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    pack_name = await rkn_botz.get_sticker_pack()
    sticker_info = f"`{pack_name}`" if pack_name else "Not set"
    await rkn.edit(
        text=f"**--Bᴏᴛ Sᴛᴀᴛᴜꜱ--** \n\n"
             f"**⌚️ Bᴏᴛ Uᴩᴛɪᴍᴇ:** {uptime} \n"
             f"**🐌 Cᴜʀʀᴇɴᴛ Pɪɴɢ:** `{time_taken_s:.3f} ᴍꜱ` \n"
             f"**👭 Tᴏᴛᴀʟ Uꜱᴇʀꜱ:** `{total_users}`\n"
             f"**💸 ᴛᴏᴛᴀʟ Chats:** `{total_chats}`\n"
             f"**🎭 Sᴛɪᴄᴋᴇʀ Pᴀᴄᴋ:** {sticker_info}"
    )


@Client.on_message(filters.private & filters.command("restart") & filters.user(rkn1.ADMIN))
async def restart_bot(b, m):
    rkn = await b.send_message(text="**🔄 ᴘʀᴏᴄᴇssᴇs sᴛᴏᴘᴘᴇᴅ. ʙᴏᴛ ɪs ʀᴇsᴛᴀʀᴛɪɴɢ.....**", chat_id=m.chat.id)
    failed = 0
    success = 0
    deactivated = 0
    blocked = 0
    start_time = time.time()
    total_users = await rkn_botz.total_users_count()
    all_users = await rkn_botz.get_all_users()
    async for user in all_users:
        try:
            restart_msg = f"ʜᴇʏ, {(await b.get_users(user['_id'])).mention}\n\n**🔄 ᴘʀᴏᴄᴇssᴇs sᴛᴏᴘᴘᴇᴅ. ʙᴏᴛ ɪs ʀᴇsᴛᴀʀᴛɪɴɢ.....\n\n✅️ ʙᴏᴛ ɪs ʀᴇsᴛᴀʀᴛᴇᴅ. ɴᴏᴡ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴍᴇ.**"
            await b.send_message(user['_id'], restart_msg)
            success += 1
        except InputUserDeactivated:
            deactivated += 1
            await rkn_botz.delete_user(user['_id'])
        except UserIsBlocked:
            blocked += 1
            await rkn_botz.delete_user(user['_id'])
        except Exception as e:
            failed += 1
            await rkn_botz.delete_user(user['_id'])
            print(e)
            pass
        try:
            await rkn.edit(f"<u>ʀᴇsᴛᴀʀᴛ ɪɴ ᴩʀᴏɢʀᴇꜱꜱ:</u>\n\n• ᴛᴏᴛᴀʟ ᴜsᴇʀs: {total_users}\n• sᴜᴄᴄᴇssғᴜʟ: {success}\n• ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: {blocked}\n• ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: {deactivated}\n• ᴜɴsᴜᴄᴄᴇssғᴜʟ: {failed}")
        except FloodWait as e:
            await asyncio.sleep(e.value)
    completed_restart = datetime.timedelta(seconds=int(time.time() - start_time))
    await rkn.edit(f"ᴄᴏᴍᴘʟᴇᴛᴇᴅ ʀᴇsᴛᴀʀᴛ: {completed_restart}\n\n• ᴛᴏᴛᴀʟ ᴜsᴇʀs: {total_users}\n• sᴜᴄᴄᴇssғᴜʟ: {success}\n• ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: {blocked}\n• ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: {deactivated}\n• ᴜɴsᴜᴄᴄᴇssғᴜʟ: {failed}")
    os.execl(sys.executable, sys.executable, *sys.argv)


@Client.on_message(filters.command("broadcast") & filters.user(rkn1.ADMIN) & filters.reply)
async def broadcast_handler(bot: Client, m: Message):
    await bot.send_message(rkn1.LOG_CHANNEL, f"{m.from_user.mention} or {m.from_user.id} Iꜱ ꜱᴛᴀʀᴛᴇᴅ ᴛʜᴇ Bʀᴏᴀᴅᴄᴀꜱᴛ......")
    all_users = await rkn_botz.get_all_users()
    broadcast_msg = m.reply_to_message
    sts_msg = await m.reply_text("Bʀᴏᴀᴅᴄᴀꜱᴛ Sᴛᴀʀᴛᴇᴅ..!")
    done = 0
    failed = 0
    success = 0
    start_time = time.time()
    total_users = await rkn_botz.total_users_count()
    async for user in all_users:
        sts = await send_msg(user['_id'], broadcast_msg)
        if sts == 200:
            success += 1
        else:
            failed += 1
        if sts == 400:
            await rkn_botz.delete_user(user['_id'])
        done += 1
        if not done % 20:
            await sts_msg.edit(f"Bʀᴏᴀᴅᴄᴀꜱᴛ Iɴ Pʀᴏɢʀᴇꜱꜱ: \nTᴏᴛᴀʟ Uꜱᴇʀꜱ {total_users} \nCᴏᴍᴩʟᴇᴛᴇᴅ: {done} / {total_users}\nSᴜᴄᴄᴇꜱꜱ: {success}\nFᴀɪʟᴇᴅ: {failed}")
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(f"Bʀᴏᴀᴅᴄᴀꜱᴛ Cᴏᴍᴩʟᴇᴛᴇᴅ: \nCᴏᴍᴩʟᴇᴛᴇᴅ Iɴ `{completed_in}`.\n\nTᴏᴛᴀʟ Uꜱᴇʀꜱ {total_users}\nCᴏᴍᴩʟᴇᴛᴇᴅ: {done} / {total_users}\nSᴜᴄᴄᴇꜱꜱ: {success}\nFᴀɪʟᴇᴅ: {failed}")


@Client.on_message(filters.command("acceptall") & filters.user(rkn1.ADMIN) & filters.private)
async def accept_all_requests(bot: Client, m: Message):
    args = m.text.split()
    if len(args) < 2:
        return await m.reply_text(
            "**Usage:** `/acceptall <channel_id>`\n\n"
            "Example: `/acceptall -1001234567890`"
        )
    try:
        channel_id = int(args[1])
    except ValueError:
        return await m.reply_text("**Invalid channel ID.** Please provide a numeric channel ID.\n\nExample: `/acceptall -1001234567890`")

    processing = await m.reply_text("⏳ **Processing... Accepting all pending join requests.**")
    try:
        peer = await bot.resolve_peer(channel_id)
        await bot.invoke(
            functions.channels.HideAllChatJoinRequests(
                channel=peer,
                approved=True
            )
        )
        await processing.edit(
            f"✅ **Done!** All pending join requests for `{channel_id}` have been accepted.\n\n"
            f"ℹ️ New requests will **not** be auto-approved — users will only receive the bot message."
        )
    except Exception as e:
        await processing.edit(f"❌ **Error:** `{str(e)}`\n\nMake sure the bot is admin in that channel with **Invite Users** permission.")


@Client.on_message(filters.command("addsticker") & filters.user(rkn1.ADMIN) & filters.private)
async def add_sticker_pack(bot: Client, m: Message):
    args = m.text.split()
    if len(args) < 2:
        return await m.reply_text(
            "**Usage:** `/addsticker <sticker_pack_link_or_name>`\n\n"
            "You can use the full link or just the pack name:\n"
            "`/addsticker https://t.me/addstickers/MyPack`\n"
            "`/addsticker MyPack`"
        )
    raw = args[1].strip()
    if "t.me/addstickers/" in raw:
        pack_name = raw.rstrip("/").split("/")[-1]
    else:
        pack_name = raw
    verifying = await m.reply_text(f"🔍 Verifying sticker pack `{pack_name}`...")
    try:
        sticker_set = await bot.get_sticker_set(pack_name)
        await rkn_botz.set_sticker_pack(pack_name)
        await verifying.edit(
            f"✅ **Sticker pack saved!**\n\n"
            f"📦 **Pack:** `{pack_name}`\n"
            f"🎭 **Total stickers:** `{len(sticker_set.stickers)}`\n\n"
            f"A random sticker from this pack will now be sent to users when they request to join a channel."
        )
    except Exception as e:
        await verifying.edit(
            f"❌ **Error:** Could not find sticker pack `{pack_name}`.\n\n"
            f"`{str(e)}`\n\n"
            f"Make sure the pack link or name is correct."
        )


@Client.on_message(filters.command("rsticker") & filters.user(rkn1.ADMIN) & filters.private)
async def remove_sticker_pack(bot: Client, m: Message):
    pack_name = await rkn_botz.get_sticker_pack()
    if not pack_name:
        return await m.reply_text("ℹ️ No sticker pack is currently set.")
    await rkn_botz.remove_sticker_pack()
    await m.reply_text(
        f"✅ **Sticker pack removed.**\n\n"
        f"Removed pack: `{pack_name}`\n\n"
        f"Stickers will no longer be sent to users on join requests."
    )


@Client.on_message(filters.command("autoapproveon") & filters.user(rkn1.ADMIN) & filters.private)
async def auto_approve_on(bot: Client, m: Message):
    try:
        await rkn_botz.set_auto_approve(True)
        await m.reply_text(
            "✅ **Auto-Approve is now ON.**\n\n"
            "The bot will automatically accept every join request "
            "after sending the video message."
        )
    except Exception as e:
        await m.reply_text(f"❌ Error: {e}")


@Client.on_message(filters.command("autoapproveoff") & filters.user(rkn1.ADMIN) & filters.private)
async def auto_approve_off(bot: Client, m: Message):
    try:
        await rkn_botz.set_auto_approve(False)
        await m.reply_text(
            "🚫 **Auto-Approve is now OFF.**\n\n"
            "The bot will only send the video message. "
            "Join requests will remain pending."
        )
    except Exception as e:
        await m.reply_text(f"❌ Error: {e}")


@Client.on_message(filters.command("addbuttons") & filters.user(rkn1.ADMIN) & filters.private)
async def add_buttons(bot: Client, m: Message):
    usage = (
        "**Usage:** `/addbuttons Name1 | URL1 | Name2 | URL2`\n\n"
        "Add 1 or 2 custom buttons shown on join-request messages.\n"
        "Examples:\n"
        "`/addbuttons Get Video | https://t.me/yourchannel`\n"
        "`/addbuttons Get Video | https://t.me/ch1 | Join Channel | https://t.me/ch2`"
    )
    parts = m.text.split(None, 1)
    if len(parts) < 2 or not parts[1].strip():
        return await m.reply_text(usage)

    raw = [p.strip() for p in parts[1].split("|")]
    if len(raw) < 2 or len(raw) % 2 != 0:
        return await m.reply_text(
            "❌ **Invalid format.**\n\n"
            "Provide pairs of `Name | URL` separated by `|`.\n\n" + usage
        )

    buttons = []
    for i in range(0, min(len(raw), 4), 2):
        name = raw[i].strip()
        url  = raw[i + 1].strip()
        if not url.startswith("http"):
            return await m.reply_text(f"❌ Invalid URL: `{url}`\n\nURLs must start with `http://` or `https://`")
        buttons.append({'name': name, 'url': url})

    await rkn_botz.set_buttons(buttons)
    preview = "\n".join(f"  • [{b['name']}]({b['url']})" for b in buttons)
    await m.reply_text(
        f"✅ **{len(buttons)} button(s) saved!**\n\n{preview}\n\n"
        f"These will now appear on every join-request message.",
        disable_web_page_preview=True
    )


@Client.on_message(filters.command("removebuttons") & filters.user(rkn1.ADMIN) & filters.private)
async def remove_buttons(bot: Client, m: Message):
    existing = await rkn_botz.get_buttons()
    if not existing:
        return await m.reply_text("ℹ️ No custom buttons are currently set.")
    await rkn_botz.remove_buttons()
    await m.reply_text(
        "✅ **Custom buttons removed.**\n\n"
        "Join-request messages will now show the default Add-to-Channel/Group buttons."
    )


async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        logger.info(f"{user_id} : Dᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ")
        return 400
    except UserIsBlocked:
        logger.info(f"{user_id} : Bʟᴏᴄᴋᴇᴅ Tʜᴇ Bᴏᴛ")
        return 400
    except PeerIdInvalid:
        logger.info(f"{user_id} : Uꜱᴇʀ Iᴅ Iɴᴠᴀʟɪᴅ")
        return 400
    except Exception as e:
        logger.error(f"{user_id} : {e}")
        return 500


# @ᴀɴᴏɴʏᴍᴏᴜꜱ
