#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Улучшенный скрипт для сканирования шины RS-485 через Modbus TCP шлюз
с расширенными возможностями обнаружения устройств
"""

import sys
import time
import pymodbus
from pymodbus.exceptions import ModbusIOException

print(f"Версия pymodbus: {pymodbus.__version__}")
major_version = int(pymodbus.__version__.split('.')[0])

if major_version >= 3:
    from pymodbus.client import ModbusTcpClient
    print("Используем импорты для pymodbus 3.x")
else:
    from pymodbus.client.sync import ModbusTcpClient
    print("Используем импорты для pymodbus 2.x")

# Настройки подключения
GATEWAY_IP = "192.168.1.58"
GATEWAY_PORT = 502
TIMEOUT = 2  # Увеличиваем таймаут для медленных устройств

# Диапазон сканирования
START_ADDRESS = 1
END_ADDRESS = 247  # Полный диапазон Modbus адресов

# Увеличиваем набор проверяемых регистров
REGISTERS_TO_CHECK = [
    # Функция 3 - Holding Registers
    (3, 0, 1),    # Стандартный первый регистр
    (3, 1, 1),    # Второй регистр
    (3, 4, 1),    # Регистр, часто используемый в устройствах
    (3, 100, 1),  # Регистр, часто используемый для конфигурации
    (3, 1000, 1), # Другой часто используемый начальный регистр
    
    # Функция 4 - Input Registers
    (4, 0, 1),
    (4, 1, 1),
    (4, 30, 1),   # Регистр, часто используемый для показаний
    
    # Функция 1 - Coils (дискретные выходы)
    (1, 0, 1),
    (1, 10, 1),
    
    # Функция 2 - Discrete Inputs (дискретные входы)
    (2, 0, 1),
    (2, 10, 1)
]

# Известные адреса Modbus для проверки (добавьте сюда адреса ваших устройств, если они известны)
KNOWN_ADDRESSES = [16, 1, 2, 3, 8, 10, 20, 32, 64, 100, 127, 200, 240]

def modbus_function_str(function_id):
    """Преобразует номер функции в читаемое описание"""
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
    """Выполняет команду Modbus с учетом версии библиотеки"""
    try:
        if major_version >= 3:
            # Параметры для pymodbus 3.x
            slave_param = {"slave_address": address}
        else:
            # Параметры для pymodbus 2.x
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

        # Проверяем ответ
        if not hasattr(response, 'isError'):
            # Проверяем наличие данных
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
    """Расширенная проверка устройства на заданном адресе"""
    device_found = False
    supported_functions = []
    register_data = {}
    
    # Проходим по всем комбинациям функций и регистров
    for function_id, start_reg, count in REGISTERS_TO_CHECK:
        success, response = execute_modbus_command(client, address, function_id, start_reg, count)
        
        if success:
            device_found = True
            func_str = modbus_function_str(function_id)
            
            if (function_id, func_str) not in supported_functions:
                supported_functions.append((function_id, func_str))
            
            # Сохраняем данные из регистра
            if hasattr(response, 'registers'):
                register_data[f"Func{function_id}_Reg{start_reg}"] = response.registers
            elif hasattr(response, 'bits'):
                register_data[f"Func{function_id}_Reg{start_reg}"] = response.bits
    
    return device_found, supported_functions, register_data

def custom_scan_strategy():
    """Возвращает список адресов для сканирования в оптимальном порядке"""
    # Сначала сканируем известные адреса
    addresses = KNOWN_ADDRESSES[:]
    
    # Затем добавляем остальные адреса диапазона, исключая уже добавленные
    for addr in range(START_ADDRESS, END_ADDRESS + 1):
        if addr not in addresses:
            addresses.append(addr)
    
    return addresses

def main():
    print("Улучшенный сканер Modbus устройств")
    print("=" * 50)
    
    # Создаем клиент с увеличенным таймаутом
    client = ModbusTcpClient(
        host=GATEWAY_IP,
        port=GATEWAY_PORT,
        timeout=TIMEOUT
    )
    
    # Подключаемся
    connection_attempts = 0
    max_attempts = 3
    
    while connection_attempts < max_attempts:
        connection_attempts += 1
        try:
            if client.connect():
                print(f"Успешное подключение к {GATEWAY_IP}:{GATEWAY_PORT}")
                break
            else:
                print(f"Попытка {connection_attempts}/{max_attempts}: Не удалось подключиться к шлюзу")
                if connection_attempts < max_attempts:
                    print("Повторная попытка через 2 секунды...")
                    time.sleep(2)
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            if connection_attempts < max_attempts:
                print("Повторная попытка через 2 секунды...")
                time.sleep(2)
    
    if connection_attempts >= max_attempts and not client.is_socket_open():
        print("Не удалось подключиться к шлюзу после нескольких попыток")
        return
    
    print("Сканирование Modbus устройств...")
    print("-" * 50)
    
    # Используем оптимизированную стратегию сканирования
    scan_addresses = custom_scan_strategy()
    print(f"Сканирование {len(scan_addresses)} адресов...")
    
    found_devices = []
    
    try:
        for i, addr in enumerate(scan_addresses):
            progress = (i+1) / len(scan_addresses) * 100
            print(f"Проверка адреса: {addr} ({progress:.1f}%)", end="\r")
            sys.stdout.flush()
            
            device_found, supported_functions, register_data = check_device(client, addr)
            
            if device_found:
                print(f"\nНайдено устройство на адресе {addr}")
                if supported_functions:
                    print("  Поддерживаемые функции:")
                    for func_id, desc in supported_functions:
                        print(f"  - {desc}")
                
                # Выводим некоторые данные из регистров, если они есть
                if register_data:
                    print("  Данные из регистров:")
                    for key, value in list(register_data.items())[:3]:  # Ограничиваем вывод первыми 3 регистрами
                        print(f"  - {key}: {value}")
                
                found_devices.append((addr, supported_functions, register_data))
                
            # Пауза между запросами для снижения нагрузки на шину
            time.sleep(0.2)  # Увеличена пауза между запросами
        
        print("\n" + "=" * 50)
        if found_devices:
            print(f"Найдено устройств: {len(found_devices)}")
            print(f"Адреса: {', '.join(str(addr) for addr, _, _ in found_devices)}")
            
            # Вывод детальной информации по каждому устройству
            print("\nДетальная информация об устройствах:")
            for addr, functions, reg_data in found_devices:
                print(f"Устройство на адресе {addr}:")
                if functions:
                    print("  Поддерживаемые функции:")
                    for func_id, desc in functions:
                        print(f"  - {desc}")
                else:
                    print("  - Не удалось определить поддерживаемые функции")
        else:
            print("Устройства не найдены при стандартном сканировании.")
            print("\nПопробуйте следующие действия:")
            print("1. Проверьте физическое подключение устройств к шлюзу (кабели, питание)")
            print("2. Проверьте настройки порта на шлюзе WB-MGE (скорость, четность, стоп-биты)")
            print("3. Убедитесь, что устройства настроены на поддерживаемую скорость (обычно 9600 или 19200)")
            print("4. Проверьте шлюз с помощью другого ПО (например, Modbus Poll или аналогичного)")
            print("5. Временно отключите или установите терминаторы на концах линии RS-485")
            
    except KeyboardInterrupt:
        print("\nСканирование прервано пользователем")
    except Exception as e:
        print(f"\nОшибка во время сканирования: {e}")
    finally:
        client.close()
        print("Соединение закрыто")

if __name__ == "__main__":
    main()
