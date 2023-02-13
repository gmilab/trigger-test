# Simple GUI tool to test each pin of a standard 8-bit trigger cable
Compatible with IEEE1284 parallel port in ECP mode or the Neurospec MMBT-S USB/serial trigger interface box.

## Installation
### Parallel port mode
1. Install the inpoutx64.dll driver into C:\Windows\system32
1. Uncomment parallel port initialization code in the triggertest.py file under init()
1. Comment serial port initialization code
1. Set the memory address for your parallel port

### Serial port mode
1. Uncomment serial port init code / comment parallel port init code in triggertest.py
1. Set the correct COM port

