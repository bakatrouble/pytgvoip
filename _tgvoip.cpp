#include "_tgvoip.h"
#include <boost/python.hpp>
#include <wchar.h>
#include <iostream>
#include <string.h>
#include <string>
#include <map>

#include "libtgvoip/VoIPServerConfig.h"
#include "libtgvoip/logging.h"

using namespace boost::python;
using namespace tgvoip;
using namespace tgvoip::audio;
using namespace std;

VoIP::VoIP() {
    configuration = dict();
    configuration["endpoints"] = boost::python::list();
    configuration["shared_config"] = dict();
    storage = dict();
    _internal_storage = dict();
    _internal_storage["creator"] = false;
    _internal_storage["call_id"] = NULL;
    _internal_storage["protocol"] = NULL;

    init_voip_controller();
}

VoIP::VoIP(bool creator, int _other_id, object call_id, object _handler, int _call_state, object protocol) : VoIP() {
    other_id = _other_id;
    call_state = _call_state;
    _internal_storage["creator"] = creator;
    _internal_storage["call_id"] = call_id;
    _internal_storage["protocol"] = protocol;
    handler = _handler;
}

void VoIP::init_voip_controller() {
    inst = new VoIPController();
    output_file = NULL;
    inst->implData = (void *)this;
    VoIPController::Callbacks callbacks;
    callbacks.connectionStateChanged = [](VoIPController *ctrl, int state) {
        ((VoIP *)ctrl->implData)->state = state;
        if (state == STATE_FAILED) {
            ((VoIP *)ctrl->implData)->deinit_voip_controller();
        }
    };
    callbacks.signalBarCountChanged = NULL;
    callbacks.groupCallKeySent = NULL;
    callbacks.groupCallKeyReceived = NULL;
    callbacks.upgradeToGroupCallRequested = NULL;
    inst->SetCallbacks(callbacks);
    inst->SetAudioDataCallbacks(
            [this](int16_t *buffer, size_t size) {
                this->send_audio_frame(buffer, size);
            },
            [this](int16_t *buffer, size_t size) {
                this->recv_audio_frame(buffer, size);
            }
    );
}

bool VoIP::discard(object reason, object rating, bool debug) {
    if (call_state == CALL_STATE_ENDED)
         return false;

    object call_id = _internal_storage.get("call_id");
    handler.attr("discard_call")(call_id, reason, rating, debug);
    deinit_voip_controller();
    return true;
}

bool VoIP::accept() {
    if (call_state != CALL_STATE_INCOMING)
        return false;

    call_state = CALL_STATE_ACCEPTED;

    object call_id = _internal_storage.get("call_id");
    if (extract<bool>(handler.attr("accept_call")(call_id)) == false) {
        bool debug = false;
        handler.attr("discard_call")(call_id, NULL, NULL, debug);
        deinit_voip_controller();
        return false;
    }

    return true;
}

void VoIP::deinit_voip_controller() {
    if (call_state != CALL_STATE_ENDED) {
        call_state = CALL_STATE_ENDED;
        if (inst) {
            inst->Stop();
            delete inst;
            inst = NULL;
        }

        while (hold_files.size()) {
            fclose(hold_files.front());
            hold_files.pop();
        }
        while (input_files.size()) {
            fclose(input_files.front());
            input_files.pop();
        }
        unset_output_file();
    }
}

bool VoIP::start_the_magic() {
    if (state == STATE_WAIT_INIT_ACK) {
        object call_id = _internal_storage.get("call_id");
        bool debug = false;
        handler.attr("discard_call")(call_id, NULL, NULL, debug);
        deinit_voip_controller();
        return false;
    }

    inst->Start();
    inst->Connect();
    _internal_storage["created"] = (int64_t)time(NULL);
    call_state = CALL_STATE_READY;
    return true;
}

void VoIP::recv_audio_frame(int16_t* data, size_t size) {
    MutexGuard m(output_mutex);
    if (this->output_file != NULL) {
        if (fwrite(data, sizeof(int16_t), size, this->output_file) != size) {
            throw "COULD NOT WRITE DATA TO FILE";
        }
    }
}

void VoIP::send_audio_frame(int16_t *data, size_t size) {
    MutexGuard m(input_mutex);

    if (!this->input_files.empty())
    {
        if ((read_input = fread(data, sizeof(int16_t), size, this->input_files.front())) != size)
        {
            fclose(this->input_files.front());
            this->input_files.pop();
            memset(data + (read_input % size), 0, size - (read_input % size));
        }
        this->playing = true;
    }
    else
    {
        this->playing = false;
        if (!this->hold_files.empty())
        {
            if ((read_input = fread(data, sizeof(int16_t), size, this->hold_files.front())) != size)
            {
                fseek(this->hold_files.front(), 0, SEEK_SET);
                this->hold_files.push(this->hold_files.front());
                this->hold_files.pop();
                memset(data + (read_input % size), 0, size - (read_input % size));
            }
        }
    }
}

