/*
 * PytgVoIP - Telegram VoIP Library for Python
 * Copyright (C) 2019 bakatrouble <https://github.com/bakatrouble>
 *
 * This file is part of PytgVoIP.
 *
 * PytgVoIP is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * PytgVoIP is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with PytgVoIP.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "_tgvoip.h"
#include <iostream>
#include <utility>
// #include <chrono>

Endpoint::Endpoint(int64_t id, std::string ip, std::string ipv6, uint16_t port, const std::string &peer_tag)
    : id(id), ip(std::move(ip)), ipv6(std::move(ipv6)), port(port), peer_tag(peer_tag) {}

VoIPController::VoIPController() {
    ctrl = nullptr;
    output_file = nullptr;
    native_io = false;
}

VoIPController::VoIPController(const std::string &_persistent_state_file) : VoIPController() {
    if (!_persistent_state_file.empty())
        persistent_state_file = _persistent_state_file;
}

void VoIPController::init() {
    ctrl = new tgvoip::VoIPController();
    ctrl->implData = (void *)this;
    tgvoip::VoIPController::Callbacks callbacks {};
    callbacks.connectionStateChanged = [](tgvoip::VoIPController *ctrl, int state) {
        ((VoIPController *)ctrl->implData)->_handle_state_change(CallState(state));
    };
    callbacks.signalBarCountChanged = [](tgvoip::VoIPController *ctrl, int count) {
        ((VoIPController *)ctrl->implData)->_handle_signal_bars_change(count);
    };
    callbacks.groupCallKeyReceived = nullptr;
    callbacks.groupCallKeySent = nullptr;
    callbacks.upgradeToGroupCallRequested = nullptr;
    ctrl->SetCallbacks(callbacks);
    ctrl->SetAudioDataCallbacks(
            [this](int16_t *buf, size_t size) {
                this->send_audio_frame(buf, size);
            },
            [this](int16_t *buf, size_t size) {
                this->recv_audio_frame(buf, size);
            },
            [](int16_t *buf, size_t size) {}
    );

    if (!persistent_state_file.empty()) {
        FILE *f = fopen(persistent_state_file.c_str(), "r");
        if (f) {
            fseek(f, 0, SEEK_END);
            auto len = static_cast<size_t>(ftell(f));
            fseek(f, 0, SEEK_SET);
            if(len<1024*512 && len>0){
                auto fbuf = static_cast<char *>(malloc(len));
                fread(fbuf, 1, len, f);
                std::vector<uint8_t> state(fbuf, fbuf+len);
                free(fbuf);
                ctrl->SetPersistentState(state);
            }
            fclose(f);
        }
    }
}

VoIPController::~VoIPController() {
    ctrl->Stop();
    std::vector<uint8_t> state = ctrl->GetPersistentState();
    delete ctrl;
    clear_play_queue();
    clear_hold_queue();
    unset_output_file();
    if (!persistent_state_file.empty()) {
        FILE *f = fopen(persistent_state_file.c_str(), "w");
        if (f) {
            fwrite(state.data(), 1, state.size(), f);
            fclose(f);
        }
    }
}

void VoIPController::start() {
    ctrl->Start();
}

void VoIPController::connect() {
    ctrl->Connect();
}

void VoIPController::set_proxy(const std::string &address, uint16_t port, const std::string &username, const std::string &password) {
    ctrl->SetProxy(tgvoip::PROXY_SOCKS5, address, port, username, password);
}

void VoIPController::set_encryption_key(char *key, bool is_outgoing) {
    ctrl->SetEncryptionKey(key, is_outgoing);
}

void VoIPController::set_remote_endpoints(std::list<Endpoint> endpoints, bool allow_p2p, bool tcp, int connection_max_layer) {
    std::vector<tgvoip::Endpoint> eps;
    for (auto const &ep : endpoints) {
        tgvoip::IPv4Address v4addr(ep.ip);
        tgvoip::IPv6Address v6addr("::0");
        if (!ep.ipv6.empty())
            v6addr = tgvoip::IPv6Address(ep.ipv6);
        std::string peer_tag = ep.peer_tag;
        unsigned char p_tag[16];
        if (!peer_tag.empty())
            memcpy(p_tag, peer_tag.c_str(), 16);
        eps.emplace_back(tgvoip::Endpoint(ep.id, ep.port, v4addr, v6addr,
                tcp ? tgvoip::Endpoint::Type::TCP_RELAY : tgvoip::Endpoint::Type::UDP_RELAY, p_tag));
    }
    ctrl->SetRemoteEndpoints(eps, allow_p2p, connection_max_layer);
}

std::string VoIPController::get_debug_string() {
    return ctrl->GetDebugString();
}

void VoIPController::set_network_type(NetType type) {
    ctrl->SetNetworkType(type);
}

void VoIPController::set_mic_mute(bool mute) {
    ctrl->SetMicMute(mute);
}

void VoIPController::set_config(double init_timeout, double recv_timeout, DataSaving data_saving_mode, bool enable_aec,
                                bool enable_ns, bool enable_agc,
#ifndef _WIN32
                                const std::string &log_file_path, const std::string &status_dump_path,
#else
                                const std::wstring &log_file_path, const std::wstring &status_dump_path,
#endif
                                bool log_packet_stats) {
    tgvoip::VoIPController::Config cfg;
    cfg.initTimeout = init_timeout;
    cfg.recvTimeout = recv_timeout;
    cfg.dataSaving = data_saving_mode;
    cfg.enableAEC = enable_aec;
    cfg.enableNS = enable_ns;
    cfg.enableAGC = enable_agc;
    cfg.enableCallUpgrade = false;
    if (!log_file_path.empty())
        cfg.logFilePath = log_file_path;
    if (!status_dump_path.empty())
        cfg.statsDumpFilePath = status_dump_path;
    cfg.logPacketStats = log_packet_stats;
    ctrl->SetConfig(cfg);
}

void VoIPController::debug_ctl(int request, int param) {
    ctrl->DebugCtl(request, param);
}

long VoIPController::get_preferred_relay_id() {
    return ctrl->GetPreferredRelayID();
}

CallError VoIPController::get_last_error() {
    return CallError(ctrl->GetLastError());
}

Stats VoIPController::get_stats() {
    tgvoip::VoIPController::TrafficStats _stats {};
    ctrl->GetStats(&_stats);
    return Stats {
        _stats.bytesSentWifi,
        _stats.bytesSentMobile,
        _stats.bytesRecvdWifi,
        _stats.bytesRecvdMobile,
    };
}

std::string VoIPController::get_debug_log() {
    return ctrl->GetDebugLog();
}

void VoIPController::set_audio_output_gain_control_enabled(bool enabled) {
    ctrl->SetAudioOutputGainControlEnabled(enabled);
}

void VoIPController::set_echo_cancellation_strength(int strength) {
    ctrl->SetEchoCancellationStrength(strength);
}

int VoIPController::get_peer_capabilities() {
    return ctrl->GetPeerCapabilities();
}

bool VoIPController::need_rate() {
    return ctrl->NeedRate();
}

/* std::vector<tgvoip::AudioInputDevice> VoIPController::enumerate_audio_inputs() {
    return tgvoip::VoIPController::EnumerateAudioInputs();
}

std::vector<tgvoip::AudioOutputDevice> VoIPController::enumerate_audio_outputs() {
    return tgvoip::VoIPController::EnumerateAudioOutputs();
}

void VoIPController::set_current_audio_input(std::string &id) {
    ctrl->SetCurrentAudioInput(id);
}

void VoIPController::set_current_audio_output(std::string &id) {
    ctrl->SetCurrentAudioOutput(id);
}

std::string VoIPController::get_current_audio_input_id() {
    return ctrl->GetCurrentAudioInputID();
}

std::string VoIPController::get_current_audio_output_id() {
    return ctrl->GetCurrentAudioOutputID();
} */

