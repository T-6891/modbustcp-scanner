#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced script for scanning RS-485 bus through Modbus TCP gateway
with advanced device discovery capabilities
"""

import sys
import time
import pymodbus
from pymodbus.exceptions import ModbusIOException

print(f"pymodbus version: {pymodbus.__version__}")
major_version = int(pymodbus.__version__.split('.')[0])

if major_version >= 3:
    from pymodbus.client import ModbusTcpClient
    print("Using imports for pymodbus 3.x")
else:
    from pymodbus.client.sync import ModbusTcpClient
    print("Using imports for pymodbus 2.x")

# Connection settings
GATEWAY_IP = "192.168.1.58"
GATEWAY_PORT = 502
TIMEOUT = 2  # Increased timeout for slow devices

# Scanning range
START_ADDRESS = 1
END_ADDRESS = 247  # Full range of Modbus addresses

# Increased set of registers to check
REGISTERS_TO_CHECK = [
    # Function 3 - Holding Registers
    (3, 0, 1),    # Standard first register
    (3, 1, 1),    # Second register
    (3, 4, 1),    # Register often used in devices
    (3, 100, 1),  # Register often used for configuration
    (3, 1000, 1), # Another commonly used starting register
    
    # Function 4 - Input Registers
    (4, 0, 1),
    (4, 1, 1),
    (4, 30, 1),   # Register often used for readings
    
    # Function 1 - Coils
    (1, 0, 1),
    (1, 10, 1),
    
    # Function 2 - Discrete Inputs
    (2, 0, 1),
    (2, 10, 1)
]

# Known Modbus addresses to check (add your device addresses here if known)
KNOWN_ADDRESSES = [16, 1, 2, 3, 8, 10, 20, 32, 64, 100, 127, 200, 240]

def modbus_function_str(function_id):
    """Converts function number to readable description"""
    if function_id == 1:
        return "Read Coils"
    elif function_id == 2:
        return "Read Discrete Inputs"
    elif function_id == 3:
        return "Read Holding Registers"
    elif function_id == 4:
        return "Read Input Registers"
    elif function_id == 5:
        return "Write Single Coil"
    elif function_id == 6:
        return "Write Single Register"
    else:
        return f"Function {function_id}"

def execute_modbus_command(client, address, function_id, start_register, count):
    """Executes Modbus command considering library version"""
    try:
        if major_version >= 3:
            # Parameters for pymodbus 3.x
            slave_param = {"slave_address": address}
        else:
            # Parameters for pymodbus 2.x
            slave_param = {"unit": address}

        if function_id == 1:  # Read Coils
            response = client.read_coils(address=start_register, count=count, **slave_param)
        elif function_id == 2:  # Read Discrete Inputs
            response = client.read_discrete_inputs(address=start_register, count=count, **slave_param)
        elif function_id == 3:  # Read Holding Registers
            response = client.read_holding_registers(address=start_register, count=count, **slave_param)
        elif function_id == 4:  # Read Input Registers
            response = client.read_input_registers(address=start_register, count=count, **slave_param)
        else:
            return False, None

        # Check response
        if not hasattr(response, 'isError'):
            # Check for data
            if hasattr(response, 'registers') or hasattr(response, 'bits'):
                return True, response
        elif not response.isError():
            return True, response
            
        return False, None
    except ModbusIOException:
        return False, None
    except Exception as e:
        return False, None

def check_device(client, address):
    """Enhanced device check at given address"""
    device_found = False
    supported_functions = []
    register_data = {}
    
    # Try all combinations of functions and registers
    for function_id, start_reg, count in REGISTERS_TO_CHECK:
        success, response = execute_modbus_command(client, address, function_id, start_reg, count)
        
        if success:
            device_found = True
            func_str = modbus_function_str(function_id)
            
            if (function_id, func_str) not in supported_functions:
                supported_functions.append((function_id, func_str))
            
            # Save register data
            if hasattr(response, 'registers'):
                register_data[f"Func{function_id}_Reg{start_reg}"] = response.registers
            elif hasattr(response, 'bits'):
                register_data[f"Func{function_id}_Reg{start_reg}"] = response.bits
    
    return device_found, supported_functions, register_data

def custom_scan_strategy():
    """Returns list of addresses for scanning in optimal order"""
    # First scan known addresses
    addresses = KNOWN_ADDRESSES[:]
    
    # Then add remaining addresses, excluding already added ones
    for addr in range(START_ADDRESS, END_ADDRESS + 1):
        if addr not in addresses:
            addresses.append(addr)
    
    return addresses

def main():
    print("Enhanced Modbus Device Scanner")
    print("=" * 50)
    
    # Create client with increased timeout
    client = ModbusTcpClient(
        host=GATEWAY_IP,
        port=GATEWAY_PORT,
        timeout=TIMEOUT
    )
    
    # Connect
    connection_attempts = 0
    max_attempts = 3
    
    while connection_attempts < max_attempts:
        connection_attempts += 1
        try:
            if client.connect():
                print(f"Successfully connected to {GATEWAY_IP}:{GATEWAY_PORT}")
                break
            else:
                print(f"Attempt {connection_attempts}/{max_attempts}: Failed to connect to gateway")
                if connection_attempts < max_attempts:
                    print("Retrying in 2 seconds...")
                    time.sleep(2)
        except Exception as e:
            print(f"Connection error: {e}")
            if connection_attempts < max_attempts:
                print("Retrying in 2 seconds...")
                time.sleep(2)
    
    if connection_attempts >= max_attempts and not client.is_socket_open():
        print("Failed to connect to gateway after several attempts")
        return
    
    print("Scanning Modbus devices...")
    print("-" * 50)
    
    # Use optimized scanning strategy
    scan_addresses = custom_scan_strategy()
    print(f"Scanning {len(scan_addresses)} addresses...")
    
    found_devices = []
    
    try:
        for i, addr in enumerate(scan_addresses):
            progress = (i+1) / len(scan_addresses) * 100
            print(f"Checking address: {addr} ({progress:.1f}%)", end="\r")
            sys.stdout.flush()
            
            device_found, supported_functions, register_data = check_device(client, addr)
            
            if device_found:
                print(f"\nFound device at address {addr}")
                if supported_functions:
                    print("  Supported functions:")
                    for func_id, desc in supported_functions:
                        print(f"  - {desc}")
                
                # Display some register data if available
                if register_data:
                    print("  Register data:")
                    for key, value in list(register_data.items())[:3]:  # Limit output to first 3 registers
                        print(f"  - {key}: {value}")
                
                found_devices.append((addr, supported_functions, register_data))
                
            # Pause between requests to reduce bus load
            time.sleep(0.2)  # Increased pause between requests
        
        print("\n" + "=" * 50)
        if found_devices:
            print(f"Devices found: {len(found_devices)}")
            print(f"Addresses: {', '.join(str(addr) for addr, _, _ in found_devices)}")
            
            # Output detailed information for each device
            print("\nDetailed device information:")
            for addr, functions, reg_data in found_devices:
                print(f"Device at address {addr}:")
                if functions:
                    print("  Supported functions:")
                    for func_id, desc in functions:
                        print(f"  - {desc}")
                else:
                    print("  - Could not determine supported functions")
        else:
            print("No devices found during standard scanning.")
            print("\nTry the following actions:")
            print("1. Check physical connection of devices to the gateway (cables, power)")
            print("2. Check port settings on the WB-MGE gateway (baud rate, parity, stop bits)")
            print("3. Make sure devices are set to a supported speed (typically 9600 or 19200)")
            print("4. Test the gateway with other software (e.g., Modbus Poll or similar)")
            print("5. Temporarily disconnect or install terminators at the ends of the RS-485 line")
            
    except KeyboardInterrupt:
        print("\nScanning interrupted by user")
    except Exception as e:
        print(f"\nError during scanning: {e}")
    finally:
        client.close()
        print("Connection closed")

if __name__ == "__main__":
    main()
