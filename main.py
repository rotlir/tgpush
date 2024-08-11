from typing import AsyncGenerator
import pyrogram
import asyncio
from pyrogram.enums.chat_type import ChatType
import requests
import functools
from pyrogram.enums import MessageMediaType

# -------------------------------------------------------------------------
# This is a config part of the script

API_ID = 0
API_HASH = ""

# topic your notifications will go to
#
# remember that if someone gets a link to this topic, they will be able to read your notifications
# use something secure as a name for your topic
# for example: "https://ntfy.sh/(@V<Tv"y4+\%f#6pQ!m#"
NTFY_TOPIC = ""

# default priority for your pushes
default_priority = "default"

# you can define custom priorities for different users or chats in these dictionaries
#
# by default user priorities override chat priorities
# (i.e. if a user with high priority sends a message to a chat with low priority,
# you will receive a notification with high priority)
#
# read more about priorities here: https://docs.ntfy.sh/publish/#message-priority
# you can either set a username or an ID as a key (don't add @ to usernames)

# True if you want user priorities to override chat priorities
override_priorities = True

user_priorities = {
    "mother": "max",
    123456: "low"
}

chat_priorities = {
    "work_chat": "max",
    -100123456: "low"
}

# list of usernames or IDs of users to be ignored
# for example ["user", 123456]
ignore_users_list = []
# list of usernames or IDs of chats/channels to be ignored
ignore_chats_list = []
# ignore messages from chats and channels
ignore_channels = True
ignore_chats = True
# chats and channels not to be ignored
ignore_exceptions = []


# -------------------------------------------------------------------------


app = pyrogram.client.Client("account", api_id=API_ID, api_hash=API_HASH)


def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))


last_media_group = ''

def filter_func(filter: pyrogram.filters.Filter, client: pyrogram.client.Client, update: pyrogram.types.Message) -> bool:
    if rgetattr(update, "from_user.username", None):
        if update.from_user.username in ignore_users_list:
            return False
    if update.from_user:
        if update.from_user.id in ignore_users_list:
            return False
    if update.chat:
        if (update.chat.type == pyrogram.enums.ChatType.CHANNEL and ignore_channels) or ((update.chat.type == pyrogram.enums.ChatType.GROUP or update.chat.type == pyrogram.enums.ChatType.SUPERGROUP) and ignore_chats):
            if update.chat.id not in ignore_exceptions or rgetattr(update, "chat.username", None) not in ignore_exceptions:
                return False
        if update.chat.id in ignore_chats_list or rgetattr(update, "chat.username", None) in ignore_chats_list:
            return False
    if update.service:
        return False
    return True


async def handle(client: pyrogram.client.Client, msg: pyrogram.types.Message):
    await asyncio.sleep(2)
    if getattr(msg, "from_user", None) == await app.get_me():
        return
    dialogs = app.get_dialogs()
    if not isinstance(dialogs, AsyncGenerator):
        return
    async for dialog in dialogs:
        if not isinstance(dialog, pyrogram.types.Dialog):
            continue
        if dialog.chat.id == msg.chat.id:
            print(f"unread: {dialog.unread_messages_count}")
            if dialog.unread_messages_count == 0:
                return
            break

    priority = default_priority
    skip = False
    skip_chat = False
    if rgetattr(msg, "chat.username", None) in list(chat_priorities.keys()):
        priority = chat_priorities[msg.chat.username]
        skip_chat = True
        if not override_priorities:
            skip = True
    if rgetattr(msg, "chat.id", None) in list(chat_priorities.keys()) and not skip_chat:
        priority = chat_priorities[msg.chat.id]
        if not override_priorities:
            skip = True
    if rgetattr(msg, "from_user.username", None) in list(user_priorities.keys()) and not skip:
        priority = user_priorities[msg.from_user.username]
        skip = True
    if rgetattr(msg, "from_user.id", None) in list(user_priorities.keys()) and not skip:
        priority = user_priorities[msg.from_user.id]

    text = ""
    deep_link = ""
    if msg.from_user:
        if msg.media and msg.media != MessageMediaType.WEB_PAGE_PREVIEW:
            text = f"{msg.from_user.full_name} sent "
        else:
            text = f"{msg.from_user.full_name}: {msg.text}"
        if msg.from_user.username and msg.chat.type == ChatType.PRIVATE:
            deep_link = f"tg://resolve?domain={msg.from_user.username}&post={msg.id}"
        elif msg.chat.type == ChatType.PRIVATE:
            deep_link = f"tg://user?id={msg.from_user.id}"
        else:
            deep_link = f"tg://privatepost?channel={str(msg.chat.id).removeprefix("-100")}&post={msg.id}"
    elif msg.chat:
        if msg.media and msg.media != MessageMediaType.WEB_PAGE_PREVIEW:
            text = f"{msg.chat.title} sent "
        else:
            text = f"{msg.chat.title}: {msg.text}"
        deep_link = f"tg://privatepost?channel={str(msg.chat.id).removeprefix("-100")}&post={msg.id}"

    if msg.media and msg.media != MessageMediaType.WEB_PAGE_PREVIEW:
        match msg.media:
            case MessageMediaType.AUDIO:
                text += "an audio"
            case MessageMediaType.VOICE:
                text += "a voice message"
            case MessageMediaType.VIDEO_NOTE:
                text += "a video note"
            case MessageMediaType.PHOTO:
                text += "a photo"
            case MessageMediaType.VIDEO:
                text += "a video"
            case MessageMediaType.STICKER:
                text += "a sticker"
            case MessageMediaType.ANIMATION:
                text += "an animation"
            case _:
                text += "a media"
        if msg.caption:
            text += f" with caption \"{msg.caption}\""
        elif msg.text:
            text += f" with text \"{msg.text}\""

    requests.post(NTFY_TOPIC,
                  data=text.encode("utf-8"),
                  headers={"Actions": f"view, Open chat, {deep_link}, clear=true"}
                  )


filter = pyrogram.filters.create(filter_func)
app.add_handler(pyrogram.handlers.message_handler.MessageHandler(handle, filter))
print("Starting script")
app.run()

