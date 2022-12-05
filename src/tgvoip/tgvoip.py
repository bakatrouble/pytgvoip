# PytgVoIP - Telegram VoIP Library for Python
# Copyright (C) 2020 bakatrouble <https://github.com/bakatrouble>
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

import json
import os
import sys
from datetime import datetime
from enum import Enum
from typing import Union, List

from _tgvoip import (
    NetType as _NetType,
    DataSaving as _DataSaving,
    CallState as _CallState,
    CallError as _CallError,
    Stats,
    Endpoint,
    VoIPController as _VoIPController,
    VoIPServerConfig as _VoIPServerConfig
)

from tgvoip.utils import get_real_elapsed_time


# docstring magic ahead


class NetType(Enum):
    """
    An enumeration of network types

    Members:
        * UNKNOWN = 0
        * GPRS = 1
        * EDGE = 2
        * NET_3G = 3
        * HSPA = 4
        * LTE = 5
        * WIFI = 6
        * ETHERNET = 7
        * OTHER_HIGH_SPEED = 8
        * OTHER_LOW_SPEED = 9
        * DIALUP = 10
        * OTHER_MOBILE = 11
    """

    UNKNOWN = _NetType.UNKNOWN
    GPRS = _NetType.GPRS
    EDGE = _NetType.EDGE
    NET_3G = _NetType.NET_3G
    HSPA = _NetType.HSPA
    LTE = _NetType.LTE
    WIFI = _NetType.WIFI
    ETHERNET = _NetType.ETHERNET
    OTHER_HIGH_SPEED = _NetType.OTHER_HIGH_SPEED
    OTHER_LOW_SPEED = _NetType.OTHER_LOW_SPEED
    DIALUP = _NetType.DIALUP
    OTHER_MOBILE = _NetType.OTHER_MOBILE


class CallState(Enum):
    """
    An enumeration of call states

    Members:
        * WAIT_INIT = 1
        * WAIT_INIT_ACK = 2
        * ESTABLISHED = 3
        * FAILED = 4
        * RECONNECTING = 5
        * HANGING_UP = 10
        * ENDED = 11
        * EXCHANGING_KEYS = 12
        * WAITING = 13
        * REQUESTING = 14
        * WAITING_INCOMING = 15
        * RINGING = 16
        * BUSY = 17
    """

    WAIT_INIT = _CallState.WAIT_INIT
    WAIT_INIT_ACK = _CallState.WAIT_INIT_ACK
    ESTABLISHED = _CallState.ESTABLISHED
    FAILED = _CallState.FAILED
    RECONNECTING = _CallState.RECONNECTING
    HANGING_UP = 10
    ENDED = 11
    EXCHANGING_KEYS = 12
    WAITING = 13
    REQUESTING = 14
    WAITING_INCOMING = 15
    RINGING = 16
    BUSY = 17


class DataSaving(Enum):
    """
    An enumeration of data saving modes

    Members:
        * NEVER = 0
        * MOBILE = 1
        * ALWAYS = 2
    """
    NEVER = _DataSaving.NEVER
    MOBILE = _DataSaving.MOBILE
    ALWAYS = _DataSaving.ALWAYS


class CallError(Enum):
    """
    An enumeration of call errors

    Members:
        * UNKNOWN = 0
        * INCOMPATIBLE = 1
        * TIMEOUT = 2
        * AUDIO_IO = 3
        * PROXY = 4
    """
    UNKNOWN = _CallError.UNKNOWN
    INCOMPATIBLE = _CallError.INCOMPATIBLE
    TIMEOUT = _CallError.TIMEOUT
    AUDIO_IO = _CallError.AUDIO_IO
    PROXY = _CallError.PROXY


