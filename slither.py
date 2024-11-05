import paramiko


def sshConnection():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    private_key = paramiko.RSAKey.from_private_key_file("lwy.pem")

    ssh.connect(hostname="8.141.113.211", port=22, username="root", pkey=private_key)
    source_file = 'result/licencePSM.sol'
    target_folder = '/contract/licencePSM.sol'
    sftp = ssh.open_sftp()
    sftp.put(source_file, target_folder)
    sftp.close()
    # stdin, stdout, stderr = ssh.exec_command('df')  # 执行命令
    # res, err = stdout.read(), stderr.read()  # stdout.readline()
    # result = res if res else err
    # print(result.decode())

    ssh.close()
