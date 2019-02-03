#ifndef PYLIBTGVOIP_H
#define PYLIBTGVOIP_H

#include "libtgvoip/VoIPController.h"
#include <boost/python.hpp>
#include <stdio.h>
#include "libtgvoip/threading.h"
#include <queue>

#define AUDIO_STATE_NONE -1
#define AUDIO_STATE_CREATED 0
#define AUDIO_STATE_CONFIGURED 1
#define AUDIO_STATE_RUNNING 2

#define CALL_STATE_NONE -1
#define CALL_STATE_REQUESTED 0
#define CALL_STATE_INCOMING 1
#define CALL_STATE_ACCEPTED 2
#define CALL_STATE_CONFIRMED 3
#define CALL_STATE_READY 4
#define CALL_STATE_ENDED 5

using namespace boost::python;
using namespace tgvoip;
using namespace tgvoip::audio;
using namespace std;

namespace tgvoip {
    namespace audio {
        class AudioInputModule;
        class AudioOutputModule;
    }
}

namespace boost {
    namespace python {
        bool hasattr(object o, string const name) {
            return PyObject_HasAttrString(o.ptr(), name.c_str());
        }
    }
}

class VoIP {
public:
    VoIP();
    VoIP(bool creator, int other_id, object call_id, object handler, int call_state, object protocol);
    VoIP(const VoIP &voip);
    void init_voip_controller();
    bool discard(str reason, object rating, bool debug);
    bool accept();
    void deinit_voip_controller();
//    void __wakeup();
//    // Php::Value __sleep();

    bool start_the_magic();

    void recv_audio_frame(int16_t* data, size_t size);
    void send_audio_frame(int16_t* data, size_t size);

    object get_visualization();
    void set_visualization(object value);

    bool play(const char* path);
    bool play_on_hold(boost::python::list paths);
    bool set_output_file(const char* path);
    bool unset_output_file();

    const char* get_version();
    long get_preferred_relay_id();
    int get_last_error();
    dict get_stats();
    dict get_debug_log();
    string get_debug_string();
    int get_signal_bars_count();
    int64_t get_peer_capabilities();
    void request_call_upgrade();
    void send_group_call_key(unsigned char *key);
    void debug_ctl(int request, int param);
    void set_bitrate(int bitrate);

    void set_mic_mute(bool mute);
    void set_handler(object handler);

    object get_protocol();
    int get_state();
    bool is_playing();
//    object is_destroyed();
    object when_created();
    bool is_creator();
    int get_other_id();
    object get_call_id();
    int get_call_state();
    void close();

    dict configuration;
    dict storage;
    dict _internal_storage;
    object handler;

    int state = STATE_CREATED;

    bool playing = false;
    bool destroyed = false;

    void parse_config();
//    void parse_proxy_config();
    int other_id;

private:
    std::queue<FILE *> input_files;
    std::queue<FILE *> hold_files;
    tgvoip::Mutex input_mutex;

    FILE *output_file;
    tgvoip::Mutex output_mutex;

    size_t read_input;
    size_t read_output;
    int call_state = CALL_STATE_NONE;
    VoIPController *inst;
};

#endif
