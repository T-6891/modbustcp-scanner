# Modbus RTU/TCP Scanner

A comprehensive utility for scanning Modbus networks to discover and analyze connected devices through TCP gateways. This tool is especially useful for industrial automation environments where you need to identify and inspect Modbus devices connected to RS-485 networks via Ethernet gateways.

## Features

- **Universal Device Discovery**: Detects any Modbus-compatible device on the RS-485 bus
- **Multi-Function Support**: Tests devices using all standard Modbus functions (Coils, Discrete Inputs, Holding and Input Registers)
- **Smart Scanning Strategy**: Prioritizes common Modbus addresses before scanning the entire address space
- **Version-Agnostic**: Compatible with both pymodbus 2.x and 3.x versions
- **Detailed Device Analysis**: Reports supported functions and register data for each discovered device
- **Fault-Tolerant**: Multiple connection attempts with appropriate timeouts and error handling
- **Diagnostic Recommendations**: Provides troubleshooting suggestions when devices aren't found

## Requirements

- Python 3.6 or higher
- pymodbus library

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/modbustcp-scanner.git
   cd modbustcp-scanner
   ```

2. Install the required dependencies:
   ```bash
   pip install pymodbus
   ```

## Usage

1. Configure the script by editing the following parameters at the top of the file:
   - `GATEWAY_IP`: IP address of your Modbus TCP gateway (default: "192.168.1.58")
   - `GATEWAY_PORT`: TCP port of your gateway (default: 502)
   - `TIMEOUT`: Connection timeout in seconds (default: 2)
   - `START_ADDRESS` and `END_ADDRESS`: Modbus address range to scan

2. Run the script:
   ```bash
   python modbus_scanner.py
   ```

3. The script will:
   - Connect to the specified gateway
   - Scan the network for Modbus devices
   - Display discovered devices with their supported functions
   - Show sample register data from each device

## Example Output

```
Улучшенный сканер Modbus устройств
==================================================
Версия pymodbus: 3.8.6
Используем импорты для pymodbus 3.x
Успешное подключение к 192.168.1.58:502
Сканирование Modbus устройств...
--------------------------------------------------
Сканирование 260 адресов...

Найдено устройство на адресе 16
  Поддерживаемые функции:
  - Read Holding Registers
  - Read Input Registers
  Данные из регистров:
  - Func3_Reg0: [235]
  - Func3_Reg1: [456]
  - Func4_Reg0: [235]

==================================================
Найдено устройств: 1
Адреса: 16

Детальная информация об устройствах:
Устройство на адресе 16:
  Поддерживаемые функции:
  - Read Holding Registers
  - Read Input Registers
Соединение закрыто
```

## Advanced Configuration

### Custom Address Lists

You can add known device addresses to the `KNOWN_ADDRESSES` list to prioritize checking these addresses first:

```python
KNOWN_ADDRESSES = [16, 1, 2, 3, 8, 10, 20, 32, 64, 100, 127, 200, 240]
```

### Testing Specific Register Ranges

Modify the `REGISTERS_TO_CHECK` list to test different register combinations:

```python
REGISTERS_TO_CHECK = [
    # Function 3 - Holding Registers
    (3, 0, 1),    # Standard first register
    (3, 1000, 1), # Another commonly used starting register
    # Add your custom register ranges here
]
```

## Troubleshooting

If the scanner doesn't find any devices:

1. Verify physical connections (cables, power supplies)
2. Check gateway RS-485 port settings (baud rate, parity, stop bits)
3. Ensure your devices are configured to a supported speed (typically 9600 or 19200 bps)
4. Test the gateway with alternative software (like Modbus Poll)
5. Check if RS-485 line terminators (120 Ohm) are required

## For WB-MGE Gateway Users

When using the WB-MGE v.2 Modbus-Ethernet gateway, ensure:

1. The Serial Port settings match your device's configuration:
   - Correct Baud Rate (typically 9600 bps)
   - 8 Data Bits
   - No Parity (or match your device settings)
   - 1 Stop Bit (or match your device settings)

2. The Socket Configuration is set to:
   - TCP Server mode
   - Port 502 (standard Modbus TCP port)
   - ModbusTCP Poll enabled

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
