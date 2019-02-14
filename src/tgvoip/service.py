# PytgVoIP - Telegram VoIP Library for Python
# Copyright (C) 2019 bakatrouble <https://github.com/bakatrouble>
#
# This file is part of PytgVoIP.
#
# PytgVoIP is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PytgVoIP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with PytgVoIP.  If not, see <http://www.gnu.org/licenses/>.


from typing import Union

import pyrogram
from pyrogram import RawUpdateHandler
from pyrogram.api import types

from tgvoip.incoming_call import VoIPIncomingCall
from tgvoip.outgoing_call import VoIPOutgoingCall


class VoIPService:
    incoming_call_class = VoIPIncomingCall
    outgoing_call_class = VoIPOutgoingCall

    def __init__(self, client: pyrogram.Client, receive_calls=True):
        self.client = client
        self.incoming_call_handlers = []
        if receive_calls:
            client.add_handler(RawUpdateHandler(self.update_handler), -1)
        client.on_message()

    def get_incoming_call_class(self):
        return self.incoming_call_class

    def get_outgoing_call_class(self):
        return self.outgoing_call_class

    def on_incoming_call(self, func) -> callable:
        self.incoming_call_handlers.append(func)
        return func

    def start_call(self, user_id: Union[str, int]):
        return self.get_outgoing_call_class()(user_id, client=self.client)

    def update_handler(self, _, update, users, chats):
        if isinstance(update, types.UpdatePhoneCall):
            call = update.phone_call
            if isinstance(call, types.PhoneCallRequested):
                voip_call = self.get_incoming_call_class()(call, client=self.client)
                for handler in self.incoming_call_handlers:
                    callable(handler) and handler(voip_call)
        raise pyrogram.ContinuePropagation