void VoIPController::_handle_state_change(CallState state) {
    throw py::not_implemented_error();
}

void VoIPController::_handle_signal_bars_change(int count) {
    throw py::not_implemented_error();
}

void VoIPController::send_audio_frame(int16_t *buf, size_t size) {
    tgvoip::MutexGuard m(input_mutex);
    // auto start = std::chrono::high_resolution_clock::now();
    if (native_io) {
        this->_send_audio_frame_native_impl(buf, size);
    } else {
        char *frame = this->_send_audio_frame_impl(sizeof(int16_t) * size);
        if (frame != nullptr) {
            memcpy(buf, frame, sizeof(int16_t) * size);
        }
    }
    // auto finish = std::chrono::high_resolution_clock::now();
    // std::cout << "send: " << std::chrono::duration_cast<std::chrono::nanoseconds>(finish - start).count() << std::endl;
}

char *VoIPController::_send_audio_frame_impl(ulong len) { return (char *)""; }

void VoIPController::_send_audio_frame_native_impl(int16_t *buf, size_t size) {
    if (!input_files.empty()) {
        size_t read_size = fread(buf, sizeof(int16_t), size, input_files.front());
        if (read_size != size) {
            fclose(input_files.front());
            input_files.pop();
            size_t read_offset = read_size % size;
            memset(buf + read_offset, 0, size - read_offset);
        }
    } else if (!hold_files.empty()) {
        size_t read_size = fread(buf, sizeof(int16_t), size, hold_files.front());
        if (read_size != size) {
            fseek(hold_files.front(), 0, SEEK_SET);
            hold_files.push(hold_files.front());
            hold_files.pop();
            size_t read_offset = read_size % size;
            memset(buf + read_offset, 0, size - read_offset);
        }
    }
}

