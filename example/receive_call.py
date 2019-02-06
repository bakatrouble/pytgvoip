import logging

import pyrogram

from tgvoip import VoIPServerConfig, VoIPService, PyrogramVoIPCall

logging.basicConfig(level=logging.INFO)


VoIPServerConfig.set_config({
    'audio_init_bitrate': 80000,
    'audio_max_bitrate': 100000,
    'audio_min_bitrate': 60000,
    'audio_bitrate_step_decr': 5000,
    'audio_bitrate_step_incr': 5000
})


client = pyrogram.Client('session', ipv6=True)
service = VoIPService(client)
client.start()


f = open('output.raw', 'wb')
f2 = open('ochinchin.raw', 'rb')


def write(frame):
    f.write(frame)


def read(length):
    return f2.read(length)


@service.on_incoming_call()
def process_call(call: PyrogramVoIPCall):
    call.ctrl.set_recv_audio_frame_callback(write)
    call.ctrl.set_send_audio_frame_callback(read)
    call.accept()


client.idle()
