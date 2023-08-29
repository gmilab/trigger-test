# Simple GUI tool to test each pin of a standard 8-bit trigger cable
Compatible with IEEE1284 parallel port in ECP mode or the Neurospec MMBT-S USB/serial trigger interface box.

## Installation
``` bash
pip install -r requirements.txt
```

### Parallel port mode
1. Install the inpoutx64.dll driver into C:\Windows\system32
1. Uncomment parallel port section of config.yaml and update address (parallel port memory address is usually listed in the Resources tab in Device Manager for the each LPT port)

### Serial port mode
1. Uncomment serial port section of config.yaml
1. Set the correct COM port

## Background

All our PsychoPy and Presentation experiments are configured to send triggers for time-locking. These can be time-locked to anything; in typical usage, when the computer presents an image, it will simultaneously toggle a pin on the trigger box. The trigger channels are +5V and are recorded simultaneously with whatever data (typically EEG). Then we can identify the precise sample in the EEG where the trigger channel went from 0V to 5V. This could be easily adapted for non-EEG data collection as well.
