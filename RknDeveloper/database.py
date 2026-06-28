# (c) @ᴀɴᴏɴʏᴍᴏᴜꜱ
# Anonymous Developer 
# Telegram Channel @ᴀɴᴏɴʏᴍᴏᴜꜱ

"""
Apache License 2.0
Copyright (c) 2022 @RknDeveloper
"""

# database imports
import motor.motor_asyncio, datetime, pytz

# bots imports
from configs import rkn1

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.user
        self.chat = self.db.chat
        self.settings = self.db.settings
        
    def new_user(self, id):
        return dict(_id=int(id))

    async def add_user(self, b, m):
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = self.new_user(u.id)
            await self.col.insert_one(user)            
            await self.send_user_log(b, u)

    async def is_user_exist(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.col.delete_many({'_id': int(user_id)})
    
    async def send_user_log(self, b, u):
        if rkn1.LOG_CHANNEL is not None:
            try:
                uname = f"@{u.username}" if u.username else "No username"
                await b.send_message(
                    rkn1.LOG_CHANNEL,
                    f"**--Nᴇᴡ Uꜱᴇʀ--**\n\nUꜱᴇʀ: {u.mention}\nIᴅ: `{u.id}`\nUɴ: {uname}\n\nBy: {b.mention}"
                )
            except Exception:
                pass
        
    async def add_chat(self, b, m):
        if not await self.is_chat_exist(m.chat.id):
            chat = self.new_user(m.chat.id)
            await self.chat.insert_one(chat)            
            await self.send_chat_log(b, m)

    async def is_chat_exist(self, id):
        user = await self.chat.find_one({'_id': int(id)})
        return bool(user)

    async def total_chats_count(self):
        count = await self.chat.count_documents({})
        return count

    async def get_all_chats(self):
        all_users = self.chat.find({})
        return all_users

    async def delete_chat(self, user_id):
        await self.chat.delete_many({'_id': int(user_id)})
    
    async def send_chat_log(self, b, m):
        if rkn1.LOG_CHANNEL is not None:
            try:
                uname = f"@{m.chat.username}" if m.chat.username else "No username"
                await b.send_message(
                    rkn1.LOG_CHANNEL,
                    f"**--Nᴇᴡ Cʜᴀᴛ--**\n\nCʜᴀᴛ: {m.chat.title}\nIᴅ: `{m.chat.id}`\nUɴ: {uname}\n\nBy: {m.from_user.mention} & {b.mention}"
                )
            except Exception:
                pass

    # ── Sticker pack ────────────────────────────────────────────────────────
    async def get_sticker_pack(self):
        doc = await self.settings.find_one({'_id': 'sticker_pack'})
        return doc.get('pack_name') if doc else None

    async def set_sticker_pack(self, pack_name):
        await self.settings.update_one(
            {'_id': 'sticker_pack'},
            {'$set': {'pack_name': pack_name}},
            upsert=True
        )

    async def remove_sticker_pack(self):
        await self.settings.delete_one({'_id': 'sticker_pack'})

    # ── Auto-approve toggle ──────────────────────────────────────────────────
    async def get_auto_approve(self) -> bool:
        doc = await self.settings.find_one({'_id': 'auto_approve'})
        return doc.get('enabled', False) if doc else False

    async def set_auto_approve(self, enabled: bool):
        await self.settings.update_one(
            {'_id': 'auto_approve'},
            {'$set': {'enabled': enabled}},
            upsert=True
        )

    # ── Custom buttons ───────────────────────────────────────────────────────
    async def get_buttons(self):
        """Returns list of dicts: [{'name': ..., 'url': ...}, ...]  (max 2)"""
        doc = await self.settings.find_one({'_id': 'custom_buttons'})
        return doc.get('buttons', []) if doc else []

    async def set_buttons(self, buttons: list):
        await self.settings.update_one(
            {'_id': 'custom_buttons'},
            {'$set': {'buttons': buttons}},
            upsert=True
        )

    async def remove_buttons(self):
        await self.settings.delete_one({'_id': 'custom_buttons'})

        
rkn_botz = Database(rkn1.DB_URL, rkn1.DB_NAME)

# @ᴀɴᴏɴʏᴍᴏᴜꜱ
