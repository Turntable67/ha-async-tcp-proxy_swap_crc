# Home Assistant AddOn Async TCP Proxy (Swap CRC)

This is a fork of the **ha-async-tcp-proxy** add-on originally developed by [cosote](https://github.com/cosote/ha-async-tcp-proxy). I want to express my gratitude to cosote for creating such a fantastic tool that provided the foundation for this project.

The original add-on was created to address Modbus communication challenges between Deye inverters and SDM630 energy meters. It worked as a reliable proxy to manage Modbus traffic between devices. However, I encountered a different challenge and made specific changes to adapt the add-on to my needs.

## Why This Fork?

When connecting a Marstek VENUS via RS485 to an Elfin EW11, I faced an issue **where the response from the Marstek device had its last two bytes swapped**. This caused Home Assistant's Modbus integration to reject the response. Unfortunately, the `pymodbus` library used in the integration does not provide an option to handle this byte-swap scenario.

To solve this, I used this proxy as a bridge between the Elfin EW11 and the Modbus integration in Home Assistant. This proxy intercepts the Marstek device's response and swaps the last two bytes before forwarding it to the Home Assistant Modbus integration.

## Changes in This Fork

- Added functionality to detect and modify the Marstek VENUS response, specifically swapping the last two bytes of the response.
- Retained all the original features of the async-tcp-proxy.
- Updated the debugging mechanism to log and verify the data exchange, enabling accurate byte-swapping for troubleshooting and testing.

This solution allows seamless integration of Marstek VENUS devices with Home Assistant using Modbus, overcoming the original limitation.

When the issue with the swapped CRC is fixed by Marstek or when the pymodbud is able to invert the CRC bytes from the response (the request does not need the swap), this forked ha-async-tcp-proxy_swap_crc will no longer be nessecary.

## Installation

You can install this add-on using the repository:

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FTurntable67%2Fha-async-tcp-proxy_swap_crc)

- Add this [Repository](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FTurntable67%2Fha-async-tcp-proxy_swap_crc) (Or click Button above)
- Install **Async TCP Proxy (Swap CRC)** from the Add-On Store.

## Configuration add on 

- Set the `server_host` and `server_port` to the address and port of the TCP server behind the proxy (e.g., Elfin EW11).
- Configure the `client_timeout` and `server_timeout` settings as required. These settings control how the proxy handles simultaneous client connections and server response timeouts.
- Enable the **DEBUG** log level for detailed packet communication and verification of byte-swapping (this can be switched to INFO when finished testing).

### Configuration Tab
![image](https://github.com/Turntable67/ha-async-tcp-proxy_swap_crc/blob/main/2025-01-11%2010_44_59-Home%20Assistant.png)


### Configuration Modbus
Follow instruction on .....

### Example YAML Configuration for Home Assistant Modbus
Modbus is now connecting to the ha-async-tcp-proxy_swap_crc and no longer to the Elfin EW11 for modbus is this now on the localhost (Home Assistant)
### At least one sensor is needed to make a connection

```yaml
modbus:
  - name: modbus_hub
    type: rtuovertcp
    port: 8899
    delay: 1
    message_wait_milliseconds: 50
    timeout: 5

    sensors:
      - name: "Battery Voltage"
        unique_id: battery_voltage
        address: 32100
        slave: 1
        scan_interval: 1
        input_type: holding
        data_type: uint16
        swap: byte
        unit_of_measurement: V
        device_class: voltage
        state_class: measurement
        scale: 0.01
        offset: 0
        precision: 1
