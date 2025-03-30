# Modbus TCP Scanner

A powerful Python tool for scanning RS-485 bus devices via Modbus TCP gateways.

## Overview

This script provides an enhanced way to discover and identify Modbus devices connected to an RS-485 bus through a Modbus TCP gateway. It implements advanced scanning strategies and comprehensive device interrogation to maximize the chances of finding all connected devices.

## Features

- Compatible with both pymodbus 2.x and 3.x versions
- Optimized scanning strategy (prioritizing commonly used addresses)
- Multiple connection retry attempts with error handling
- Extended register checking across various Modbus functions:
  - Read Holding Registers (function 3)
  - Read Input Registers (function 4)
  - Read Coils (function 1)
  - Read Discrete Inputs (function 2)
- Detailed reporting of discovered devices and their capabilities
- Practical troubleshooting suggestions when no devices are found

## Requirements

- Python 3.x
- pymodbus library (works with both 2.x and 3.x versions)

## Installation

1. Ensure Python 3.x is installed
2. Install the required dependencies:

```bash
pip install pymodbus
```

## Configuration

Edit the following parameters at the top of the script to match your setup:

```python
# Connection settings
GATEWAY_IP = "192.168.1.58"  # Change to your gateway IP
GATEWAY_PORT = 502           # Default Modbus TCP port
TIMEOUT = 2                  # Timeout in seconds

# Scanning range
START_ADDRESS = 1
END_ADDRESS = 247            # Full range of Modbus addresses

# Known addresses to check first
KNOWN_ADDRESSES = [16, 1, 2, 3, 8, 10, 20, 32, 64, 100, 127, 200, 240]
```

## Usage

Simply run the script:

```bash
python modbustcp-scanner.py
```

The script will:
1. Connect to the specified Modbus TCP gateway
2. Scan all addresses in the optimized order
3. Report any discovered devices with their supported functions and register data
4. Provide troubleshooting suggestions if no devices are found

## Troubleshooting

If no devices are found, the script suggests the following actions:

1. Check physical connections (cables, power) of devices to the gateway
2. Verify port settings on the gateway (baud rate, parity, stop bits)
3. Ensure devices are configured with supported communication parameters
4. Test the gateway with other software tools (e.g., Modbus Poll)
5. Consider adding terminators at the ends of the RS-485 line

## Advanced Use

You can customize the script for your specific needs by:

- Modifying the `REGISTERS_TO_CHECK` list to target specific registers
- Adding known device addresses to the `KNOWN_ADDRESSES` list for faster detection
- Adjusting the timeout value for slower networks or devices

## License

This project is provided as-is, free to use and modify.

## Contributions

Contributions, bug reports, and feature requests are welcome!
