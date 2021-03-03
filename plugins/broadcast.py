# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available

• `{i}add <id/reply to list/none>`
    Add chat to database. Adds current chat if no id specified.

• `{i}rem <all/id/none>`
    Removes the specified chat (current chat if none specified), or all chats.

• `{i}broadcast <reply to msg>`
    Send the replied message to all chats in database.

• `{i}forward <reply to msg>`
     Forward the message to all chats in database.
"""
from . import *
import asyncio
import io


@ultroid_cmd(pattern="add ?(.*)")
async def broadcast_adder(event):
    if event.reply_to_msg_id:
        await event.edit("`Adding to db...`")
        previous_message = await event.get_reply_message()
        raw_text = previous_message.text
        lines = raw_text.split("\n")
        length = len(lines)
        for line_number in range(1, length - 2):
            channel_id = lines[line_number][4:-1]
            if not is_channel_added(channel_id):
                add_channel(channel_id)
        await event.edit("Channels added!")
        await asyncio.sleep(3)
        await event.delete()
        return
    chat_id = event.chat_id
    try:
        if int(chat_id) == Var.LOG_CHANNEL:
            return
    except BaseException:
        pass
    if not is_channel_added(chat_id):
        x = add_channel(chat_id)
        if x:
            await event.edit("`Added to database!`")
        else:
            await event.edit("Error")
        await asyncio.sleep(3)
        await event.delete()
    elif is_channel_added(chat_id):
        await event.edit("`Channel is already is database!`")
        await asyncio.sleep(3)
        await event.delete()


@ultroid_cmd(pattern="rem ?(.*)")
async def broadcast_remover(event):
    chat_id = event.pattern_match.group(1)
    if chat_id == "all":
        await event.edit("`Removing...`")
        udB.delete("BROADCAST")
        await event.edit("Database cleared.")
        return
    if is_channel_added(chat_id):
        rem_channel(chat_id)
        await event.edit("Removed from database")
        await asyncio.sleep(3)
        await event.delete()
    elif is_channel_added(event.chat_id):
        rem_channel(event.chat_id)
        await event.edit("Removed from database")
        await asyncio.sleep(3)
        await event.delete()
    elif not is_channel_added(event.chat_id):
        await event.edit("Channel is already removed from database. ")
        await asyncio.sleep(3)
        await event.delete()


@ultroid_cmd(pattern="listchannels")
async def list_all(event):
    x = await eor(event, "`Calculating...`")
    channels = get_channels()
    num = get_no_channels()
    if num == 0:
        return await eod(x, "No chats were added.", time=5)
    msg = "Channels in database:\n"
    for channel in channels:
        name = (await ultroid.get_entity(int(channel))).title
        msg += f"=> **{name}** [`{channel}`]\n"
    msg += f"\nTotal {get_no_channels()} channels."
    if len(msg) > 4095:
        with io.BytesIO(str.encode(msg)) as out_file:
            out_file.name = "channels.txt"
            await ultroid_bot.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption="Channels in database",
                reply_to=event,
            )
            await x.delete()
    else:
        await x.edit(msg)


@ultroid_cmd(pattern="forward ?(.*)")
async def forw(event):
    if event.fwd_from:
        return
    if not event.is_reply:
        await event.edit("Reply to a message to broadcast.")
        return
    channels = get_channels()
    await event.edit("Sending...")
    if get_no_channels() == 0:
        return await event.edit(f"Please add channels by using `{hndlr}add` in them.")
    error_count = 0
    sent_count = 0
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        previous_message.message
        previous_message.raw_text
    error_count = 0
    for channel in channels:
        try:
            await ultroid_bot.forward_messages(int(channel), previous_message)
            sent_count += 1
            await event.edit(
                f"Sent : {sent_count}\nError : {error_count}\nTotal : {len(channels)}",
            )
        except Exception as error:
            try:
                await ultroid_bot.send_message(
                    Var.LOG_CHANNEL, f"Error in sending at {channel}."
                )
                await ultroid_bot.send_message(Var.LOG_CHANNEL, "Error! " + str(error))
                if error == "The message cannot be empty unless a file is provided":
                    return await event.edit(
                        "For sending files, upload in Saved Messages and reply .forward to it."
                    )
            except BaseException:
                pass
            error_count += 1
            await event.edit(
                f"Sent : {sent_count}\nError : {error_count}\nTotal : {len(channels)}",
            )
    await event.edit(f"{sent_count} messages sent with {error_count} errors.")
    if error_count > 0:
        try:
            await ultroid_bot.send_message(Var.LOG_CHANNEL, f"{error_count} Errors")
        except BaseException:
            await event.edit("Set up log channel for checking errors.")


@ultroid_cmd(pattern="broadcast ?(.*)")
async def sending(event):
    if not event.is_reply:
        return await event.edit("Reply to a message to broadcast.")
    channels = get_channels()
    error_count = 0
    sent_count = 0
    if len(channels) == 0:
        return await event.edit(
            f"You haven't added any channels. Use `{hndlr}add` in them fist!"
        )
    await event.edit("Sending....")
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        if previous_message.sticker or previous_message.poll:
            await event.edit(f"Reply `{hndlr}forward` for stickers and polls.")
            return
        if (
            previous_message.gif
            or previous_message.audio
            or previous_message.voice
            or previous_message.video
            or previous_message.video_note
            or previous_message.contact
            or previous_message.game
            or previous_message.geo
            or previous_message.invoice
        ):
            await event.edit(f"Not supported. Try `{hndlr}forward`")
            return
        if not previous_message.web_preview and previous_message.photo:
            file = await ultroid_bot.download_file(previous_message.media)
            uploaded_doc = await ultroid_bot.upload_file(file, file_name="img.png")
            raw_text = previous_message.text
            for channel in channels:
                try:
                    if previous_message.photo:
                        await ultroid_bot.send_file(
                            int(channel),
                            InputMediaUploadedPhoto(file=uploaded_doc),
                            force_document=False,
                            caption=raw_text,
                            link_preview=False,
                        )

                    sent_count += 1
                    await event.edit(
                        f"Sent : {sent_count}\nError : {error_count}\nTotal : {len(channels)}",
                    )
                except Exception as error:
                    try:
                        await ultroid_bot.send_message(
                            Var.LOG_CHANNEL, f"Error in sending at {channel}."
                        )
                        await ultroid_bot.send_message(
                            Var.LOG_CHANNEL, "Error! " + str(error)
                        )
                        if (
                            error
                            == "The message cannot be empty unless a file is provided"
                        ):
                            return await event.edit(
                                f"For sending files, upload in Saved Messages and reply {hndlr}forward to in."
                            )
                    except BaseException:
                        pass
                    error_count += 1
                    await event.edit(
                        f"Sent : {sent_count}\nError : {error_count}\nTotal : {len(channels)}",
                    )
            await event.edit(f"{sent_count} messages sent with {error_count} errors.")
            if error_count > 0:
                try:
                    await ultroid_bot.send_message(
                        Var.LOG_CHANNEL, f"{error_count} Errors"
                    )
                except BaseException:
                    pass
        else:
            raw_text = previous_message.text
            for channel in channels:
                try:
                    await ultroid_bot.send_message(
                        int(channel), raw_text, link_preview=False
                    )
                    sent_count += 1
                    await event.edit(
                        f"Sent : {sent_count}\nError : {error_count}\nTotal : {len(channels)}",
                    )
                except Exception as error:
                    try:
                        await ultroid_bot.send_message(
                            Var.LOG_CHANNEL, f"Error in sending at {channel}."
                        )
                        await ultroid_bot.send_message(
                            Var.LOG_CHANNEL, "Error! " + str(error)
                        )
                        if (
                            error
                            == "The message cannot be empty unless a file is provided"
                        ):
                            return await event.edit(
                                f"For sending files, upload in Saved Messages and reply {hndlr}forward to in."
                            )
                    except BaseException:
                        pass
                    error_count += 1
                    await event.edit(
                        f"Sent : {sent_count}\nError : {error_count}\nTotal : {len(channels)}",
                    )
            await event.edit(f"{sent_count} messages sent with {error_count} errors.")
            if error_count > 0:
                try:
                    await ultroid_bot.send_message(
                        Var.LOG_CHANNEL, f"{error_count} Errors"
                    )
                except BaseException:
                    await event.edit("Set up log channel for checking errors.")