from flask import *
from flask import Flask

from modelConvert import writeFile

app = Flask(__name__)  # 初始化app


@app.route('/')  # 建立路由
def hello():
    return 'hello world'  # 定义路由执行结果


@app.route('/modelShow', methods=['POST'])
def modelShow():
    comment = request.json.get('cimCode')
    writeFile(comment)
    return ''


@app.route('/convert')
def convertModel():
    return 'convert'


if __name__ == '__main__':
    app.run()  # 运行app
