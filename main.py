import network
import socket
from secrets import secrets

from time import sleep
from machine import Pin, PWM

html = """<!DOCTYPE html>
<html>
    <head> <title>Door man</title> </head>
    <body> <h1>Welcome home.</h1>
        <p>%s</p>
    </body>
</html>
"""
request_nums = {
    "POST": 7,
    "GET": 6
}
pwm = machine.PWM(Pin(1))
pwm.freq(50)

def connect_to_lan():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets["network_name"], secrets["network_password"])

    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])

def bind_to_socket():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    print('listening on', addr)

def listen_for_connections():
    while True:
        try:
            cl, addr = s.accept()
            print('client connected from', addr)
            request = cl.recv(1024)
            print(request)

            request = str(request)
            handle_request(request)

            response = html % "hi"

            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(response)
            cl.close()
        except OSError as e:
            cl.close()
            print('connection closed')
            
def handle_request(request):
    buzzer = request.find('/buzz')
    restart = request.find('/restart')

    if buzzer in [request_nums["POST"], request_nums["GET"]]:
        buzz()
    if restart == request_nums["GET"]:
        machine.restart()

def buzz():
    for position in range(6000,3300,-100):
        pwm.duty_u16(position)
        sleep(0.01)
    sleep(3)
    for position in range(3300,6000,100):
        pwm.duty_u16(position)
        sleep(0.01)

connect_to_lan()
bind_to_socket()
listen_for_connections()

