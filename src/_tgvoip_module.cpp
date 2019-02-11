#include "_tgvoip.h"
#include <sstream>
#include <chrono>

PYBIND11_MODULE(_tgvoip, m) {
    py::register_exception_translator([](std::exception_ptr p) {
        try {
            if (p) std::rethrow_exception(p);
        } catch (const py::not_implemented_error &e) {
            PyErr_SetString(PyExc_NotImplementedError, "");
        }
    });

    py::enum_<NetType>(m, "NetType")
            .value("UNKNOWN", NetType::NET_TYPE_UNKNOWN)
            .value("GPRS", NetType::NET_TYPE_GPRS)
            .value("EDGE", NetType::NET_TYPE_EDGE)
            .value("NET_3G", NetType::NET_TYPE_3G)
            .value("HSPA", NetType::NET_TYPE_HSPA)
            .value("LTE", NetType::NET_TYPE_LTE)
            .value("WIFI", NetType::NET_TYPE_WIFI)
            .value("ETHERNET", NetType::NET_TYPE_ETHERNET)
            .value("OTHER_HIGH_SPEED", NetType::NET_TYPE_OTHER_HIGH_SPEED)
            .value("OTHER_LOW_SPEED", NetType::NET_TYPE_OTHER_LOW_SPEED)
            .value("DIALUP", NetType::NET_TYPE_DIALUP)
            .value("OTHER_MOBILE", NetType::NET_TYPE_OTHER_MOBILE);

    py::enum_<CallState>(m, "CallState")
            .value("WAIT_INIT", CallState::STATE_WAIT_INIT)
            .value("WAIT_INIT_ACK", CallState::STATE_WAIT_INIT_ACK)
            .value("ESTABLISHED", CallState::STATE_ESTABLISHED)
            .value("FAILED", CallState::STATE_FAILED)
            .value("RECONNECTING", CallState::STATE_RECONNECTING);

    py::enum_<DataSaving>(m, "DataSaving")
            .value("NEVER", DataSaving::DATA_SAVING_NEVER)
            .value("MOBILE", DataSaving::DATA_SAVING_MOBILE)
            .value("ALWAYS", DataSaving::DATA_SAVING_ALWAYS);

    py::enum_<CallError>(m, "CallError")
            .value("UNKNOWN", CallError::ERROR_UNKNOWN)
            .value("INCOMPATIBLE", CallError::ERROR_INCOMPATIBLE)
            .value("TIMEOUT", CallError::ERROR_TIMEOUT)
            .value("AUDIO_IO", CallError::ERROR_AUDIO_IO)
            .value("PROXY", CallError::ERROR_PROXY);

    py::class_<Stats>(m, "Stats")
            .def_readonly("bytes_sent_wifi", &Stats::bytes_sent_wifi)
            .def_readonly("bytes_sent_mobile", &Stats::bytes_sent_mobile)
            .def_readonly("bytes_recvd_wifi", &Stats::bytes_recvd_wifi)
            .def_readonly("bytes_recvd_mobile", &Stats::bytes_recvd_mobile)
            .def("__repr__", [](const Stats &s) {
                std::ostringstream repr;
                repr << "<_tgvoip.Stats ";
                repr << "bytes_sent_wifi=" << s.bytes_sent_wifi << " ";
                repr << "bytes_sent_mobile=" << s.bytes_sent_mobile << " ";
                repr << "bytes_recvd_wifi=" << s.bytes_recvd_wifi << " ";
                repr << "bytes_recvd_mobile=" << s.bytes_recvd_mobile << ">";
                return repr.str();
            });

    py::class_<Endpoint>(m, "Endpoint")
            .def(py::init<long, const std::string &, const std::string &, int, const std::string &>())
            .def_readwrite("_id", &Endpoint::id)
            .def_readwrite("ip", &Endpoint::ip)
            .def_readwrite("ipv6", &Endpoint::ipv6)
            .def_readwrite("port", &Endpoint::port)
            .def_readwrite("peer_tag", &Endpoint::peer_tag)
            .def("__repr__", [](const Endpoint &e) {
                std::ostringstream repr;
                repr << "<_tgvoip.Endpoint ";
                repr << "_id=" << e.id << " ";
                repr << "ip=\"" << e.ip << "\" ";
                repr << "ipv6=\"" << e.ipv6 << "\" ";
                repr << "port=" << e.port << ">";
                // repr << "peer_tag=" << e.peer_tag << ">";
                return repr.str();
            });

    py::class_<tgvoip::AudioInputDevice>(m, "AudioInputDevice")
            .def_readonly("_id", &tgvoip::AudioInputDevice::id)
            .def_readonly("display_name", &tgvoip::AudioInputDevice::displayName)
            .def("__repr__", [](const tgvoip::AudioInputDevice &d) {
                std::ostringstream repr;
                repr << "<_tgvoip.AudioInputDevice ";
                repr << "_id=\"" << d.id << "\" ";
                repr << "display_name=\"" << d.displayName << "\">";
                return repr.str();
            });

    py::class_<tgvoip::AudioOutputDevice>(m, "AudioOutputDevice")
            .def_readonly("_id", &tgvoip::AudioOutputDevice::id)
            .def_readonly("display_name", &tgvoip::AudioOutputDevice::displayName)
            .def("__repr__", [](const tgvoip::AudioOutputDevice &d) {
                std::ostringstream repr;
                repr << "<_tgvoip.AudioOutputDevice ";
                repr << "_id=\"" << d.id << "\" ";
                repr << "display_name=\"" << d.displayName << "\">";
                return repr.str();
            });

    py::class_<VoIPController, PyVoIPController>(m, "VoIPController")
            .def(py::init<>())
            .def(py::init<const std::string &>())
            .def("_init", &VoIPController::init)
            .def("start", &VoIPController::start)
            .def("connect", &VoIPController::connect)
            .def("set_proxy", &VoIPController::set_proxy)
            .def("set_encryption_key", &VoIPController::set_encryption_key)
            .def("set_remote_endpoints", &VoIPController::set_remote_endpoints)
            .def("get_debug_string", &VoIPController::get_debug_string)
            .def("set_network_type", &VoIPController::set_network_type)
            .def("set_mic_mute", &VoIPController::set_mic_mute)
            .def("set_config", &VoIPController::set_config)
            .def("debug_ctl", &VoIPController::debug_ctl)
            .def("get_preferred_relay_id", &VoIPController::get_preferred_relay_id)
            .def("get_last_error", &VoIPController::get_last_error)
            .def("get_stats", &VoIPController::get_stats)
            .def("get_debug_log", &VoIPController::get_debug_log)
            .def("set_audio_output_gain_control_enabled", &VoIPController::set_audio_output_gain_control_enabled)
            .def("set_echo_cancellation_strength", &VoIPController::set_echo_cancellation_strength)
            .def("get_peer_capabilities", &VoIPController::get_peer_capabilities)
            .def("need_rate", &VoIPController::need_rate)
            .def("enumerate_audio_inputs", &VoIPController::enumerate_audio_inputs)
            .def("enumerate_audio_outputs", &VoIPController::enumerate_audio_outputs)
            .def("set_current_audio_input", &VoIPController::set_current_audio_input)
            .def("set_current_audio_output", &VoIPController::set_current_audio_output)
            .def("get_current_audio_input_id", &VoIPController::get_current_audio_input_id)
            .def("get_current_audio_output_id", &VoIPController::get_current_audio_output_id)
            .def("handle_state_change", &VoIPController::handle_state_change)
            .def("handle_signal_bars_change", &VoIPController::handle_signal_bars_change)
            .def_readonly("persistent_state_file", &VoIPController::persistent_state_file)
            .def_property_readonly_static("LIBTGVOIP_VERSION", &VoIPController::get_version)
            .def_property_readonly_static("CONNECTION_MAX_LAYER", &VoIPController::connection_max_layer);

    py::class_<VoIPServerConfig>(m, "VoIPServerConfig")
            .def_static("set_config", &VoIPServerConfig::set_config);

#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}
