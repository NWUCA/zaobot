from nonebot.plugin import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment
from .data_source import should_fudu

fudu = on_message(priority=100)
@fudu.handle()
async def _(event: GroupMessageEvent):

    if not should_fudu(event.group_id, event.raw_message):
        return

    send_msg = Message()
    for seg in event.message:
        if seg.type == 'text':
            text = seg.data['text']
            if len(text) >= 2 and text[0] == '[' and text[-1] == ']':
                return
        elif seg.type == 'image':
            send_msg.append(MessageSegment(
                type=seg.type,
                data={'file': seg.data['url']},
            ))
        else:
            send_msg.append(seg.copy())
    await fudu.finish(send_msg)
