"""Evaluate Python and GNU/Linux Code inside Telegram
Syntax: `.eval {PythonCode}`
        `.exec `{LinuxCode}`
"""
import asyncio
import io
import logging
import sys
import time
import traceback

from uniborg.util import admin_cmd, yaml_format

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.WARN
)


@borg.on(admin_cmd(pattern="eval"))
async def _(event):
    if event.fwd_from or event.via_bot_id:
        return
    await event.edit("`Processing...`")
    cmd = event.raw_text.split(" ", maxsplit=1)[1]
    reply_to_id = event.message.id
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(cmd, event)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"

    if event.chat_id not in borg._NOT_SAFE_PLACES:
        evaluation = borg.secure_text(evaluation)

    final_output = "⬤ **EVAL**: `{}` \n\n⬤ **RESULT**: \n`{}` \n".format(
        cmd, borg.secure_text(evaluation)
    )

    if len(final_output) > Config.MAX_MESSAGE_SIZE_LIMIT:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.txt"
            await borg.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption=cmd,
                reply_to=reply_to_id,
            )
            await event.delete()
    else:
        await event.edit(final_output)


async def aexec(code, event):
    p = lambda _x: print(yaml_format(_x))
    reply = await event.get_reply_message()
    exec(
        f"async def __aexec(event, reply, client, p): "
        + "".join(f"\n {l}" for l in code.split("\n"))
    )
    return await locals()["__aexec"](event, reply, event.client, p)


@borg.on(admin_cmd(pattern="exec"))
async def _(event):
    if event.fwd_from or event.via_bot_id:
        return
    PROCESS_RUN_TIME = 100
    await event.edit("`Processing...`")
    cmd = event.raw_text.split(" ", maxsplit=1)[1]
    reply_to_id = event.message.id
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    time.time() + PROCESS_RUN_TIME
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    e = stderr.decode()
    if not e:
        e = "No Error"
    o = stdout.decode()
    if not o:
        o = "`No Result Returned/False`"
    else:
        _o = o.split("\n")
        o = "`\n".join(_o)
    OUTPUT = f"**INPUT:**\n`{cmd}`\n__PID:__\n`{process.pid}`\n\n**ERROR:**\n`{borg.secure_text(e)}`\n**OUTPUT:**\n{borg.secure_text(o)}"
    if len(OUTPUT) > Config.MAX_MESSAGE_SIZE_LIMIT:
        with io.BytesIO(str.encode(OUTPUT)) as out_file:
            out_file.name = "exec.txt"
            await borg.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption=cmd,
                reply_to=reply_to_id,
            )
            await event.delete()
    await event.edit(OUTPUT)
