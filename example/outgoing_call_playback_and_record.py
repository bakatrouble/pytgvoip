from tgvoip import PyrogramVoIPCall
import pyrogram


client = pyrogram.Client('session', ipv6=True)
client.start()
call = PyrogramVoIPCall(client)
f = open('output.raw', 'wb')
f2 = open('ochinchin.raw', 'rb')


def write(frame):
    f.write(frame)


def read(length):
    return f2.read(length)


call.ctrl.set_recv_audio_frame_callback(write)
call.ctrl.set_send_audio_frame_callback(read)
call.start_outgoing_call('@bakatrouble')
client.idle()
