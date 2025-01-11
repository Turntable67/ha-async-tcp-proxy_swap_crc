# Home Assistant AddOn Async TCP Proxy (Swap CRC)

This is a fork of the **ha-async-tcp-proxy** add-on originally developed by [cosote](https://github.com/cosote/ha-async-tcp-proxy). I want to express my gratitude to cosote for creating such a fantastic tool that provided the foundation for this project.

The original add-on was created to address Modbus communication challenges between Deye inverters and SDM630 energy meters. It worked as a reliable proxy to manage Modbus traffic between devices. However, I encountered a different challenge and made specific changes to adapt the add-on to my needs.

## Why This Fork?

When connecting a Marstek VENUS via RS485 to an Elfin EW11, I faced an issue where the response from the Marstek device had its last two bytes swapped. This caused Home Assistant's Modbus integration to reject the response. Unfortunately, the `pymodbus` library used in the integration does not provide an option to handle this byte-swap scenario.

To solve this, I used this proxy as a bridge between the Elfin EW11 and the Modbus integration in Home Assistant. This proxy intercepts the Marstek device's response and swaps the last two bytes before forwarding it to the Home Assistant Modbus integration.

## Changes in This Fork

- Added functionality to detect and modify the Marstek VENUS response, specifically swapping the last two bytes of the response.
- Retained all the original features of the async-tcp-proxy.
- Updated the debugging mechanism to log and verify the data exchange, enabling accurate byte-swapping for troubleshooting and testing.

This solution allows seamless integration of Marstek VENUS devices with Home Assistant using Modbus, overcoming the original limitation.

## Installation

You can install this add-on using the repository:

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FTurntable67%2Fha-async-tcp-proxy_swap_crc)

- Add this [Repository](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FTurntable67%2Fha-async-tcp-proxy_swap_crc) (Or click Button above)
- Install **Async TCP Proxy (Swap CRC)** from the Add-On Store.

## Configuration

- Set the `server_host` and `server_port` to the address and port of the TCP server behind the proxy (e.g., Elfin EW11).
- Configure the `client_timeout` and `server_timeout` settings as required. These settings control how the proxy handles simultaneous client connections and server response timeouts.
- Enable the **DEBUG** log level for detailed packet communication and verification of byte-swapping (this can be switched to INFO when finished testing).

### Configuration Tab
![image](https://github.com/Turntable67/ha-async-tcp-proxy_swap_crc/blob/main/2025-01-11%2010_44_59-Home%20Assistant.png)


### Example YAML Configuration for Home Assistant Modbus

```yaml
modbus:
  - name: marstek_proxy
    host: localhost
    port: 8899
    type: rtuovertcp
    retries: 0
    timeout: 1
    sensors:
      - name: venus_sensor
        unique_id: venus_sensor
        address: 10
        input_type: input
        count: 1
        data_type: uint
        precision: 2
        scan_interval: 5

## My configuration
The default async-tcp-proxy addon configuration is based on my HA setup. The PE11 TCP-Server is running on IP 192.168.177.202:8899 and connected with 38400 baud, 8 data bit, 1 stop bit and none parity to my SDM630v2. This PE11 TCP-Server is configured behind the proxy.


![image](https://github.com/Turntable67/ha-async-tcp-proxy_swap_crc/blob/main/2025-01-11%2010_44_59-Home%20Assistant)
</details>

  
### PE11 TCP-Server on SDM630v2
<details><summary>Serial Port Settings</summary>
https://github.com/Turntable67/ha-async-tcp-proxy_swap_crc/blob/main/2025-01-11%2010_44_59-Home%20Assistant.png?raw=true
![image](https://github.com/cosote/ha-async-tcp-proxy/assets/15175818/3e5cdb1c-54b2-4d18-b2db-e333286f272f)
</details>

https://github.com/Turntable67/ha-async-tcp-proxy_swap_crc/blob/main/2025-01-11%2010_44_59-Home%20Assistant.png

<details><summary>Communication Settings</summary>

![image](https://github.com/cosote/ha-async-tcp-proxy/assets/15175818/a5470e26-da0e-4321-98bc-2b6013632bbe)
</details>

### PE11 TCP-Client on Deye inverter
<details><summary>Serial Port Settings</summary>

![image](https://github.com/Turntable67/ha-async-tcp-proxy_swap_crc/blob/main/2025-01-11%2010_44_59-Home%20Assistant)
</details>

<details><summary>Communication Settings</summary>

![image](https://github.com/cosote/ha-async-tcp-proxy/assets/15175818/ab36dbd6-f4f3-4ce7-ac0e-41172653a2de)
</details>
