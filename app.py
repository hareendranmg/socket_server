from web_socket_server import WebSocketServer
from utils import helpers

def main():
    try:
        ws = WebSocketServer(helpers.get_host_ip(), 8765)
        ws.start()
    except KeyboardInterrupt:
        print('\nClosing Server...')
        ws.stop()


if __name__ == '__main__':
    main()