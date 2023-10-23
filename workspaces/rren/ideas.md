# Ideas for UI
:o
## Hardware
- 1 Pico for handling arm logic
- 1 Pico for handling mqtt (?)
- Purple board outputs 6v
- Red H-bridge outputs 12v

## Area of Confusion
- How will I send data to and from the Pico if I'm not using Adafruit IO?
- Is mqtt an option? Will the laptop itself serve as a broker while also operating the UI?
- Is BLE an option? Will the laptop then act as a (?) device, and the UI communicates over BLE?
  - Is this a reliable option, robust, and won't fail on repeated attempts?

## BLE Notes
- [To-Do] Get Laptop to Pico "UART" communication working.
- [To-Do] Get Pico to Pico from BLE communication working.
- [To-Do] Add controller communication, can be wired to arm, or wireless
- [To-Do] Add input system to record previous movements.
- [To-Do] Implement playback.
## UI Notes
- [To-Do] Create a basic "shell" to build on, add buttons, graphs.
- [To-Do] Link BLE communication to the UI
- [To-Do] Add MatPlotLib to create dashboard
- [To-Do] 