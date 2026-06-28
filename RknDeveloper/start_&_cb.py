# (c) @ᴀɴᴏɴʏᴍᴏᴜꜱ
# Anonymous Developer 
# Telegram Channel @ᴀɴᴏɴʏᴍᴏᴜꜱ

"""
Apache License 2.0
Copyright (c) 2022 @RknDeveloper
"""

import random, logging

from pyrogram import filters, Client, enums
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import UserNotParticipant, PeerIdInvalid, UserIsBlocked, InputUserDeactivated
from pyrogram.raw.types import UpdateBotChatInviteRequester
from pyrogram.raw.functions.messages import GetStickerSet as RawGetStickerSet, SendMedia
from pyrogram.raw.types import (
    InputStickerSetShortName,
    InputDocument,
    InputMediaDocument,
)

from RknDeveloper.database import rkn_botz
from RknDeveloper.fs import force_sub
from configs import rkn1

logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────

def build_join_keyboard(bot_username: str, custom_buttons: list) -> InlineKeyboardMarkup:
    """Return the inline keyboard for the join-request message.
    Custom buttons (when set) replace the default Add-to-Channel/Group buttons."""
    if custom_buttons:
        rows = [[InlineKeyboardButton(b['name'], url=b['url'])] for b in custom_buttons]
    else:
        rows = [
            [InlineKeyboardButton(
                "✛ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Cʜᴀɴɴᴇʟ ࿇",
                url=f"https://t.me/{bot_username}?startchannel=Bots4Sale&admin=invite_users+manage_chat"
            )],
            [InlineKeyboardButton(
                "✛ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ ࿇",
                url=f"https://t.me/{bot_username}?startgroup=Bots4Sale&admin=invite_users+manage_chat"
            )],
        ]
    return InlineKeyboardMarkup(rows)


# ────────────────────────────────────────────────────────────────────────────
# Step 1 – Cache the user peer from the raw update (group=-1, runs FIRST)
# ────────────────────────────────────────────────────────────────────────────

@Client.on_raw_update(group=-1)
async def cache_join_request_peer(bot, update, users, chats):
    """
    Pyrofork's fetch_peers() skips 'min' users so their access_hash never
    reaches the session DB.  This handler fires before on_chat_join_request
    (group 0) and stores the access_hash directly from the raw users dict,
    making send_video / send_sticker work even for users who never started
    the bot.
    """
    try:
        if not isinstance(update, UpdateBotChatInviteRequester):
            return

        user_id  = update.user_id
        raw_user = users.get(user_id)
        if raw_user is None:
            return

        access_hash = getattr(raw_user, 'access_hash', 0) or 0
        username    = getattr(raw_user, 'username', None)
        phone       = getattr(raw_user, 'phone', None)

        # Force-store the peer, bypassing the min-user skip in fetch_peers
        await bot.storage.update_peers([
            (user_id, access_hash, "user", username, phone)
        ])
        logger.info(
            f"[join-req] cached peer {user_id} | "
            f"access_hash={'✓' if access_hash else '✗ (0)'} | "
            f"min={getattr(raw_user, 'min', False)}"
        )
    except Exception as e:
        logger.error(f"cache_join_request_peer: {e}")


# ────────────────────────────────────────────────────────────────────────────
# Step 2 – Send the video + sticker (group=0, runs AFTER the cache step)
# ────────────────────────────────────────────────────────────────────────────

