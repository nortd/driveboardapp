import websocket
ws = websocket.WebSocket()
ws.connect("ws://localhost:4411")
ws.send('{"cmd_air_enable":1}')
ws.recv()
ws.close()