void VoIPController::recv_audio_frame(int16_t *buf, size_t size) {
    tgvoip::MutexGuard m(output_mutex);
    // auto start = std::chrono::high_resolution_clock::now();
    if (buf != nullptr) {
        if (native_io) {
            this->_recv_audio_frame_native_impl(buf, size);
        } else {
            std::string frame((const char *) buf, sizeof(int16_t) * size);
            this->_recv_audio_frame_impl(frame);
        }
    }
    // auto finish = std::chrono::high_resolution_clock::now();
    // std::cout << "recv: " << std::chrono::duration_cast<std::chrono::nanoseconds>(finish - start).count() << std::endl;
}

void VoIPController::_recv_audio_frame_impl(const py::bytes &frame) {}

void VoIPController::_recv_audio_frame_native_impl(int16_t *buf, size_t size) {
    if (output_file != nullptr) {
        size_t written_size = fwrite(buf, sizeof(int16_t), size, output_file);
        if (written_size != size) {
            std::cerr << "Written size (" << written_size << ") does not match expected (" << size << ")" << std::endl;
        }
    }
}

std::string VoIPController::get_version(const py::object& /* cls */) {
    return tgvoip::VoIPController::GetVersion();
}

int VoIPController::connection_max_layer(const py::object& /* cls */) {
    return tgvoip::VoIPController::GetConnectionMaxLayer();
}

bool VoIPController::_native_io_get() {
    return native_io;
}

void VoIPController::_native_io_set(bool status) {
    native_io = status;
}

bool VoIPController::play(std::string &path) {
    FILE *tmp = fopen(path.c_str(), "rb");
    if (tmp == nullptr) {
        std::cerr << "Unable to open file " << path << " for reading" << std::endl;
        return false;
    }
    tgvoip::MutexGuard m(input_mutex);
    input_files.push(tmp);
    return true;
}

void VoIPController::play_on_hold(std::vector<std::string> &paths) {
    clear_hold_queue();
    tgvoip::MutexGuard m(input_mutex);
    for (auto &path : paths) {
        FILE *tmp = fopen(path.c_str(), "rb");
        if (tmp == nullptr) {
            std::cerr << "Unable to open file " << path << " for reading" << std::endl;
        } else {
            hold_files.push(tmp);
        }
    }
}

bool VoIPController::set_output_file(std::string &path) {
    FILE *tmp = fopen(path.c_str(), "wb");
    if (tmp == nullptr) {
        std::cerr << "Unable to open file " << path << " for writing" << std::endl;
        return false;
    }
    unset_output_file();
    tgvoip::MutexGuard m(output_mutex);
    output_file = tmp;
    return true;
}

void VoIPController::clear_play_queue() {
    tgvoip::MutexGuard m(input_mutex);
    while (!input_files.empty()) {
        fclose(input_files.front());
        input_files.pop();
    }
}

void VoIPController::clear_hold_queue() {
    tgvoip::MutexGuard m(input_mutex);
    while (!hold_files.empty()) {
        fclose(hold_files.front());
        hold_files.pop();
    }
}

void VoIPController::unset_output_file() {
    if (output_file != nullptr) {
        tgvoip::MutexGuard m(output_mutex);
        fclose(output_file);
        output_file = nullptr;
    }
}

void VoIPServerConfig::set_config(std::string &json_str) {
    tgvoip::ServerConfig::GetSharedInstance()->Update(json_str);
}
