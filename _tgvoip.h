#ifndef PYLIBTGVOIP_LIBRARY_H
#define PYLIBTGVOIP_LIBRARY_H

#include <iostream>
#include <pybind11/pybind11.h>
#include "libtgvoip/VoIPController.h"
#include "libtgvoip/VoIPServerConfig.h"

namespace pybind11 {
    class not_implemented_error : public std::exception {};
};

namespace py = pybind11;

enum NetType {
    NET_UNKNOWN = tgvoip::NET_TYPE_UNKNOWN,
    GPRS = tgvoip::NET_TYPE_GPRS,
    EDGE = tgvoip::NET_TYPE_EDGE,
    NET_3G = tgvoip::NET_TYPE_3G,
    HSPA = tgvoip::NET_TYPE_HSPA,
    LTE = tgvoip::NET_TYPE_LTE,
    WIFI = tgvoip::NET_TYPE_WIFI,
    ETHERNET = tgvoip::NET_TYPE_ETHERNET,
    OTHER_HIGH_SPEED = tgvoip::NET_TYPE_OTHER_HIGH_SPEED,
    OTHER_LOW_SPEED = tgvoip::NET_TYPE_OTHER_LOW_SPEED,
    DIALUP = tgvoip::NET_TYPE_DIALUP,
    OTHER_MOBILE = tgvoip::NET_TYPE_OTHER_MOBILE,
};

enum CallState {
    WAIT_INIT = tgvoip::STATE_WAIT_INIT,
    WAIT_INIT_ACK = tgvoip::STATE_WAIT_INIT_ACK,
    ESTABLISHED = tgvoip::STATE_ESTABLISHED,
    FAILED = tgvoip::STATE_FAILED,
    RECONNECTING = tgvoip::STATE_RECONNECTING,
};

enum DataSaving {
    NEVER = tgvoip::DATA_SAVING_NEVER,
    MOBILE = tgvoip::DATA_SAVING_MOBILE,
    ALWAYS = tgvoip::DATA_SAVING_ALWAYS,
};

struct Stats {
    uint64_t bytes_sent_wifi;
    uint64_t bytes_sent_mobile;
    uint64_t bytes_recvd_wifi;
    uint64_t bytes_recvd_mobile;
};

struct Endpoint {
    Endpoint(int64_t id, const std::string &ip, const std::string &ipv6, uint16_t port, const std::string &peer_tag);
    int64_t id;
    std::string ip;
    std::string ipv6;
    uint16_t port;
    std::string peer_tag;
};

class VoIPController {
public:
    VoIPController();
    explicit VoIPController(const std::string &_persistent_state_file);
    ~VoIPController();
    void start();
    void connect();
    void set_proxy(const std::string &address, uint16_t port, const std::string &username, const std::string &password);
    void set_encryption_key(char *key, bool is_outgoing);
    void set_remote_endpoints(std::list<Endpoint> endpoints, bool allow_p2p, bool tcp, int connection_max_layer);
    std::string get_debug_string();
    void set_network_type(NetType type);
    void set_mic_mute(bool mute);
    void set_config(double recv_timeout, double init_timeout, DataSaving data_saving_mode, bool enable_aec,
            bool enable_ns, bool enable_agc, const std::string &log_file_path, const std::string &status_dump_path,
            bool log_packet_stats);
    void debug_ctl(int request, int param);
    long get_preferred_relay_id();
    int get_last_error();
    Stats get_stats();
    std::string get_debug_log();
    void set_audio_output_gain_control_enabled(bool enabled);
    void set_echo_cancellation_strength(int strength);
    int get_peer_capabilities();
    bool need_rate();

    // callbacks
    virtual void handle_state_change(CallState state);
    virtual void handle_signal_bars_change(int count);

    static std::string get_version(py::object /* cls */);
    static int connection_max_layer(py::object /* cls */);

    std::string persistent_state_file;

private:
    tgvoip::VoIPController *ctrl;
};

class PyVoIPController : public VoIPController {
    using VoIPController::VoIPController;

    void handle_state_change(CallState state) override {
        PYBIND11_OVERLOAD(void, VoIPController, handle_state_change, state);
    };
    void handle_signal_bars_change(int count) override {
        PYBIND11_OVERLOAD(void, VoIPController, handle_signal_bars_change, count);
    };
};

class VoIPServerConfig {
public:
    static void set_config(py::object cls, std::string &json_str);
};

#endif