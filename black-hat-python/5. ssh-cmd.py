# 使用paramiko连接到一台有ssh的机器, 在上面执行命令
# 利用paramiko编写ssh服务器和客户端, 用它们在windows系统上远程执行命令
# 如何用paramiko自带的反向隧道示例程序实现与BHNET工具的代理功能相同的效果

import paramiko

def ssh_command(ip, port, user, passwd, cmd):
    # 向SSH服务器发起连接并执行一条命令
    client = paramiko.SSHClient()
    # paramiko支持用密钥认证替代密码认证
    # 当服务器发来一个没有记录的公钥时, 设定的策略是自动信任并记住该公钥
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    client.connect(ip, port=port, username=user, password=passwd)

    # 服务器执行命令
    _, stdout, stderr = client.exec_command(cmd)
    output = stdout.readlines() + stderr.readlines()
    if output:
        print('---Output---')
        for line in output:
            print(line.strip())

if __name__ == '__main__':
    import getpass
    # 获取当前设备上登录用户的用户名
    # user = getpass.getuser()
    # 由于服务器和当前设备上的用户名不同, 所以此处明确要求用户输入用户名
    user = input('Username: ')
    # getpass使得用户敲击的密码字符不会出现在屏幕上
    pasword = getpass.getpass()
    ip = input('Enter server IP: ') or '192.168.15.128'
    port = input('Enter port or <CR>: ') or 2222
    cmd = input('Enter command or <CR>: ') or 'id'
    ssh_command(ip, port, user, pasword, cmd)