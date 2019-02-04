import os
from datetime import datetime
from time import sleep

import pyrogram
from pyrogram.api.types import UpdatePhoneCall, PhoneCallAccepted

from pyrogram_wrapper import PyrogramWrapper
from _tgvoip import VoIP


"""
Calls two users and connects them to each other
"""


def configure_voip(cnf):
    cnf['audio_init_bitrate'] = 80000
    cnf['audio_max_bitrate'] = 100000
    cnf['audio_min_bitrate'] = 60000
    cnf['audio_bitrate_step_decr'] = 5000
    cnf['audio_bitrate_step_incr'] = 5000
    return cnf


client = pyrogram.Client('session', 'app_id', 'app_hash', ipv6=True)
calls = PyrogramWrapper(client, configure_voip)

client.start()


class Calls:
    voip1 = calls.request_call('@username1')
    voip2 = calls.request_call('@username2')


Calls.voip1.play_on_hold(['hold.raw'])
Calls.voip2.play_on_hold(['hold.raw'])

Calls.voip1.storage['active'] = False
Calls.voip2.storage['active'] = False
ts = int(datetime.now().timestamp())


def check():
    if Calls.voip1.storage['active'] and Calls.voip2.storage['active']:
        Calls.voip1.set_output_file(f'output1-{ts}.raw')
        Calls.voip2.set_output_file(f'output2-{ts}.raw')
        while os.path.getsize(f'output1-{ts}.raw') < 10000 or os.path.getsize(f'output2-{ts}.raw') < 10000:
            # wait until both call recordings buffer at least 10k each
            sleep(.1)
        Calls.voip1.play(f'output2-{ts}.raw')
        Calls.voip2.play(f'output1-{ts}.raw')


@client.on_raw_update()
def process_raw_update(cl, update, users, chats):
    if isinstance(update, UpdatePhoneCall):
        pc = update.phone_call
        if isinstance(pc, PhoneCallAccepted):
            if pc.participant_id == Calls.voip1.get_other_id():
                Calls.voip1.storage['active'] = True
            else:
                Calls.voip2.storage['active'] = True
            check()


while Calls.voip1.get_call_state() < VoIP.CALL_STATE_ENDED and Calls.voip2.get_call_state() < VoIP.CALL_STATE_ENDED:
    sleep(1)

client.stop()
