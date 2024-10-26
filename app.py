from flask import *
from flask import Flask, jsonify
from flask_cors import *
import modelConvert
from codeGeneration import outputCode
from modelConvert import writeFile, parsePUML, convert
import codeGeneration

app = Flask(__name__)  # 初始化app
CORS(app, resources=r'/*')


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


@app.route('/generateCode', methods=['POST'])
@cross_origin()
def generate():
    content = request.json.get('pimCode')
    Note = open('tmp_cim\cim.puml', mode='a')
    Note.seek(0)
    Note.truncate()
    Note.write(content)
    Note.close()
    # 解析CIM
    parsePUML()
    convert()
    outputCode()
    with open('code_result/licencePSM.sol', 'r', encoding='utf-8') as file:
        result = file.read()
        return result


@app.route('/getInfo', methods=['GET'])
@cross_origin()
def getInfo():
    contractInfo = codeGeneration.getContractName()
    contractData = codeGeneration.getContractData()
    contractRes = codeGeneration.getRestrictionInfo()
    contractPattern = codeGeneration.getProcessInfo()
    data = {
        'contractInfo': [{
            'contractKey': '合约名',
            'contractValue': contractInfo.get('name')
        }, {
            'contractKey': '合约描述',
            'contractValue': contractInfo.get('desc')
        }, {
            'contractKey': '合约参与方',
            'contractValue': contractInfo.get('party').strip('[').strip(']')
        }],
        'dataInfo': contractData,
        'restrictionInfo': contractRes,
        'patternInfo': contractPattern
    }
    json_data = json.dumps(data)
    return json_data


@app.route('/getDataDetail', methods=['GET'])
@cross_origin()
def getDataDetail():
    name = request.values.get('dataName')
    detail = codeGeneration.getDataDetailInfo(name)
    data = {
        'dataDetail': detail
    }
    json_data = json.dumps(data)
    return json_data


@app.route('/getResDetail', methods=['GET'])
@cross_origin()
def getResDetail():
    name = request.values.get('resName')
    detail = codeGeneration.getResDetailInfo(name)
    data = {
        'resDetail': detail
    }
    json_data = json.dumps(data)
    return json_data


@app.route('/getPatternDetail', methods=['GET'])
@cross_origin()
def getPatternDetail():
    name = request.values.get('patternName')
    patternInfo = codeGeneration.getProcessDetailInfo(name)
    functionInfo = []
    pattern = codeGeneration.selectProcessByName(name)
    functions = pattern[0][2].strip('[').strip(']').split(',')
    for f in functions:
        cur = codeGeneration.getFunctionDetailInfo(f)
        functionInfo.append(cur)
    data = {
        'processDetail': patternInfo,
        'functionDetail': functionInfo
    }
    json_data = json.dumps(data)
    return json_data


if __name__ == '__main__':
    modelConvert.truncateCimDB()
    modelConvert.truncatePimDB()
    app.run(host='127.0.0.1', port=9014,)  # 运行app
