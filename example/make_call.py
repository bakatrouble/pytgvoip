from tgvoip import VoIPServerConfig, VoIPFileStreamService
import pyrogram


VoIPServerConfig.set_bitrate_config(80000, 100000, 60000, 5000, 5000)
client = pyrogram.Client('session')
client.start()

voip_service = VoIPFileStreamService(client, receive_calls=False)
call = voip_service.start_call('@bakatrouble')
call.play('ochinchin.raw')
call.play_on_hold(['ochinchin.raw'])
client.idle()
