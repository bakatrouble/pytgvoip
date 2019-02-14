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


from collections import deque
from typing import Union, List, IO, Iterable

from tgvoip import VoIPOutgoingCall, VoIPIncomingCall, VoIPService
from tgvoip.base_call import VoIPCallBase


class VoIPFileStreamCallMixin(VoIPCallBase):
    def __init__(self, *args, **kwargs):
        super(VoIPFileStreamCallMixin, self).__init__(*args, **kwargs)
        self.input_files = deque()
        self.hold_files = deque()
        self.output_file = None
        self.ctrl.set_send_audio_frame_callback(self._read_frame)
        self.ctrl.set_recv_audio_frame_callback(self._write_frame)

    def __del__(self):
        self.clear_play_queue()
        self.clear_hold_queue()
        self.unset_output_file()

    def play(self, f: Union[IO, str]):
        if isinstance(f, str):
            f = open(f, 'rb')
        elif not hasattr(f, 'mode') or 'b' not in f.mode or not any(m in f.mode for m in 'rxa+'):
            print('file must be opened in binary reading/updating mode')
            return
        self.input_files.append(f)

    def play_on_hold(self, files: List[Union[IO, str]]):
        if not isinstance(files, (list, tuple, set)):
            print('list, tuple or set expected, got {}'.format(type(files)))
            return
        self.clear_hold_queue()
        for f in files:
            if isinstance(f, str):
                f = open(f, 'rb')
            elif not hasattr(f, 'mode') or 'b' not in f.mode or not any(m in f.mode for m in 'rxa+'):
                print('file must be opened in binary reading/updating mode')
                continue
            self.hold_files.append(f)

    def set_output_file(self, f: Union[IO, str]):
        if isinstance(f, str):
            f = open(f, 'wb')
        elif 'b' not in f.mode or not any(m in f.mode for m in 'wxa+'):
            print('file must be opened in binary writing/updating mode')
            return
        self.output_file = f

    def clear_play_queue(self):
        for f in self.input_files:
            f.close()
        self.input_files.clear()

    def clear_hold_queue(self):
        for f in self.hold_files:
            f.close()
        self.hold_files.clear()

    def unset_output_file(self):
        if self.output_file:
            self.output_file.close()
        self.output_file = None

    def _read_frame(self, length: int) -> bytes:
        frame = b''
        if len(self.input_files):
            frame = self.input_files[0].read(length)
            if len(frame) != length:
                self.input_files[0].close()
                self.input_files.popleft()
        elif len(self.hold_files):
            frame = self.hold_files[0].read(length)
            if len(frame) != length:
                self.hold_files[0].seek(0)
                self.hold_files.rotate(-1)
        return frame

    def _write_frame(self, frame: bytes) -> None:
        if self.output_file:
            self.output_file.write(frame)


class VoIPOutgoingFileStreamCall(VoIPFileStreamCallMixin, VoIPOutgoingCall):
    pass


class VoIPIncomingFileStreamCall(VoIPFileStreamCallMixin, VoIPIncomingCall):
    pass


class VoIPFileStreamService(VoIPService):
    incoming_call_class = VoIPIncomingFileStreamCall
    outgoing_call_class = VoIPOutgoingFileStreamCall