class VoIPController(_VoIPController):
    """
    A wrapper around C++ wrapper for libtgvoip ``VoIPController``

    Args:
        persistent_state_file (``str``, *optional*): ?, empty to not use
        debug (``bool``, *optional*): Modifies logging behavior
        logs_dir (``str``, *optional*): Logs directory

    Class attributes:
        LIBTGVOIP_VERSION
            Used ``libtgvoip`` version

        CONNECTION_MAX_LAYER
            Maximum layer supported by used ``libtgvoip`` version

    Attributes:
        persistent_state_file:
            Value set in the constructor

        call_state_changed_handlers:
            ``list`` of call state change callbacks, callbacks receive a :class:`CallState` object as argument

        signal_bars_changed_handlers
            ``list`` of signal bars count change callbacks, callbacks receive an ``int`` object as argument
    """

    def __init__(self, persistent_state_file: str = '', debug=False, logs_dir='logs'):
        super().__init__(persistent_state_file)  # _VoIPController.__init__(self, persistent_state_file)
        self.debug = debug
        self.logs_dir = logs_dir
        self.start_time = 0
        self.send_audio_frame_callback = lambda length: b''
        self.recv_audio_frame_callback = lambda frame: ...
        self.call_state_changed_handlers = []
        self.signal_bars_changed_handlers = []
        self._init()

    @property
    def call_duration(self) -> int:
        """
        Current call duration in seconds as ``int`` if call was started, otherwise 0
        """
        return int(get_real_elapsed_time() - self.start_time) if self.start_time else 0

    def start(self):
        """
        Start the controller
        """
        super().start()

    def connect(self):
        """
        Start the call
        """
        super().connect()
    
    def stop(self):
        """
        Stop the controller
        """
        super().stop()

    def set_proxy(self, address: str, port: int = 1080, username: str = '', password: str = ''):
        """
        Set SOCKS5 proxy config

        Args:
            address (``str``): Proxy hostname or IP address
            port (``int``, *optional*): Proxy port
            username (``int``, *optional*): Proxy username
            password (``int``, *optional*): Proxy password

        Raises:
            :class:`ValueError` if :attr:`address` is empty
        """
        if not address:
            raise ValueError('address can\'t be empty')
        super().set_proxy(address, port, username, password)

    def set_encryption_key(self, key: bytes, is_outgoing: bool):
        """
        Set call auth key

        Args:
            key (``bytes``): Auth key, must be exactly 256 bytes
            is_outgoing (``bool``): Is call outgoing

        Raises:
            :class:`ValueError` if provided auth key has wrong length
        """
        if len(key) != 256:
            raise ValueError('key length must be exactly 256 bytes but is {}'.format(len(key)))
        super().set_encryption_key(key, is_outgoing)

    def set_remote_endpoints(self, endpoints: List[Endpoint], allow_p2p: bool, tcp: bool, connection_max_layer: int):
        """
        Set remote endpoints received in call object from Telegram.

        Usually it's ``[call.connection] + call.alternative_connections``.

        You must build :class:`Endpoint` objects from MTProto :class:`phoneConnection` objects and pass them in list.

        Args:
            endpoints (``list`` of :class:`Endpoint`): List of endpoints
            allow_p2p (``bool``): Is p2p connection allowed, usually `call.p2p_allowed` value is used
            tcp (``bool``): Connect via TCP, not recommended
            connection_max_layer (``int``): Use a value provided by :attr:`VoIPController.CONNECTION_MAX_LAYER`

        Raises:
            :class:`ValueError` if either no endpoints are provided or endpoints without IPv4 or with wrong \
            ``peer_tag`` (must be either ``None`` or have length of 16 bytes) are detected
        """
        if not endpoints:
            raise ValueError('endpoints len is 0')
        for ep in endpoints:
            if ep.ip is None or not len(ep.ip):
                raise ValueError('endpoint {} has empty/null ipv4'.format(ep))
            if ep.peer_tag is not None and len(ep.peer_tag) != 16:
                raise ValueError('endpoint {} has peer_tag of wrong length'.format(ep))
        super().set_remote_endpoints(endpoints, allow_p2p, tcp, connection_max_layer)

    def get_debug_string(self) -> str:
        """
        Get debug string

            Returns:
                ``str`` containing debug info
        """
        return super().get_debug_string()

    def set_network_type(self, _type: NetType):
        """
        Set network type

        Args:
            _type (:class:`NetType`): Network type to set
        """
        super().set_network_type(_NetType(_type.value))

    def set_mic_mute(self, mute: bool):
        """
        Set "microphone" state. If muted, audio is not being sent

        Args:
            mute (``bool``): Whether to mute "microphone"
        """
        super().set_mic_mute(mute)

    def set_config(self,
                   recv_timeout: float,
                   init_timeout: float,
                   data_saving_mode: DataSaving,
                   call_id: int,
                   enable_aec: bool = True,
                   enable_ns: bool = True,
                   enable_agc: bool = True,
                   log_file_path: str = None,
                   status_dump_path: str = None,
                   log_packet_stats: bool = None):
        """
        Set call config

        Args:
            recv_timeout (``float``):
                Packet receive timeout, usually value received from ``help.getConfig()`` is used

            init_timeout (``float``):
                Packet init timeout, usually value received from ``help.getConfig()`` is used

            data_saving_mode (:class:`DataSaving`): Data saving mode

            call_id (``int``): Call ID

            enable_aec (``bool``, *optional*):
                Whether to enable automatic echo cancellation, defaults to ``True``

            enable_ns (``bool``, *optional*):
                Whether to enable noise suppression, defaults to ``True``

            enable_agc (``bool``, *optional*):
                Whether to enable automatic gain control, defaults to ``True``

            log_file_path (``str``, *optional*):
                Call log file path, calculated automatically if not provided

            status_dump_path (``str``, *optional*):
                Status dump path, calculated automatically if not provided and ``debug`` is enabled

            log_packet_stats (``bool``, *optional*):
                Whether to log packet stats, defaults to ``debug`` value
        """
        if log_file_path is None:
            if self.debug:
                log_file_path = self._get_log_file_path('voip{}'.format(call_id))
            else:
                log_file_path = self._get_log_file_path_for_call_id(call_id)  # wtf?
        if status_dump_path is None:
            status_dump_path = self._get_log_file_path('voip_stats') if self.debug else ''
        if log_packet_stats is None:
            log_packet_stats = self.debug
        super().set_config(recv_timeout, init_timeout, _DataSaving(data_saving_mode.value), enable_aec, enable_ns, enable_agc,
                           log_file_path, status_dump_path, log_packet_stats)

    def debug_ctl(self, request: int, param: int):
        """
        Debugging options

        Args:
            request (``int``):
                Option (``1`` for max bitrate, ``2`` for packet loss (in percents), ``3`` for toggling p2p, \
                ``4`` for toggling echo cancelling)

            param (``int``):
                Numeric value for options 1 and 2, ``0`` or ``1`` for options 3 and 4
        """
        super().debug_ctl(request, param)

    def get_preferred_relay_id(self) -> int:
        """
        Get preferred relay ID (used in ``discardCall`` MTProto request)

        Returns:
            ``int`` ID
        """
        return super().get_preferred_relay_id()

    def get_last_error(self) -> CallError:
        """
        Get last error type

        Returns:
            :class:`CallError` matching last occurred error type
        """
        return CallError(super().get_last_error())

    def get_stats(self) -> Stats:
        """
        Get call stats

        Returns:
            :class:`Stats` object
        """
        return super().get_stats()

    def get_debug_log(self) -> str:
        """
        Get debug log

        Returns:
            JSON ``str`` containing debug log
        """
        return super().get_debug_log()

    def set_audio_output_gain_control_enabled(self, enabled: bool):
        """
        Toggle output gain control

        Args:
            enabled (``bool``): Whether to enable output gain control
        """
        super().set_audio_output_gain_control_enabled(enabled)

    def set_echo_cancellation_strength(self, strength: int):
        """
        Set echo cancellation strength, does nothing currently but was in Java bindings (?)

        Args:
            strength (``int``): Strength value
        """
        super().set_echo_cancellation_strength(strength)

    def get_peer_capabilities(self) -> int:
        """
        Get peer capabilities

        Returns:
            ``int`` with bit mask, looks like it is used only for experimental features (group, video calls)
        """
        return super().get_peer_capabilities()

    def need_rate(self) -> bool:
        """
        Get whether the call needs rating

        Returns:
            ``bool`` value
        """
        return super().need_rate()

    @property
    def native_io(self) -> bool:
        """
        Get native I/O status (file I/O implemented in C++)

        Returns:
            ``bool`` status (enabled or not)
        """
        return self._native_io_get()

    @native_io.setter
    def native_io(self, val: bool) -> None:
        """
        Set native I/O status (file I/O implemented in C++)

        Args:
            val (``bool``): Status value
        """
        self._native_io_set(val)

    def play(self, path: str) -> bool:
        """
        Add a file to play queue for native I/O

        Args:
            path (``str``): File path

        Returns:
            ``bool`` whether opening the file was successful. File is not added to queue on failure.
        """
        return super().play(path)

    def play_on_hold(self, paths: List[str]) -> None:
        """
        Replace the hold queue for native I/O

        Args:
            paths (``list`` of ``str``): List of file paths
        """
        super().play_on_hold(paths)

    def set_output_file(self, path: str) -> bool:
        """
        Set output file for native I/O

        Args:
            path (``str``): File path

        Returns:
            ``bool`` whether opening the file was successful. Output file is not replaced on failure.
        """
        return super().set_output_file(path)

    def clear_play_queue(self) -> None:
        """
        Clear the play queue for native I/O
        """
        super().clear_play_queue()

    def clear_hold_queue(self) -> None:
        """
        Clear the hold queue for native I/O
        """
        super().clear_hold_queue()

    def unset_output_file(self) -> None:
        """
        Unset the output file for native I/O
        """
        super().unset_output_file()

    # native code callback
    def _handle_state_change(self, state: _CallState):
        state = CallState(state)

        if state == CallState.ESTABLISHED and not self.start_time:
            self.start_time = get_real_elapsed_time()

        for handler in self.call_state_changed_handlers:
            callable(handler) and handler(state)

    # native code callback
    def _handle_signal_bars_change(self, count: int):
        for handler in self.signal_bars_changed_handlers:
            callable(handler) and handler(count)

    def update_state(self, state: CallState):
        """
        Manually update state (only triggers handlers)

        Args:
            state (:class:`CallState`): State to set
        """
        self._handle_state_change(state)

    def set_send_audio_frame_callback(self, func: callable):
        """
        Set callback providing audio data to send

        Should accept one argument (``int`` length of requested audio frame) and return ``bytes`` object with audio \
        data encoded in 16-bit signed PCM

        If returned object has insufficient length, it will be automatically padded with zero bytes

        Args:
            func (``callable``): Callback function
        """
        self.send_audio_frame_callback = func

    def _send_audio_frame_impl(self, length: int):
        frame = b''
        if callable(self.send_audio_frame_callback):
            frame = self.send_audio_frame_callback(length)
        return frame.ljust(length, b'\0')

    def set_recv_audio_frame_callback(self, func: callable):
        """
        Set callback receiving incoming audio data

        Should accept one argument (``bytes``) with audio data encoded in 16-bit signed PCM

        Args:
            func (``callable``): Callback function
        """
        self.recv_audio_frame_callback = func

    def _recv_audio_frame_impl(self, frame: bytes):
        if callable(self.recv_audio_frame_callback):
            self.recv_audio_frame_callback(frame)

    def _get_log_file_path(self, name: str) -> str:
        os.makedirs(self.logs_dir, exist_ok=True)
        now = datetime.now()
        fname = '{}_{}_{}_{}_{}_{}_{}.txt'.format(now.year, now.month, now.day, now.hour, now.minute, now.second, name)
        return os.path.abspath(os.path.join(self.logs_dir, fname))

    def _get_log_file_path_for_call_id(self, call_id: int) -> str:
        os.makedirs(self.logs_dir, exist_ok=True)
        # Java version cleans up old logs (*.log) for non-debug version here (leaves 20 latest)
        return os.path.abspath(os.path.join(self.logs_dir, '{}.log'.format(call_id)))


