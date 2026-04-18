# XequeSoundDesign

This project explores real-time sonification of chess as an interactive and embodied audiovisual system.

A custom Python interface (based on `python-chess` and `pygame`) captures game state and events, which are transmitted via Open Sound Control (OSC) to a Max/MSP patch. The Max environment maps these events to a sample-based sound engine, generating both discrete sonic events (moves, captures, checks) and continuous sound layers reflecting the evolving board state.

The system is designed as a modular pipeline:

Python (interaction & analysis) → OSC → Max/MSP (sound synthesis)

The goal is not only to represent chess moves, but to translate structural and dynamic properties of the game—such as piece activity, spatial relationships, and positional tension—into sound.

## Features

- Real-time chess interaction (Pygame interface)
- Legal move validation via `python-chess`
- OSC communication layer for modularity
- Sample-based sound engine in Max/MSP
- Event-based sonification (moves, captures, checks)
- State-based sonification (piece positions, board structure)
- Optional engine evaluation (Stockfish integration)
- Designed for extension toward perceptual and embodied interaction (e.g. vision-based input)

## Research Context

This project is developed as part of a Master's thesis in Sound and Music Computing, focusing on:

- Sonification of complex systems
- Embodied interaction
- Mapping strategies between symbolic systems and sound
- Real-time audiovisual performance systems
