import pyrogram
from pyrogram import RawUpdateHandler
from pyrogram.api.types import UpdatePhoneCall

from pyrogram_wrapper import PyrogramWrapper
from _tgvoip import VoIP


client = pyrogram.Client('session', 'app_id', 'app_hash', ipv6=True)
calls = PyrogramWrapper(client)


def accept_call(cl, update, users, chats):
    if isinstance(update, UpdatePhoneCall):
        pc = update.phone_call
        voip = calls.get_voip(pc.id)
        if voip and voip.get_call_state() == VoIP.CALL_STATE_INCOMING:
            voip.accept()
            voip.play('input.raw')
            voip.then('input.raw')
            voip.play_on_hold(['input.raw'])
            voip.set_output_file('output.raw')


client.start()
client.add_handler(RawUpdateHandler(accept_call))
client.idle()
