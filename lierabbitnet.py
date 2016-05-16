#!/usr/bin/python3.5
"""
version : 1.0
by      : LieRabbit
qq      : 1053963770
time    : 2016-5-16  19:10
"""

import sys
import socket
import getopt
import threading
import subprocess
import os
import platform


# 定义一些全局变量
listen = False
command = False
upload = False
target = ''
upload_destination = ''
port = 0
firstSend = True
filename = -1


def usage():
    print('LieRabbit Net Tool')
    print()
    print('Usage: lierabbitnet.py -t target_host -p port')
    print('-l --listen              - listen on [host]:[post] for incoming connections')
    print('-c --command             - initialize a command shell')
    print('-u --upload=destination  - upon receiving connection upload a file and write to')
    print('                           [destination]')
    print('-f --file=filename       - upload a file')
    print()
    print()
    print('Examples: ')
    print('./lierabbitnet.py -p 5555 -l -c')
    print('python3 lierabbitnet.py -p 5555 -l -c')
    print('./lierabbitnet.py -t 192.168.0.1 -p 5555')
    print('./lierabbitnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe')
    sys.exit(0)


def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # 连接到目标主机
        client.connect((target, port))
        if len(buffer):
            client.send(buffer)

        while 1:
            # 现在等待数据回传
            recv_len = 1
            response = ''

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data.decode()

                if recv_len < 4096:
                    break

            print(response, end=' ')

            # 等待更多的输入
            buffer = input().encode()
            buffer += b'\n'

            # 发送出去
            client.send(buffer)
    except Exception as e:
        print(e)
        print('[*] Exception! Exiting.')
        # 关闭连接并且退出
        client.close()
        sys.exit(0)


def server_loop():
    global target
    global firstSend

    # 如果没有定义目标，那么监听所有接口
    if not len(target):
        target = '0.0.0.0'

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    while 1:
        client_socket, addr = server.accept()
        firstSend = True
        print('连接成功')

        # 分拆一个线程处理新的客户端
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


def run_command(command):
    # 去掉换行
    command = command.rstrip()
    if command.startswith('cd '):
        os.chdir(command[3:])
        return b'change path\n'

    # 运行命令并将输出返回
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        if platform.system() == 'Windows':
            output = output.decode('gbk').encode()
    except Exception:
        output = b'Failed to execute command.\r\n'

    # 将输出发送
    return output


def client_handler(client_socket):
    global upload
    global command
    global firstSend

    # 检测上传文件
    if len(upload_destination):
        # 读取所有的字符并写下目标
        file_buffer = b''
        # 持续读取数据直到没有符合的数据

        while 1:
            data = client_socket.recv(1024)
            data_len = len(data)
            file_buffer += data
            if data_len < 1024:
                break
        # 现在接收这些数据并将他们写出来
        try:
            file_descriptor = open(upload_destination, 'wb')
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            if firstSend:
                client_socket.send(b'Successfully saved file to %s \r\n<LieRabbit:#>' % upload_destination.encode())
                firstSend = False
            else:
                # 确认文件已经写出来
                client_socket.send(b'Successfully saved file to %s \r\n' % upload_destination.encode())
        except Exception:
            if firstSend:
                firstSend = False
                client_socket.send(b'Failed to save file to %s \r\n<LieRabbit:#>' % upload_destination.encode())
            else:
                client_socket.send(b'Failed to save file to %s \r\n' % upload_destination.encode())

    if command:
        if firstSend:
            firstSend = False
            # 发送名字
            client_socket.send(b'<LieRabbit:#>')
        while 1:

            # 现在接收文件直到发现换行符(enter key)
            cmd_buffer = ''
            while '\n' not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024).decode()

            # 返回命令输出
            response = run_command(cmd_buffer)
            response += b'<LieRabbit:#>'
            # 返回响应数据
            client_socket.send(response)


def main():
    global listen
    global port
    global command
    global upload_destination
    global target
    global filename

    if not len(sys.argv[1:]):
        usage()

    # 读取命令行选项
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hlt:p:cu:f:', ['help', 'listen', 'target=', 'port=', 'command', 'upload=', 'file='])
    except getopt.GetoptError as err:
        print(err)
        usage()

    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
        elif o in ('-l', '--listen'):
            listen = True
        elif o in ('-c', '--command'):
            command = True
        elif o in ('-u', '--upload'):
            upload_destination = a
        elif o in ('-t', '--target'):
            target = a
        elif o in ('-p', '--port'):
            port = int(a)
        elif o in ('-f', '--file'):
            filename = a
        else:
            assert False, 'Unhandled Option'

    # 进行监听还是仅从标准输入发送数据
    if not listen and len(target) and port > 0:
        buffer = b''
        if not (filename == -1):
            buffer = open(filename, 'rb')
            client_sender(buffer.read())
        # 发送数据
        client_sender(buffer)

    # 开始监听并准备上传文件、执行命令
    # 放置一个反弹shell
    # 取决于上面的命令选项
    if listen:
        print('进入服务')
        server_loop()

if __name__ == '__main__':
    main()
