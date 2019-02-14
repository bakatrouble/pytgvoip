# pytgvoip
Examples require tweaking (set app_id and app_hash, change usernames)

## Running examples

```bash
$ cd example
$ wget https://github.com/danog/MadelineProto/raw/master/input.raw  # download sample stream to play
$ python make_call.py  # or receive_call.py, alsa.py
```

### make_call.py
Makes outgoing calls, plays `input.raw` in loop to the callee and records callee's voice to `output.raw`

Change username to call and run

### receive_call.py
Answers incoming calls, plays `input.raw` in loop to the caller and records caller's voice to `output.raw`

### alsa.py
Makes outgoing calls, uses ALSA to output/receive sound through system devices (speakers/mic)

Requires installed `pyalsaaudio`