object VoIP::get_visualization() {
    return _internal_storage.get("visualization");
}

void VoIP::set_visualization(object value) {
    _internal_storage["visualization"] = value;
}

bool VoIP::play(const char* path) {
    FILE *tmp = fopen(path, "rb");

    if (tmp == NULL) {
        throw "Could not open file!";
        return false;
    }

    MutexGuard m(input_mutex);
    input_files.push(tmp);

    return true;
}

bool VoIP::play_on_hold(boost::python::list paths) {
    FILE *tmp = NULL;

    MutexGuard m(input_mutex);
    while (hold_files.size()) {
        fclose(hold_files.front());
        hold_files.pop();
    }
    for (int i=0; i < len(paths); ++i) {
        const char* path = extract<const char*>(paths[i]);
        tmp = fopen(path, "rb");
        if (tmp == NULL) {
            throw "Could not open file!";
            return false;
        }
        hold_files.push(tmp);
    }
    return true;
}

bool VoIP::set_output_file(const char* path) {
    MutexGuard m(output_mutex);

    if (output_file != NULL) {
        fclose(output_file);
        output_file = NULL;
    }
    output_file = fopen(path, "wb");
    if (output_file == NULL) {
        throw "Could not open file!";
        return false;
    }
    return true;
}

bool VoIP::unset_output_file() {
    if (output_file == NULL) {
        return false;
    }

    MutexGuard m(output_mutex);
    fflush(output_file);
    fclose(output_file);
    output_file = NULL;

    return true;
}

const char* VoIP::get_version() {
    return VoIPController::GetVersion();
}

long VoIP::get_preferred_relay_id() {
    return inst->GetPreferredRelayID();
}

int VoIP::get_last_error() {
    return inst->GetLastError();
}

dict VoIP::get_stats() {
    dict stats;
    VoIPController::TrafficStats _stats;
    inst->GetStats(&_stats);
    stats["bytesSentWifi"] = (int64_t)_stats.bytesSentWifi;
    stats["bytesSentMobile"] = (int64_t)_stats.bytesSentMobile;
    stats["bytesRecvdWifi"] = (int64_t)_stats.bytesRecvdWifi;
    stats["bytesRecvdMobile"] = (int64_t)_stats.bytesRecvdMobile;
    return stats;
}

dict VoIP::get_debug_log() {
    dict data;
    string encoded = inst->GetDebugLog();
    if (!encoded.empty()) {
        object json = import("json");
        data = (dict)json.attr("loads")(encoded);
    }
    return data;
}

string VoIP::get_debug_string() {
    return inst->GetDebugString();
}

int VoIP::get_signal_bars_count() {
    return inst->GetSignalBarsCount();
}

int64_t VoIP::get_peer_capabilities() {
    return (int64_t)inst->GetPeerCapabilities();
}

void VoIP::request_call_upgrade() {
    return inst->RequestCallUpgrade();
}

void VoIP::send_group_call_key(unsigned char *key) {
    inst->SendGroupCallKey(key);
}

void VoIP::debug_ctl(int request, int param) {
    inst->DebugCtl(request, param);
}

void VoIP::set_bitrate(int value) {
    inst->DebugCtl(1, value);
}

int VoIP::get_connection_max_layer() {
    return inst->GetConnectionMaxLayer();
}

void VoIP::set_mic_mute(bool mute) {
    inst->SetMicMute(mute);
}

void VoIP::set_handler(object _handler) {
    handler = _handler;
}

object VoIP::get_protocol() {
    return _internal_storage["protocol"];
}

int VoIP::get_state() {
    return state;
}

bool VoIP::is_playing() {
    return playing;
}

object VoIP::when_created() {
    return _internal_storage.get("created");
}

bool VoIP::is_creator() {
    return _internal_storage["creator"];
}

int VoIP::get_other_id() {
    return other_id;
}

object VoIP::get_call_id() {
    return _internal_storage["call_id"];
}

int VoIP::get_call_state() {
    return call_state;
}

void VoIP::close() {
    deinit_voip_controller();
}

