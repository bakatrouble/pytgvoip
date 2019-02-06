import json
import os
import sys
from datetime import datetime
from typing import Union, List

from _tgvoip import (
    NetType,
    DataSaving,
    CallState as _CallState,
    CallError,
    Stats,
    Endpoint,
    VoIPController as _VoIPController,
    VoIPServerConfig as _VoIPServerConfig,
    __version__
)

from tgvoip._utils import get_real_elapsed_time


class CallState(_CallState):
    HANGING_UP = 10
    ENDED = 11
    EXCHANGING_KEYS = 12
    WAITING = 13
    REQUESTING = 14
    WAITING_INCOMING = 15
    RINGING = 16
    BUSY = 17


class VoIPController(_VoIPController):
    def __init__(self, persistent_state_file: str = '', debug=False, logs_dir='logs'):
        _VoIPController.__init__(self, persistent_state_file)
        self.debug = debug
        self.logs_dir = logs_dir
        self.start_time = 0
        self.send_audio_frame_callback = None
        self.recv_audio_frame_callback = None
        self.init()

    def _parse_endpoint(self, obj) -> Endpoint:
        raise NotImplementedError()

    def set_remote_endpoints(self, endpoints: List[Endpoint], allow_p2p: bool, tcp: bool, connection_max_layer: int):
        if not endpoints:
            raise ValueError('endpoints len is 0')
        for ep in endpoints:
            if ep.ip is None or not len(ep.ip):
                raise ValueError('endpoint {} has empty/null ipv4'.format(ep))
            if ep.peer_tag is not None and len(ep.peer_tag) != 16:
                raise ValueError('endpoint {} has peer_tag of wrong length'.format(ep))
        super(VoIPController, self).set_remote_endpoints(endpoints, allow_p2p, tcp, connection_max_layer)

    def set_encryption_key(self, key: bytes, is_outgoing: bool):
        if len(key) != 256:
            raise ValueError('key length must be exactly 256 bytes but is {}'.format(len(key)))
        super(VoIPController, self).set_encryption_key(key, is_outgoing)

    # native code callback
    def handle_state_change(self, state: CallState):
        if state == CallState.ESTABLISHED and self.start_time:
            self.start_time = get_real_elapsed_time()
        # TODO: listeners

    # native code callback
    def handle_signal_bars_change(self, count: int):
        pass
        # TODO: listeners

    @property
    def call_duration(self) -> float:
        return get_real_elapsed_time() - self.start_time

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
        if log_file_path is None:
            if self.debug:
                log_file_path = self.get_log_file_path('voip{}'.format(call_id))
            else:
                log_file_path = self.get_log_file_path_for_call_id(call_id)  # wtf?
        if status_dump_path is None:
            status_dump_path = self.get_log_file_path('voip_stats') if self.debug else ''
        if log_packet_stats is None:
            log_packet_stats = self.debug
        super(VoIPController, self).set_config(recv_timeout, init_timeout, data_saving_mode, enable_aec,
                                               enable_ns, enable_agc, log_file_path, status_dump_path, log_packet_stats)

    def get_log_file_path(self, name: str) -> str:
        os.makedirs(self.logs_dir, exist_ok=True)
        now = datetime.now()
        fname = '{}_{}_{}_{}_{}_{}_{}.txt'.format(now.year, now.month, now.day, now.hour, now.minute, now.second, name)
        return os.path.abspath(os.path.join(self.logs_dir, fname))

    def get_log_file_path_for_call_id(self, call_id: int) -> str:
        os.makedirs(self.logs_dir, exist_ok=True)
        # Java version cleans up old logs (*.log) for non-debug version here (leaves 20 latest)
        return os.path.abspath(os.path.join(self.logs_dir, '{}.log'.format(call_id)))

    def set_proxy(self, address: str, port: int = 1080, username: str = '', password: str = ''):
        if not address:
            raise ValueError('address can\'t be empty')
        super(VoIPController, self).set_proxy(address, port, username, password)

    def set_send_audio_frame_callback(self, func):
        self.send_audio_frame_callback = func

    def send_audio_frame_impl(self, length: int):
        if callable(self.send_audio_frame_callback):
            return self.send_audio_frame_callback(length)
        return b''

    def set_recv_audio_frame_callback(self, func):
        self.recv_audio_frame_callback = func

    def recv_audio_frame_impl(self, frame: bytes):
        if callable(self.recv_audio_frame_callback):
            self.recv_audio_frame_callback(frame)


class VoIPServerConfig(_VoIPServerConfig):
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

    @staticmethod
    def set_config(_json: Union[str, dict]):
        try:
            if isinstance(_json, dict):
                _json = json.dumps(_json)
            VoIPServerConfig.config.update(json.loads(_json))
            _VoIPServerConfig.set_config(_json)
        except json.JSONDecodeError as e:
            print('Error parsing VoIP config', e, file=sys.stderr)
        except TypeError as e:
            print('Error building JSON', e, file=sys.stderr)

    @staticmethod
    def set_bitrate_config(init_bitrate: int = 16000, max_bitrate: int = 20000, min_bitrate: int = 8000,
                           decrease_step: int = 1000, increase_step: int = 1000):
        VoIPServerConfig.set_config({
            'audio_init_bitrate': init_bitrate,
            'audio_max_bitrate': max_bitrate,
            'audio_min_bitrate': min_bitrate,
            'audio_bitrate_step_decr': decrease_step,
            'audio_bitrate_step_incr': increase_step,
        })


__all__ = ['NetType', 'DataSaving', 'CallState', 'CallError', 'Stats', 'Endpoint', 'VoIPController',
           'VoIPServerConfig', '__version__']
