from flask import *
from flask import Flask

from modelConvert import writeFile, parsePUML, convert

app = Flask(__name__)  # 初始化app


@app.route('/')  # 建立路由
def hello():
    return 'hello world'  # 定义路由执行结果


@app.route('/modelShow', methods=['POST'])
def modelShow():
    comment = request.json.get('cimCode')
    writeFile(comment)
    return 'OK'


@app.route('/convert')
def convertModel():
    content = request.values.get('cimCode')
    Note = open('tmp_cim\cim.puml', mode='a')
    Note.seek(0)
    Note.truncate()
    Note.write(content)
    Note.close()
    # 解析CIM
    parsePUML()
    # 转换PIM
    result = convert()
    return result


if __name__ == '__main__':
    app.run()  # 运行app