void VoIP::parse_config() {
    if (!configuration.has_key("auth_key"))
        return;

    VoIPController::Config cfg;
    cfg.recvTimeout = extract<double>(configuration["recv_timeout"]);
    cfg.initTimeout = extract<double>(configuration["init_timeout"]);
    cfg.dataSaving = extract<int>(configuration["data_saving"]);
    cfg.enableAEC = extract<bool>(configuration["enable_AEC"]);
    cfg.enableNS = extract<bool>(configuration["enable_NS"]);
    cfg.enableAGC = extract<bool>(configuration["enable_AGC"]);
    cfg.enableCallUpgrade = extract<bool>(configuration.get("enable_call_upgrade"));

    if (configuration.has_key("log_file_path")) {
        string log_file_path = extract<string>(configuration["log_file_path"]);
        cfg.logFilePath = log_file_path;
    }

    if (configuration.has_key("stats_dump_file_path")) {
        std::string stats_dump_file_path = extract<string>(configuration["stats_dump_file_path"]);
        cfg.statsDumpFilePath = stats_dump_file_path;
    }

    ServerConfig::GetSharedInstance()->Update(extract<string>(configuration["shared_config"]));
    inst->SetConfig(cfg);

    char *key = (char *)malloc(256);
    string auth_key = extract<string>(configuration["auth_key"]);
    memcpy(key, auth_key.c_str(), 256);
    inst->SetEncryptionKey(key, (bool)_internal_storage["creator"]);
    free(key);

    vector<Endpoint> eps;
    boost::python::list endpoints = extract<boost::python::list>(configuration["endpoints"]);
    for (int i = 0; i < len(endpoints); ++i) {
        string ip = extract<string>(endpoints[i].attr("ip"));
        string ipv6 = extract<string>(endpoints[i].attr("ipv6"));
        string peer_tag = extract<string>(endpoints[i].attr("peer_tag"));

        IPv4Address v4addr(ip);
        IPv6Address v6addr("::0");
        unsigned char *pTag = (unsigned char *)malloc(16);

        if (!ipv6.empty())
            v6addr = IPv6Address(ipv6);

        if (!peer_tag.empty())
            memcpy(pTag, peer_tag.c_str(), 16);

        eps.push_back(Endpoint(extract<int64_t>(endpoints[i].attr("id")), extract<int16_t>(endpoints[i].attr("port")), v4addr, v6addr, Endpoint::UDP_RELAY, pTag));
        eps.push_back(Endpoint(extract<int64_t>(endpoints[i].attr("id")), extract<int16_t>(endpoints[i].attr("port")), v4addr, v6addr, Endpoint::TCP_RELAY, pTag));
        free(pTag);
    }

    inst->SetRemoteEndpoints(eps, extract<bool>(_internal_storage["protocol"]["udp_p2p"]), extract<int>(_internal_storage["protocol"]["max_layer"]));
    inst->SetNetworkType(extract<int>(configuration["network_type"]));
    if (configuration.has_key("proxy"))
        inst->SetProxy(
                extract<int>(configuration["proxy"]["protocol"]),
                extract<string>(configuration["proxy"]["address"]),
                extract<int16_t>(configuration["proxy"]["port"]),
                extract<string>(configuration["proxy"]["username"]),
                extract<string>(configuration["proxy"]["password"])
        );
}