@Client.on_chat_join_request()
async def approve_request(bot, m):
    user = m.from_user
    try:
        # DB ops are best-effort — a MongoDB failure must NOT block the video send
        try:
            await rkn_botz.add_chat(bot, m)
            await rkn_botz.add_user(bot, m)
        except Exception as db_err:
            logger.warning(f"[join-req] DB error (non-fatal): {db_err}")

        img = random.choice(rkn1.SURPRICE)

        try:
            buttons = await rkn_botz.get_buttons()
        except Exception:
            buttons = []
        keyboard = build_join_keyboard(bot.me.username, buttons)

        await bot.send_video(
            user.id,
            img,
            "\"𝐈𝐧𝐬𝐭𝐚𝐧𝐭 𝐕𝐢𝐫𝐚𝐥 𝐌𝐨𝐝𝐞𝐥 𝐕𝐢𝐝𝐞𝐨\n\n𝐂𝐥𝐢𝐜𝐤 𝐎𝐧 𝐁𝐞𝐥𝐨𝐰 𝐁𝐮𝐭𝐭𝐨𝐧 𝐓𝐨 𝐆𝐞𝐭 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐋𝐢𝐧𝐤 👇👇\"",
            reply_markup=keyboard
        )

        # ── Send sticker from the configured pack (if any) ──────────────
        pack_name = await rkn_botz.get_sticker_pack()
        if pack_name:
            try:
                # get_sticker_set() only returns metadata; use raw API for files
                r = await bot.invoke(
                    RawGetStickerSet(
                        stickerset=InputStickerSetShortName(short_name=pack_name),
                        hash=0
                    )
                )
                if r.documents:
                    doc  = random.choice(r.documents)
                    peer = await bot.resolve_peer(user.id)
                    await bot.invoke(
                        SendMedia(
                            peer=peer,
                            media=InputMediaDocument(
                                id=InputDocument(
                                    id=doc.id,
                                    access_hash=doc.access_hash,
                                    file_reference=doc.file_reference
                                )
                            ),
                            message="",
                            random_id=random.randint(0, 2**63)
                        )
                    )
            except Exception as e:
                logger.warning(f"[join-req] sticker send error for {user.id}: {e}")

        # ── Auto-approve if enabled ──────────────────────────────────────
        try:
            if await rkn_botz.get_auto_approve():
                await bot.approve_chat_join_request(m.chat.id, user.id)
        except Exception as e:
            logger.warning(f"[join-req] auto-approve error for {user.id}: {e}")

    except UserIsBlocked:
        logger.info(f"[join-req] user {user.id} blocked the bot")
    except InputUserDeactivated:
        logger.info(f"[join-req] user {user.id} account is deactivated")
    except PeerIdInvalid:
        logger.warning(
            f"[join-req] PeerIdInvalid for {user.id} — "
            "user may have extreme privacy settings (access_hash=0)"
        )
    except Exception as err:
        logger.error(f"[join-req] approve_request error for {user.id}: {err}")


# ────────────────────────────────────────────────────────────────────────────
# /start
# ────────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("start"))
async def start_commond(bot, m: Message):
    if m.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        await rkn_botz.add_chat(bot, m)
        return await m.reply_text(
            "**❣️ Hᴇʟʟᴏ {}!\n\nWʀɪᴛᴇ Mᴇ Pʀɪᴠᴀᴛᴇ Fᴏʀ Mᴏʀᴇ Dᴇᴛᴀɪʟs.**".format(m.from_user.first_name),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Pʀɪᴠᴀᴛᴇ", url=f"https://t.me/{bot.me.username}?start=start")
            ]])
        )
    await rkn_botz.add_user(bot, m)
    await force_sub(bot, m, rkn1.FORCE_SUB)
    await m.reply_photo(
        photo=rkn1.RKN_PIC,
        caption="**Hᴇy, {}!\n\nI'ᴍ Aɴ Aᴜᴛᴏ Aᴘᴘʀᴏᴠᴇ [Aᴅᴍɪɴ Jᴏɪɴ Rᴇǫᴜᴇsᴛs]({}) Bᴏᴛ.\nI Cᴀɴ Aᴘᴘʀᴏᴠᴇ Usᴇʀs Iɴ Cʜᴀɴɴᴇʟs & Gʀᴏᴜᴘs.Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Cʜᴀɴɴᴇʟ Aɴᴅ Gʀᴏᴜᴘ ᴀɴᴅ Pʀᴏᴍᴏᴛᴇ Mᴇ Tᴏ Aᴅᴍɪɴ Wɪᴛʜ Aᴅᴅ Mᴇᴍʙᴇʀs Pᴇʀᴍɪssɪᴏɴ.\n\n__Pᴏᴡᴇʀᴅ Bʏ : @ᴀɴᴏɴʏᴍᴏᴜꜱ__**".format(
            m.from_user.mention, "https://t.me/telegram/153"
        ),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("─シ｡Aʙᴏᴜᴛ｡シ─", callback_data="about")
        ],[
            InlineKeyboardButton("✛ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Cʜᴀɴɴᴇʟ ࿇", url=f"https://t.me/{bot.me.username}?startchannel=Bots4Sale&admin=invite_users+manage_chat")
        ],[
            InlineKeyboardButton("✛ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ ࿇", url=f"https://t.me/{bot.me.username}?startgroup=Bots4Sale&admin=invite_users+manage_chat")
        ]])
    )


