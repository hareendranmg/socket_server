from web_socket_server import WebSocketServer
import utils


try:
    ws = WebSocketServer(utils.get_host_ip(), 8765)
    ws.start()
except KeyboardInterrupt:
    print('\nClosing Server...')
    ws.stop()
