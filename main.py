from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication, Session
from graia.application.message.chain import MessageChain
import asyncio

from graia.broadcast.interrupt import InterruptControl
from graia.application.message.elements.internal import Plain, At, Voice, Image, Xml
from graia.application.friend import Friend
from graia.application.group import Group, Member
import subprocess
from model.command import Command
import yaml
import os


if __name__ == '__main__':
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f.read())


loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)

app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host="{}:{}".format(
            config['connect_mirai']['host'],
            config['connect_mirai']['port']),  # 填入 httpapi 服务运行的地址
        authKey=config['connect_mirai']['authKey'],  # 填入 authKey
        account=config['connect_mirai']['account'],  # 机器人的 qq 号

        # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
        websocket=config['connect_mirai']['websocket']
    )
)
inc = InterruptControl(bcc)


async def exec_command(msg, some, *member):
    message = str(Command(msg, config))
    send_message = MessageChain.create([Plain(message)])
    if member[0] != ():
        await app.sendGroupMessage(some, send_message)
    else:
        await app.sendFriendMessage(some, send_message)


async def judge(msg, some, *member):
    if msg.startswith("执行指令 "):
        if member == () or member[0].id == config['bot']['master']:
            await exec_command(msg, some, member)
        else:
            await app.sendGroupMessage(some, MessageChain.create([Plain(config['feedback']['permission_denied'])]))


@bcc.receiver("FriendMessage")
async def friend_message_listener(
    app: GraiaMiraiApplication,
    friend: Friend,
    message: MessageChain,
):
    await judge(message.asDisplay(), friend)


@bcc.receiver("GroupMessage")
async def group_message_listener(
    message: MessageChain,
    app: GraiaMiraiApplication,
    group: Group,
    member: Member,
):
    await judge(message.asDisplay(), group, member)

app.launch_blocking()
