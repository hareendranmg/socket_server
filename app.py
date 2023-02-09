from web_socket_server import WebSocketServer
from utils import helpers
from datetime import datetime

def main():
    try:
        ws = WebSocketServer(helpers.get_host_ip(), 8000)
        ws.start()
    except KeyboardInterrupt:
        print(f'\n{datetime.now()}: Closing Server...')
        ws.stop()


if __name__ == '__main__':
    main()