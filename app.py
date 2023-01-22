from web_socket_server import WebSocketServer
import utils

def main():
    try:
        ws = WebSocketServer(utils.get_host_ip(), 8765)
        ws.start()
    except KeyboardInterrupt:
        print('\nClosing Server...')
        ws.stop()


if __name__ == '__main__':
    main()