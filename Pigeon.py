# -*- coding:utf-8 -*-

import socket
import platform
import logging
import threading
import time

print """
Welcome to Pigeon!
Commands:
connnect - connect to certain host.
exit - quit chat or Pigeon.
"""
print 'Your ID:' + socket.gethostname()

# identify default charset
sys = platform.system()
if sys == 'Windows':
    charset = 'GBK'
else:
    charset = 'utf-8'
print 'System:' + sys, 'Charset:' + charset

global connected
connected = False  # False: wait, True: connected


class Server(threading.Thread):
    def __init__(self, charset):
        threading.Thread.__init__(self)
        self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 6666
        self.charset = charset
        self.Socket.bind((self.host, self.port))
        self.Socket.listen(5)

    def run(self):
        global connected

        while True:
            print 'Listening on ' + self.host + ':' + str(self.port)

            connection, address = self.Socket.accept()
            print 'Peer ' + address[0] + ' connected!'
            connected = True

            logger_remote_user = logging.getLogger(address[0])
            logger_remote_user.setLevel(logging.INFO)

            datefmt = '%Y-%m-%d %H:%M:%S'

            record_handler = logging.FileHandler('./record.log')
            record_handler.setLevel(logging.INFO)
            recv_handler = logging.StreamHandler()
            recv_handler.setLevel(logging.INFO)

            formatter_user = logging.Formatter('%(asctime)s - %(name)s : %(message)s', datefmt=datefmt)

            recv_handler.setFormatter(formatter_user)
            record_handler.setFormatter(formatter_user)

            logger_remote_user.addHandler(recv_handler)
            logger_remote_user.addHandler(record_handler)

            while True:
                msg_recv = connection.recv(1024)
                if len(msg_recv) > 0:
                    logger_remote_user.info(msg_recv.decode('utf-8').encode(self.charset))
                else:
                    logger_remote_user.info('Peer offline')
                    connection.close()
                    connected = False
                    break


class Client(threading.Thread):

    def __init__(self, charset):
        threading.Thread.__init__(self)
        self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = 6666
        self.charset = charset

    def stop(self):
        self._stop.set()

    def run(self):
        global connected

        # create loggers
        logger_client = logging.getLogger('client')
        logger_client.setLevel(logging.INFO)

        logger_local_user = logging.getLogger(socket.gethostname())
        logger_local_user.setLevel(logging.INFO)

        # create handlers
        client_handler = logging.StreamHandler()
        client_handler.setLevel(logging.INFO)
        recv_handler = logging.StreamHandler()
        recv_handler.setLevel(logging.INFO)
        record_handler = logging.FileHandler('./record.log')
        record_handler.setLevel(logging.INFO)

        # create formatters
        datefmt = '%Y-%m-%d %H:%M:%S'
        formatter_client = logging.Formatter('%(asctime)s - %(message)s', datefmt=datefmt)
        formatter_user = logging.Formatter('%(asctime)s - %(name)s : %(message)s', datefmt=datefmt)

        # add formatters
        client_handler.setFormatter(formatter_client)
        recv_handler.setFormatter(formatter_user)
        record_handler.setFormatter(formatter_user)

        # add handlers to logger
        logger_client.addHandler(client_handler)
        logger_client.addHandler(record_handler)
        logger_local_user.addHandler(recv_handler)
        logger_local_user.addHandler(record_handler)

        # send messages
        while True:
            cmd = raw_input('Command:')
            if cmd == 'connect':
                # set host
                self.host = raw_input('host ip:')
                if len(self.host) == 0:
                    self.host = '192.168.3.53'

                #  connect
                print 'Connecting...'
                while not connected:
                    print 2
                    try:
                        self.Socket.connect((self.host, self.port))
                        print 1
                        connected = True
                    except:
                        pass
                    time.sleep(1)

                logger_client.info('Connected to host ' + self.host)
                while connected:
                    msg_send = raw_input()
                    if msg_send == 'exit':
                        print 'Quit chat.'
                        self.connected = False
                        self.Socket.close()
                        break
                    else:
                        logger_local_user.info(msg_send)
                        self.Socket.send(msg_send.decode(charset).encode('utf-8'))

            elif cmd == 'exit':
                logger_client.info('Bye!')
                break
            else:
                logger_client.info('Unknown command')


if __name__ == '__main__':
    server = Server(charset)
    server.daemon = True
    server.start()
    # start client
    client = Client(charset)
    client.start()