class VoIPServerConfig(_VoIPServerConfig):
    """
    Global server config class. This class contains default config in its source
    """

    # default config
    config = {
        'audio_max_bitrate': 20000,
        'audio_max_bitrate_gprs': 8000,
        'audio_max_bitrate_edge': 16000,
        'audio_max_bitrate_saving': 8000,
        'audio_init_bitrate': 16000,
        'audio_init_bitrate_gprs': 8000,
        'audio_init_bitrate_edge': 8000,
        'audio_init_bitrate_saving': 8000,
        'audio_bitrate_step_incr': 1000,
        'audio_bitrate_step_decr': 1000,
        'audio_min_bitrate': 8000,
        'relay_switch_threshold': 0.8,
        'p2p_to_relay_switch_threshold': 0.6,
        'relay_to_p2p_switch_threshold': 0.8,
        'reconnecting_state_timeout': 2.0,
        'rate_flags': 0xFFFFFFFF,
        'rate_min_rtt': 0.6,
        'rate_min_send_loss': 0.2,
        'packet_loss_for_extra_ec': 0.02,
        'max_unsent_stream_packets': 2,
    }

    @classmethod
    def set_config(cls, _json: Union[str, dict]):
        """
        Set global server config

        Args:
            _json (``str`` | ``dict``): either JSON-encoded object or ``dict`` containing config values. \
            Might be received from MTProto ``phone.getCallConfig()`` call, if not set default values are used

        Raises:
            Prints an error to ``stderr`` if JSON parsing (for ``str`` argument) or encoding (for ``dict`` argument) \
            has occurred
        """
        try:
            if isinstance(_json, dict):
                _json = json.dumps(_json)
            cls.config.update(json.loads(_json))
            _VoIPServerConfig.set_config(_json)
        except json.JSONDecodeError as e:
            print('Error parsing VoIP config', e, file=sys.stderr)
        except TypeError as e:
            print('Error building JSON', e, file=sys.stderr)

    @classmethod
    def set_bitrate_config(cls, init_bitrate: int = 16000, max_bitrate: int = 20000, min_bitrate: int = 8000,
                           decrease_step: int = 1000, increase_step: int = 1000):
        """
        Helper method for setting bitrate options

        Args:
            init_bitrate (``int``): Initial bitrate value
            max_bitrate (``int``): Maximum bitrate value
            min_bitrate (``int``):  Minimum bitrate value
            decrease_step (``int``): Bitrate decrease step
            increase_step (``int``): Bitrate increase step

        Raises:
            Same as :meth:`set_config`
        """
        cls.set_config({
            'audio_init_bitrate': init_bitrate,
            'audio_max_bitrate': max_bitrate,
            'audio_min_bitrate': min_bitrate,
            'audio_bitrate_step_decr': decrease_step,
            'audio_bitrate_step_incr': increase_step,
        })


__all__ = ['NetType', 'DataSaving', 'CallState', 'CallError', 'Stats', 'Endpoint', 'VoIPController',
           'VoIPServerConfig']
