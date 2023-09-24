import socket
import network
import _thread
import machine
import time
import esp
esp.osdebug(None)
import gc
gc.collect()

led1 = machine.Pin(17, machine.Pin.OUT)
led2 = machine.Pin(16, machine.Pin.OUT)

resposta_nok = """<!DOCTYPE HTML><html><head><title>ESP32 TECTI</title></head>\r\n
<body><h1>Página Invalida</h1></body>\r\n'</html>"""

resposta_ok = """<!DOCTYPE HTML><html><head><title>ESP32 TECTI</title></head>\r\n
<body><h1>LED %(led)s %(estado)s</h1></body>\r\n'</html>"""

def sendHTTP(msg, type='html'):
    resp = ('HTTP/1.1 200 OK\r\n'
            'Content-Type: text/' + type + '\r\n'
            'Connection: close\r\n'
            '\r\n' + msg + '\r\n\r\n')
    return resp

wlan = network.WLAN(network.STA_IF)  # cria a interface Wifi
wlan.active(True)  # ativa a interface
wlan.connect('PUC-ACD', '')  # conecta-se a ela

while not wlan.isconnected():
    print(".", end="")
    time.sleep(0.1)

print('Connection successful')
print(wlan.ifconfig())
print('------')

def on_new_client(con, addr):
    while True:
        msg = con.recv(1024)
        if msg:
            print(str(addr) + ' >>\r\n' + msg.decode())
            break

    dados = msg.decode()
    header = dados.split('\r\n')
    getHeader = header[0].split(' ')

    if getHeader[1] == "/17/on":
        led1.value(1)
        msg = sendHTTP(resposta_ok % {'led': '17', 'estado': 'on'}).encode()
        
    elif getHeader[1] == "/17/off":
        led1.value(0)
        msg = sendHTTP(resposta_ok % {'led': '17', 'estado': 'off'}).encode()
        
    elif getHeader[1] == "/16/on":    
        led2.value(1)
        msg = sendHTTP(resposta_ok % {'led': '16', 'estado': 'on'}).encode()
        
    elif getHeader[1] == "/16/off":
        led2.value(0)
        msg = sendHTTP(resposta_ok % {'led': '16', 'estado': 'off'}).encode()
    else:
        msg = sendHTTP(resposta_nok).encode()

    con.send(msg)
    con.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

try:
    while True:
        conn, addr = s.accept()
        print('Got a connection from %s' % str(addr))
        _thread.start_new_thread(on_new_client, (conn, addr))
except:
    print('Saindo')
    s.close()
