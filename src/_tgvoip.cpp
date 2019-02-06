#include "_tgvoip.h"
#include <iostream>

Endpoint::Endpoint(int64_t id, const std::string &ip, const std::string &ipv6, uint16_t port, const std::string &peer_tag)
    : id(id), ip(ip), ipv6(ipv6), port(port), peer_tag(peer_tag) {}

VoIPController::VoIPController() {
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
        ((VoIPController *)ctrl->implData)->handle_state_change(CallState(state));
    };
    callbacks.signalBarCountChanged = [](tgvoip::VoIPController *ctrl, int count) {
        ((VoIPController *)ctrl->implData)->handle_signal_bars_change(count);
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
            }
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
                                bool enable_ns, bool enable_agc, const std::string &log_file_path,
                                const std::string &status_dump_path, bool log_packet_stats) {
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

std::string VoIPController::get_version(py::object /* cls */) {
    return tgvoip::VoIPController::GetVersion();
}

int VoIPController::connection_max_layer(py::object /* cls */) {
    return tgvoip::VoIPController::GetConnectionMaxLayer();
}

void VoIPController::handle_state_change(CallState state) {
    throw py::not_implemented_error();
}

void VoIPController::handle_signal_bars_change(int count) {
    throw py::not_implemented_error();
}

void VoIPController::send_audio_frame(int16_t *buf, size_t size) {
    tgvoip::MutexGuard m(input_mutex);
    char *frame = this->send_audio_frame_impl(sizeof(int16_t) * size);
    if (frame != nullptr)
        memcpy(buf, frame, sizeof(int16_t) * size);
}

char *VoIPController::send_audio_frame_impl(long len) { return (char *)""; }

void VoIPController::recv_audio_frame(int16_t *buf, size_t size) {
    tgvoip::MutexGuard m(output_mutex);
    if (buf != nullptr) {
        std::string frame((const char *) buf, sizeof(int16_t) * size);
        this->recv_audio_frame_impl(frame);
    }
}

void VoIPController::recv_audio_frame_impl(py::bytes frame) {}


void VoIPServerConfig::set_config(std::string &json_str) {
    tgvoip::ServerConfig::GetSharedInstance()->Update(json_str);
}
