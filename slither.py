import paramiko
import codeGeneration


def sshUploadFile():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    private_key = paramiko.RSAKey.from_private_key_file("lwy.pem")
    ssh.connect(hostname="8.141.113.211", port=22, username="root", pkey=private_key)
    source_file = 'code_result/licencePSM.sol'
    target_folder = '/contract/test.sol'
    sftp = ssh.open_sftp()
    sftp.put(source_file, target_folder)
    ssh.exec_command('slither /contract/test.sol --print cfg')
    filename = 'C:\\Users\\24476\\Desktop\project-mda\\vue-smart-contract-editor\src\ssh\\test.png'
    sftp.get("/contract/test.png", filename)
    filename = 'C:\\Users\\24476\\Desktop\project-mda\\vue-smart-contract-editor\src\ssh\\test2.png'
    sftp.get("/contract/test2.png", filename)
    filename = 'C:\\Users\\24476\\Desktop\project-mda\\vue-smart-contract-editor\src\ssh\\test3.png'
    sftp.get("/contract/test3.png", filename)
    filename = 'C:\\Users\\24476\\Desktop\project-mda\\vue-smart-contract-editor\src\ssh\\test4.png'
    sftp.get("/contract/test4.png", filename)
    # stdin, stdout, stderr = ssh.exec_command('df')  # 执行命令
    # res, err = stdout.read(), stderr.read()  # stdout.readline()
    # result = res if res else err
    # print(result.decode())
    sftp.close()
    ssh.close()