@Client.on_callback_query(filters.regex("start"))
async def start_query(bot, cb: CallbackQuery):
    await cb.message.edit(
        "**Hᴇy, {}!\n\nI'ᴍ Aɴ Aᴜᴛᴏ Aᴘᴘʀᴏᴠᴇ [Aᴅᴍɪɴ Jᴏɪɴ Rᴇǫᴜᴇsᴛs]({}) Bᴏᴛ.\nI Cᴀɴ Aᴘᴘʀᴏᴠᴇ Usᴇʀs Iɴ Cʜᴀɴɴᴇʟs & Gʀᴏᴜᴘs.Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Cʜᴀɴɴᴇʟ Aɴᴅ Gʀᴏᴜᴘ ᴀɴᴅ Pʀᴏᴍᴏᴛᴇ Mᴇ Tᴏ Aᴅᴍɪɴ Wɪᴛʜ Aᴅᴅ Mᴇᴍʙᴇʀs Pᴇʀᴍɪssɪᴏɴ.\n\n__Pᴏᴡᴇʀᴅ Bʏ : @ᴀɴᴏɴʏᴍᴏᴜꜱ__**".format(
            cb.from_user.mention, "https://t.me/telegram/153"
        ),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("─シ｡Aʙᴏᴜᴛ｡シ─", callback_data="about")
        ],[
            InlineKeyboardButton("✛ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Cʜᴀɴɴᴇʟ ࿇", url=f"https://t.me/{bot.me.username}?startchannel=Bots4Sale&admin=invite_users+manage_chat")
        ],[
            InlineKeyboardButton("✛ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ ࿇", url=f"https://t.me/{bot.me.username}?startgroup=Bots4Sale&admin=invite_users+manage_chat")
        ]]),
        disable_web_page_preview=True
    )


@Client.on_callback_query(filters.regex('about'))
async def about_query(bot, update):
    await update.message.edit_text(
        text="""<b>» Mʏ Nᴀᴍᴇ: Aᴜᴛᴏ Jᴏɪɴ Rᴇǫᴜᴇsᴛ Bᴏᴛ
‣ Cʀᴇᴀᴛᴏʀ : <a href='tg://settings'>ᴛʜɪs Pᴇʀsᴏɴ</a>
‣ Dᴇᴠᴇʟᴏᴘᴇʀ : @ᴀɴᴏɴʏᴍᴏᴜꜱ
‣ Lɪʙʀᴀʀʏ : <a href='https://docs.pyrogram.org'>Pʏʀᴏɢʀᴀᴍ</a>
‣ Lᴀɴɢᴜᴀɢᴇ : <a href='https://www.python.org'>Pʏᴛʜᴏɴ 3</a>
‣ Dᴀᴛᴀ Bᴀsᴇ : <a href='https://www.mongodb.com/'>Mᴏɴɢᴏ Dʙ</a>
‣ Bᴜɪʟᴅ Sᴛᴀᴛᴜs : ᴠ2.1.1 [sᴛᴀʙʟᴇ]</b>""",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("→ Bᴀᴄᴋ", callback_data="start")
        ]])
    )


# @ᴀɴᴏɴʏᴍᴏᴜꜱ
