# Max patch structure

Open these files in Max:

- `main.maxpat`
- `patches/event_mapper.maxpat`
- `patches/state_mapper.maxpat`
- `patches/mixer.maxpat`
- `poly/eventVoice.maxpat`
- `poly/stateVoice.maxpat`

## Message flow

Python / OSC sends:

- `/move [piece_id fx fy tx ty capture check]`
- `/piece [piece_id x y pitch color]`
- `/evaluation [float]`
- `/fragility [float]`
- `/update_done [1]`

## What each patch does

- `main.maxpat` receives OSC and routes named streams.
- `patches/event_mapper.maxpat` reduces `/move` to symbolic event messages:
  - `normal <piece_id>`
  - `capture <piece_id>`
  - `check <piece_id>`
- `patches/state_mapper.maxpat` forwards `/piece` state and a `sync` message on `/update_done`.
- `patches/mixer.maxpat` sums the event and state layers into `mainL/mainR`.
- `poly/eventVoice.maxpat` plays placeholder move/capture/check samples.
- `poly/stateVoice.maxpat` plays placeholder looping state samples.

## Important

The sample file paths are placeholders. Replace them with your own WAV files.

These are starter patches following the modular structure we discussed. They are intentionally simple and designed to be the clean baseline before adding:
- multiple overlapping voices with `poly~`
- pan/filter mapping from x/y
- bank selection from evaluation or fragility
- more detailed event types (promotion, castling, mate)
