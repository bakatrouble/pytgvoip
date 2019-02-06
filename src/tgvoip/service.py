from typing import Union

import pyrogram
from pyrogram import RawUpdateHandler
from pyrogram.api import types

from tgvoip.incoming_call import VoIPIncomingCall
from tgvoip.outgoing_call import VoIPOutgoingCall
from .call import PyrogramVoIPCall


class VoIPService:
    def __init__(self, client: pyrogram.Client, receive_calls=True):
        self.client = client
        self.incoming_call_handlers = []
        if receive_calls:
            client.add_handler(RawUpdateHandler(self.update_handler), -1)
        client.on_message()

    def on_incoming_call(self, func) -> callable:
        self.incoming_call_handlers.append(func)
        return func

    def start_call(self, user_id: Union[str, int]):
        return VoIPOutgoingCall(user_id, client=self.client)

    def update_handler(self, _, update, users, chats):
        if isinstance(update, types.UpdatePhoneCall):
            call = update.phone_call
            if isinstance(call, types.PhoneCallRequested):
                voip_call = VoIPIncomingCall(call, client=self.client)
                for handler in self.incoming_call_handlers:
                    handler(voip_call)
        raise pyrogram.ContinuePropagation
