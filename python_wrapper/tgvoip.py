import json
import os
import sys
from datetime import datetime

from _tgvoip import (
    NetType,
    DataSaving,
    CallState,
    Stats,
    Endpoint,
    VoIPController as _VoIPController,
    VoIPServerConfig as _VoIPServerConfig
)

from _utils import get_real_elapsed_time


class VoIPController(_VoIPController):
    def __init__(self, persistent_state_file: str = '', debug=False, logs_dir='logs'):
        self.debug = debug
        self.logs_dir = logs_dir
        self.start_time = 0
        super(VoIPController, self).__init__(persistent_state_file)

    def _parse_endpoint(self, obj) -> Endpoint:
        raise NotImplementedError()

    def set_remote_endpoints(self, endpoints: list, allow_p2p: bool, tcp: bool, connection_max_layer: int):
        if not endpoints:
            raise ValueError('endpoints len is 0')
        parsed_endpoints = [self._parse_endpoint(obj) for obj in endpoints]
        for ep in parsed_endpoints:
            if ep.ip is None or not len(ep.ip):
                raise ValueError('endpoint {} has empty/null ipv4'.format(ep))
            if ep.peer_tag is not None and len(ep.peer_tag) != 16:
                raise ValueError('endpoint {} has peer_tag of wrong length'.format(ep))
        super(VoIPController, self).set_remote_endpoints(parsed_endpoints, allow_p2p, tcp, connection_max_layer)

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
        # Java version cleans up old logs (*.log) for non-debug version here (leaves 20 latest)
        return os.path.abspath(os.path.join(self.logs_dir, '{}.log'.format(call_id)))

    def set_proxy(self, address: str, port: int = 1080, username: str = '', password: str = ''):
        if not address:
            raise ValueError('address can\'t be empty')
        super(VoIPController, self).set_proxy(address, port, username, password)


class VoIPServerConfig(_VoIPServerConfig):
    config = {}

    @staticmethod
    def set_config(json_string: str):
        try:
            VoIPServerConfig.config = json.loads(json_string)
            _VoIPServerConfig.set_config(json_string)
        except json.JSONDecodeError as e:
            print('Error parsing VoIP config', e, file=sys.stderr)


__all__ = ['NetType', 'DataSaving', 'CallState', 'Stats', 'Endpoint', 'VoIPController', 'VoIPServerConfig']