BOOST_PYTHON_MODULE(_tgvoip) {
    class_<VoIP, boost::noncopyable>("VoIP")
        .def(init<object, int, object, object, int, object>())
        .def("discard", &VoIP::discard)
        .def("accept", &VoIP::accept)
        .def("start_the_magic", &VoIP::start_the_magic)
        .def("get_visualization", &VoIP::get_visualization)
        .def("set_visualization", &VoIP::set_visualization)
        .def("then", &VoIP::play)
        .def("play", &VoIP::play)
        .def("play_on_hold", &VoIP::play_on_hold)
        .def("set_output_file", &VoIP::set_output_file)
        .def("unset_output_file", &VoIP::unset_output_file)
        .def("get_version", &VoIP::get_version)
        .def("get_preferred_relay_id", &VoIP::get_preferred_relay_id)
        .def("get_last_error", &VoIP::get_last_error)
        .def("get_stats", &VoIP::get_stats)
        .def("get_debug_log", &VoIP::get_debug_log)
        .def("get_debug_string", &VoIP::get_debug_string)
        .def("get_signal_bars_count", &VoIP::get_signal_bars_count)
        .def("get_peer_capabilities", &VoIP::get_peer_capabilities)
        .def("request_call_upgrade", &VoIP::request_call_upgrade)
        .def("send_group_call_key", &VoIP::send_group_call_key)
        .def("debug_ctl", &VoIP::debug_ctl)
        .def("set_bitrate", &VoIP::set_bitrate)
        .def("set_mic_mute", &VoIP::set_mic_mute)
        .def("set_handler", &VoIP::set_handler)
        .def("get_protocol", &VoIP::get_protocol)
        .def("get_state", &VoIP::get_state)
        .def("is_playing", &VoIP::is_playing)
        .def("when_created", &VoIP::when_created)
        .def("is_creator", &VoIP::is_creator)
        .def("get_other_id", &VoIP::get_other_id)
        .def("get_call_id", &VoIP::get_call_id)
        .def("get_call_state", &VoIP::get_call_state)
        .def("close", &VoIP::close)
        .def("parse_config", &VoIP::parse_config)

        .def("get_connection_max_layer", &VoIP::get_connection_max_layer)
        
        .def_readwrite("configuration", &VoIP::configuration)
        .def_readwrite("storage", &VoIP::storage)
        .def_readwrite("_internal_storage", &VoIP::_internal_storage)
        .def_readwrite("handler", &VoIP::handler)

        .setattr("STATE_CREATED", (int)0)
        .setattr("STATE_WAIT_INIT", (int)STATE_WAIT_INIT)
        .setattr("STATE_WAIT_INIT_ACK", (int)STATE_WAIT_INIT_ACK)
        .setattr("STATE_ESTABLISHED", (int)STATE_ESTABLISHED)
        .setattr("STATE_FAILED", (int)STATE_FAILED)
        .setattr("STATE_RECONNECTING", (int)STATE_RECONNECTING)

        .setattr("TGVOIP_ERROR_UNKNOWN", (int)ERROR_UNKNOWN)
        .setattr("TGVOIP_ERROR_INCOMPATIBLE", (int)ERROR_INCOMPATIBLE)
        .setattr("TGVOIP_ERROR_TIMEOUT", (int)ERROR_TIMEOUT)
        .setattr("TGVOIP_ERROR_AUDIO_IO", (int)ERROR_AUDIO_IO)
        .setattr("TGVOIP_ERROR_PROXY", (int)ERROR_PROXY)

        .setattr("NET_TYPE_UNKNOWN", (int)NET_TYPE_UNKNOWN)
        .setattr("NET_TYPE_GPRS", (int)NET_TYPE_GPRS)
        .setattr("NET_TYPE_EDGE", (int)NET_TYPE_EDGE)
        .setattr("NET_TYPE_3G", (int)NET_TYPE_3G)
        .setattr("NET_TYPE_HSPA", (int)NET_TYPE_HSPA)
        .setattr("NET_TYPE_LTE", (int)NET_TYPE_LTE)
        .setattr("NET_TYPE_WIFI", (int)NET_TYPE_WIFI)
        .setattr("NET_TYPE_ETHERNET", (int)NET_TYPE_ETHERNET)
        .setattr("NET_TYPE_OTHER_HIGH_SPEED", (int)NET_TYPE_OTHER_HIGH_SPEED)
        .setattr("NET_TYPE_OTHER_LOW_SPEED", (int)NET_TYPE_OTHER_LOW_SPEED)
        .setattr("NET_TYPE_DIALUP", (int)NET_TYPE_DIALUP)
        .setattr("NET_TYPE_OTHER_MOBILE", (int)NET_TYPE_OTHER_MOBILE)

        .setattr("DATA_SAVING_NEVER", (int)DATA_SAVING_NEVER)
        .setattr("DATA_SAVING_MOBILE", (int)DATA_SAVING_MOBILE)
        .setattr("DATA_SAVING_ALWAYS", (int)DATA_SAVING_ALWAYS)

        .setattr("PROXY_NONE", (int)PROXY_NONE)
        .setattr("PROXY_SOCKS5", (int)PROXY_SOCKS5)

        .setattr("AUDIO_STATE_NONE", AUDIO_STATE_NONE)
        .setattr("AUDIO_STATE_CREATED", AUDIO_STATE_CREATED)
        .setattr("AUDIO_STATE_CONFIGURED", AUDIO_STATE_CONFIGURED)
        .setattr("AUDIO_STATE_RUNNING", AUDIO_STATE_RUNNING)

        .setattr("CALL_STATE_NONE", CALL_STATE_NONE)
        .setattr("CALL_STATE_REQUESTED", CALL_STATE_REQUESTED)
        .setattr("CALL_STATE_INCOMING", CALL_STATE_INCOMING)
        .setattr("CALL_STATE_ACCEPTED", CALL_STATE_ACCEPTED)
        .setattr("CALL_STATE_CONFIRMED", CALL_STATE_CONFIRMED)
        .setattr("CALL_STATE_READY", CALL_STATE_READY)
        .setattr("CALL_STATE_ENDED", CALL_STATE_ENDED)

        .setattr("TGVOIP_PEER_CAP_GROUP_CALLS", TGVOIP_PEER_CAP_GROUP_CALLS)
        ;
}
