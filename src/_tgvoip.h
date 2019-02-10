#ifndef PYLIBTGVOIP_LIBRARY_H
#define PYLIBTGVOIP_LIBRARY_H

#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <VoIPController.h>
#include <VoIPServerConfig.h>

namespace pybind11 {
    class not_implemented_error : public std::exception {};
};

namespace py = pybind11;

enum NetType {
    NET_TYPE_UNKNOWN = tgvoip::NET_TYPE_UNKNOWN,
    NET_TYPE_GPRS = tgvoip::NET_TYPE_GPRS,
    NET_TYPE_EDGE = tgvoip::NET_TYPE_EDGE,
    NET_TYPE_3G = tgvoip::NET_TYPE_3G,
    NET_TYPE_HSPA = tgvoip::NET_TYPE_HSPA,
    NET_TYPE_LTE = tgvoip::NET_TYPE_LTE,
    NET_TYPE_WIFI = tgvoip::NET_TYPE_WIFI,
    NET_TYPE_ETHERNET = tgvoip::NET_TYPE_ETHERNET,
    NET_TYPE_OTHER_HIGH_SPEED = tgvoip::NET_TYPE_OTHER_HIGH_SPEED,
    NET_TYPE_OTHER_LOW_SPEED = tgvoip::NET_TYPE_OTHER_LOW_SPEED,
    NET_TYPE_DIALUP = tgvoip::NET_TYPE_DIALUP,
    NET_TYPE_OTHER_MOBILE = tgvoip::NET_TYPE_OTHER_MOBILE,
};

enum CallState {
    STATE_WAIT_INIT = tgvoip::STATE_WAIT_INIT,
    STATE_WAIT_INIT_ACK = tgvoip::STATE_WAIT_INIT_ACK,
    STATE_ESTABLISHED = tgvoip::STATE_ESTABLISHED,
    STATE_FAILED = tgvoip::STATE_FAILED,
    STATE_RECONNECTING = tgvoip::STATE_RECONNECTING,
};

enum DataSaving {
    DATA_SAVING_NEVER = tgvoip::DATA_SAVING_NEVER,
    DATA_SAVING_MOBILE = tgvoip::DATA_SAVING_MOBILE,
    DATA_SAVING_ALWAYS = tgvoip::DATA_SAVING_ALWAYS,
};

enum CallError {
    ERROR_UNKNOWN = tgvoip::ERROR_UNKNOWN,
    ERROR_INCOMPATIBLE = tgvoip::ERROR_INCOMPATIBLE,
    ERROR_TIMEOUT = tgvoip::ERROR_TIMEOUT,
    ERROR_AUDIO_IO = tgvoip::ERROR_AUDIO_IO,
    ERROR_PROXY = tgvoip::ERROR_PROXY,
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
    py::bytes peer_tag;
};

class VoIPController {
public:
    VoIPController();
    explicit VoIPController(const std::string &_persistent_state_file);
    ~VoIPController();
    void init();
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
    CallError get_last_error();
    Stats get_stats();
    std::string get_debug_log();
    void set_audio_output_gain_control_enabled(bool enabled);
    void set_echo_cancellation_strength(int strength);
    int get_peer_capabilities();
    bool need_rate();

    // callbacks
    virtual void handle_state_change(CallState state);
    virtual void handle_signal_bars_change(int count);
    void send_audio_frame(int16_t *buf, size_t size);
    void recv_audio_frame(int16_t *buf, size_t size);
    virtual char *send_audio_frame_impl(long len);
    virtual void recv_audio_frame_impl(py::bytes frame);

    static std::string get_version(py::object /* cls */);
    static int connection_max_layer(py::object /* cls */);

    std::string persistent_state_file;

private:
    tgvoip::VoIPController *ctrl;
    tgvoip::Mutex output_mutex;
    tgvoip::Mutex input_mutex;
};

class PyVoIPController : public VoIPController {
    using VoIPController::VoIPController;

    void handle_state_change(CallState state) override {
        PYBIND11_OVERLOAD(void, VoIPController, handle_state_change, state);
    };
    void handle_signal_bars_change(int count) override {
        PYBIND11_OVERLOAD(void, VoIPController, handle_signal_bars_change, count);
    };
    char *send_audio_frame_impl(long len) override {
        PYBIND11_OVERLOAD(char *, VoIPController, send_audio_frame_impl, len);
    };
    void recv_audio_frame_impl(py::bytes frame) override {
        PYBIND11_OVERLOAD(void, VoIPController, recv_audio_frame_impl, frame);
    };
};

class VoIPServerConfig {
public:
    static void set_config(std::string &json_str);
};

#endif