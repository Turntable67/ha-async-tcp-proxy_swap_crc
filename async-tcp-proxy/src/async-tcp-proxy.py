#
# This file is part of the ha-async-tcp-proxy project
#
# Copyright (c) 2023 Jens Bornemann
#
# Distributed under the Apache 2.0. See LICENSE for more info.
#

import argparse
import asyncio
import logging

# Default timeout waiting for client to request data from remote server
MAX_CLIENT_TIMEOUT = 60

# Default communication buffer size of 4kb
BUFFER_SIZE = 2 ** 12

# Create a lock to synchronize access to the remote server
remote_server_lock = asyncio.Lock()

# Create a global variable to store the remote server connection
remote_server_connection = None

async def get_remote_server_connection(log):
    global remote_server_connection
    if not remote_server_connection:
        try:
            remote_reader, remote_writer = await asyncio.open_connection(args.server_host, args.server_port)
            remote_server_connection = (remote_reader, remote_writer)
        except (ConnectionError, asyncio.TimeoutError) as e:
            log.error(f'Error connecting to remote server: {e}')
            return
    return remote_server_connection

def close_remote_server_connection(log, reason):
    global remote_server_connection
    log.warning(f'Closing remote server connection, reason: {reason}')
    reader, writer = remote_server_connection
    remote_server_connection = None
    writer.close()
    return reader, writer

# Source: https://github.com/ickerwx/tcpproxy/blob/master/proxymodules/hexdump.py
def hex_dump(data, length=16):
        result = []
        digits = 2
        for i in range(0, len(data), length):
            s = data[i:i + length]
            hexa = ' '.join(['%0*X' % (digits, x) for x in s])
            text = ''.join([chr(x) if 0x20 <= x < 0x7F else '.' for x in s])
            result.append("%04X   %-*s   %s" % (i, length * (digits + 1), hexa, text))
        return "\n".join(result)

async def handle_client(reader, writer):
    try:
        MAX_TIMEOUTS = 5
        timeout_count = 0
        return_reason = 'unknown'

        client_address = writer.get_extra_info('peername')
        log = logging.getLogger(f'{client_address[0]}:{client_address[1]}')
        log.info(f'New client connection')

        async with remote_server_lock:
            remote_reader, remote_writer = await get_remote_server_connection(log)

        while True:
            client_in_session = False
            try:
                data = await asyncio.wait_for(reader.read(BUFFER_SIZE), timeout=MAX_CLIENT_TIMEOUT)
                if data:
                    if log.isEnabledFor(logging.DEBUG):
                        log.debug(f'Received {len(data)} bytes from client (new session):\n{hex_dump(data)}')
                else:
                    return_reason = f'No data received from client (new session)'
                    log.debug(return_reason)
                    return
            except asyncio.TimeoutError:
                log.debug(f'Timeout receiving from client (new session)')
                continue
            except ConnectionError as e:
                return_reason = f'Error reading from client: {e}'
                log.error(return_reason)
                return

            async with remote_server_lock:
                client_in_session = True
                try:
                    _, remote_writer = await get_remote_server_connection(log)
                    remote_writer.write(data)
                    log.debug(f'Sent {len(data)} bytes to remote server')
                except ConnectionError as e:
                    return_reason = f'Connection error writing to remote server: {e}'
                    log.error(return_reason)
                    close_remote_server_connection(log, e)
                    return
                except Exception as e:
                    return_reason = f'Error writing to remote server: {e}'
                    log.error(return_reason)
                    close_remote_server_connection(log, e)
                    return

                try:
                    remote_reader, _ = await get_remote_server_connection(log)
                    response = await asyncio.wait_for(remote_reader.read(BUFFER_SIZE), timeout=args.server_timeout)
                    if not response:
                        break
                    timeout_count = 0

                    # Swap the last two bytes in the response
                    if len(response) >= 2:
                        swapped_response = response[:-2] + response[-1:] + response[-2:-1]
                        response = swapped_response
                        log.debug(f'Swapped last two bytes in response:\n{hex_dump(response)}')

                    if log.isEnabledFor(logging.DEBUG):
                        log.debug(f'Received {len(response)} bytes from remote server:\n{hex_dump(response)}')
                except asyncio.TimeoutError:
                    if log.isEnabledFor(logging.DEBUG):
                        log.debug(f'No response from remote server for client request:\n{hex_dump(data)}')
                    timeout_count += 1
                    if timeout_count >= MAX_TIMEOUTS:
                        return_reason = f'For {timeout_count} times no data received from remote server'
                        close_remote_server_connection(log, return_reason)
                        return
                    break
                except ConnectionError as e:
                    return_reason = f'Connection error reading from remote server: {e}'
                    log.error(return_reason)
                    close_remote_server_connection(log, e)
                    return
                except Exception as e:
                    return_reason = f'Error reading from remote server: {e}'
                    log.error(return_reason)
                    close_remote_server_connection(log, e)
                    return

                try:
                    writer.write(response)
                    log.debug(f'Sent {len(response)} bytes to client')
                except ConnectionError as e:
                    return_reason = f'Connection error writing to client: {e}'
                    return
                except Exception as e:
                    return_reason = f'Error writing to client: {e}'
                    return
    finally:
        log.info(f'Closing client connection, reason: {return_reason}')
        writer.close()

async def main():
    parser = argparse.ArgumentParser(description='TCP proxy server')
    parser.add_argument('--port', type=int, default=8899, help='proxy server port')
    parser.add_argument('--server-host', type=str, default='192.168.177.202', help='server host')
    parser.add_argument('--server-port', type=int, default=8899, help='server port')
    parser.add_argument('--server-timeout', type=float, default=0.15, help='timeout for server response')
    parser.add_argument('--client-timeout', type=float, default=0.15, help='timeout for additional client requests')
    parser.add_argument('--loglevel', type=str, default='INFO', help='log level: NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL')

    global args
    args = parser.parse_args()

    # Initialize logging
    logging.basicConfig(level=args.loglevel.upper(), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Start proxy server
    try:
        server = await asyncio.start_server(handle_client, '0.0.0.0', args.port)
        async with server:
            logging.info(f'TCP proxy server started on port {args.port}')
            await server.serve_forever()
    except Exception as e:
        logging.critical(f'Critical error: {e}')

asyncio.run(main())
