from flask import *
from flask import Flask, jsonify
from flask_cors import *
import modelConvert
from codeGeneration import outputCode
from modelConvert import writeFile, parsePUML, convert
import codeGeneration
import reusableLibManage
import slither

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


@app.route('/getContractInLib', methods=['GET'])
@cross_origin()
def getAllContract():
    contractInfo = reusableLibManage.getAllContract()
    res = []
    for c in contractInfo:
        cur = {
            'number': c[0],
            'contractName': c[1],
            'contractDesc': c[2]
        }
        res.append(cur)
    return res


@app.route('/getContractCode', methods=['GET'])
@cross_origin()
def getContractCode():
    contractId = request.values.get('id')
    code = reusableLibManage.getContractCode(contractId)
    return code


@app.route('/update/contract', methods=['GET'])
@cross_origin()
def updateContract():
    contractId = request.values.get('id')
    contractName = request.values.get('name')
    contractDesc = request.values.get('desc')
    contractCode = request.values.get('code')
    reusableLibManage.updateContract(contractId, contractName, contractDesc, contractCode)
    return 'Successful Update!'


@app.route('/addContract', methods=['GET'])
@cross_origin()
def addContract():
    contractName = request.values.get('name')
    contractDesc = request.values.get('desc')
    contractCode = request.values.get('code')
    reusableLibManage.addContract(contractName, contractDesc, contractCode)
    return 'Successful Add!'


@app.route('/getPatternInLib', methods=['GET'])
@cross_origin()
def getPatternInfo():
    patternInfo = reusableLibManage.getAllPattern()
    pattern = []
    domain = []
    functions = []
    for r in patternInfo:
        cur = {
            'number': r[0],
            'patternName': r[1],
            'patternClass': r[2],
            'patternDesc': r[3],
            'allFunctions': r[4]
        }
        pattern.append(cur)
    allClasses = reusableLibManage.getAllClass()
    for c in allClasses:
        cur = {
            'value': c[0],
            'label': c[0]
        }
        domain.append(cur)
    allFunctions = reusableLibManage.getAllFunctions()
    for f in allFunctions:
        cur = {
            'value': f[0],
            'label': f[0]
        }
        functions.append(cur)
    res = {
        'pattern': pattern,
        'domain': domain,
        'functions': functions
    }
    return res


@app.route('/updatePatternInLib', methods=['GET'])
@cross_origin()
def updatePattern():
    patternId = request.values.get('id')
    patternName = request.values.get('name')
    patternDomain = request.values.get('class')
    patternDesc = request.values.get('desc')
    patternFunctions = request.values.get('functions')
    reusableLibManage.updatePattern(patternId, patternName, patternDomain, patternDesc, patternFunctions)
    return 'Successful Update!'


@app.route('/deletePatternInLib', methods=['GET'])
@cross_origin()
def deletePattern():
    patternId = request.values.get('id')
    reusableLibManage.deletePattern(patternId)
    return 'Successful Delete!'


@app.route('/addPatternInLib', methods=['GET'])
@cross_origin()
def addPattern():
    patternName = request.values.get('name')
    patternDomain = request.values.get('class')
    patternDesc = request.values.get('desc')
    patternFunctions = request.values.get('functions')
    reusableLibManage.addPattern(patternName, patternDomain, patternDesc, patternFunctions)
    return 'Successful Add!'


@app.route('/getFunctionInLib', methods=['GET'])
@cross_origin()
def getAllFunctionInfo():
    functionInfo = reusableLibManage.getAllFunctionInfo()
    functionArray = []
    for f in functionInfo:
        cur = {
            'number': f[0],
            'functionName': f[1],
            'functionDesc': f[2],
            'functionParam': f[3],
            'output': f[4],
            'onChainData': f[5]
        }
        functionArray.append(cur)
    paramName = reusableLibManage.getAllParam()
    param = []
    for p in paramName:
        cur = {
            'value': p[0],
            'label': p[0]
        }
        param.append(cur)
    dataName = reusableLibManage.getAllChainData()
    data = []
    for d in dataName:
        cur = {
            'value': d[0],
            'label': d[0]
        }
        data.append(cur)
    res = {
        'functionInfo': functionArray,
        'param': param,
        'data': data
    }
    return res


@app.route('/getFunctionCodeInLib', methods=['GET'])
@cross_origin()
def getFunctionCode():
    functionId = request.values.get('id')
    code = reusableLibManage.getFunctionCode(functionId)
    return code[0][0]


@app.route('/deleteFunctionInLib', methods=['GET'])
@cross_origin()
def deleteFunction():
    functionId = request.values.get('id')
    reusableLibManage.deleteFunction(functionId)
    return 'Successful Delete!'


@app.route('/updateFunctionCodeInLib', methods=['GET'])
@cross_origin()
def updateFunction():
    functionId = request.values.get('id')
    functionName = request.values.get('functionName')
    functionDesc = request.values.get('functionDesc')
    functionParam = request.values.get('functionParam')
    output = request.values.get('output')
    chainData = request.values.get('chainData')
    code = request.values.get('code')
    reusableLibManage.updateFunction(functionId, functionName, functionDesc, functionParam, output, chainData, code)
    return 'Successful Update!'


@app.route('/addFunctionInLib', methods=['GET'])
@cross_origin()
def addFunction():
    functionName = request.values.get('functionName')
    functionDesc = request.values.get('functionDesc')
    functionParam = request.values.get('functionParam')
    output = request.values.get('output')
    chainData = request.values.get('chainData')
    code = request.values.get('code')
    reusableLibManage.addFunction(functionName, functionDesc, functionParam, output, chainData, code)
    return 'Successful Add!'


@app.route('/getResInLib', methods=['GET'])
@cross_origin()
def getAllResInfo():
    resInfo = reusableLibManage.getAllResInfo()
    resArray = []
    for f in resInfo:
        cur = {
            'number': f[0],
            'resName': f[1],
            'resPattern': f[2],
            'resDesc': f[3],
            'resParam': f[4],
            'resData': f[5]
        }
        resArray.append(cur)
    paramName = reusableLibManage.getAllParam()
    param = []
    for p in paramName:
        cur = {
            'value': p[0],
            'label': p[0]
        }
        param.append(cur)
    dataName = reusableLibManage.getAllChainData()
    data = []
    for d in dataName:
        cur = {
            'value': d[0],
            'label': d[0]
        }
        data.append(cur)
    res = {
        'resInfo': resArray,
        'param': param,
        'data': data
    }
    return res


@app.route('/getResCodeInLib', methods=['GET'])
@cross_origin()
def getResCode():
    resId = request.values.get('id')
    code = reusableLibManage.getResCode(resId)
    return code[0][0]


@app.route('/updateResCodeInLib', methods=['GET'])
@cross_origin()
def updateRes():
    resId = request.values.get('id')
    resName = request.values.get('resName')
    resPattern = request.values.get('resPattern')
    resDesc = request.values.get('resDesc')
    resParam = request.values.get('resParam')
    chainData = request.values.get('chainData')
    code = request.values.get('code')
    reusableLibManage.updateRes(resId, resName, resPattern, resDesc, resParam, chainData, code)
    return 'Successful Update!'


@app.route('/deleteResInLib', methods=['GET'])
@cross_origin()
def deleteRes():
    resId = request.values.get('id')
    reusableLibManage.deleteRes(resId)
    return 'Successful Delete!'


@app.route('/addResInLib', methods=['GET'])
@cross_origin()
def addRes():
    resName = request.values.get('resName')
    resPattern = request.values.get('resPattern')
    resDesc = request.values.get('resDesc')
    resParam = request.values.get('resParam')
    chainData = request.values.get('chainData')
    code = request.values.get('code')
    reusableLibManage.addRes(resName, resPattern, resDesc, resParam, chainData, code)
    return 'Successful Add!'


@app.route('/getData', methods=['GET'])
@cross_origin()
def getDataInfo():
    data = reusableLibManage.getData()
    param = reusableLibManage.getParam()
    res = []
    for d in data:
        cur = {
            'number': 'd' + str(d[0]),
            'name': d[1],
            'desc': d[2],
            'type': d[3],
            'source': 'on-chain'
        }
        res.append(cur)
    for p in param:
        cur = {
            'number': 'p' + str(p[0]),
            'name': p[1],
            'desc': p[2],
            'type': p[3],
            'source': 'off-chain'
        }
        res.append(cur)
    return res


@app.route('/updateData', methods=['GET'])
@cross_origin()
def updateData():
    dataId = request.values.get('id')
    dataName = request.values.get('name')
    dataDesc = request.values.get('desc')
    dataType = request.values.get('type')
    reusableLibManage.updateData(dataId, dataName, dataDesc, dataType)
    return 'Successful Update!'


@app.route('/updateParam', methods=['GET'])
@cross_origin()
def updateParam():
    paramId = request.values.get('id')
    paramName = request.values.get('name')
    paramDesc = request.values.get('desc')
    paramType = request.values.get('type')
    reusableLibManage.updateParam(paramId, paramName, paramDesc, paramType)
    return 'Successful Update!'


@app.route('/deleteData', methods=['GET'])
@cross_origin()
def deleteData():
    dataId = request.values.get('id')
    reusableLibManage.deleteData(dataId)
    return 'Successful Delete!'


@app.route('/deleteParam', methods=['GET'])
@cross_origin()
def deleteParam():
    paramId = request.values.get('id')
    reusableLibManage.deleteParam(paramId)
    return 'Successful Delete!'


@app.route('/addData', methods=['GET'])
@cross_origin()
def addData():
    dataName = request.values.get('name')
    dataDesc = request.values.get('desc')
    dataType = request.values.get('type')
    reusableLibManage.addData(dataName, dataDesc, dataType)
    return 'Successful Add!'


@app.route('/addParam', methods=['GET'])
@cross_origin()
def addParam():
    paramName = request.values.get('name')
    paramDesc = request.values.get('desc')
    paramType = request.values.get('type')
    reusableLibManage.addParam(paramName, paramDesc, paramType)
    return 'Successful Add!'


@app.route('/analysisModel', methods=['POST'])
@cross_origin()
def getAnalysisModel():
    content = request.json.get('cim')
    Note = open('tmp_cim\cim.puml', mode='a')
    Note.seek(0)
    Note.truncate()
    Note.write(content)
    Note.close()
    parsePUML()
    convert()
    outputCode()
    contractInfo = codeGeneration.getContractName()
    contractData = codeGeneration.getContractData()
    contractRes = codeGeneration.getRestrictionInfo()
    dataInfo = []
    for d in contractData:
        name = d.get('dataName')
        desc = d.get('dataDesc')
        dataDetail = codeGeneration.getDataDetailInfo(name)
        cur = {
            'dataName': name,
            'dataDesc': desc,
            'dataType': dataDetail[1].get('value'),
            'dataVisible': dataDetail[2].get('value'),
            'dataConstant': dataDetail[4].get('value'),
            'dataValue': dataDetail[3].get('value'),
            'dataSource': dataDetail[5].get('value'),
        }
        dataInfo.append(cur)
    resInfo = []
    for r in contractRes:
        name = r.get('restrictionName')
        desc = r.get('restrictionDesc')
        resDetail = codeGeneration.getResDetailInfo(name)
        cur = {
            'restrictionName': name,
            'restrictionDesc': desc,
            'restrictionData': resDetail[2].get('value'),
            'restrictionparam': resDetail[3].get('value')
        }
        resInfo.append(cur)
    taskInfo = []
    processInfo = codeGeneration.getProcessInfo()
    for p in processInfo:
        patternName = p.get('patternName')
        functionList = codeGeneration.getProcessDetailInfo(patternName)[2].get('value').split(',')
        for f in functionList:
            functionInfo = codeGeneration.getFunctionDetailInfo(f)
            cur = {
                'functionName': f,
                'functionDesc': functionInfo.get('functionDesc'),
                'functionData': functionInfo.get('functionData'),
                'functionParam': functionInfo.get('functionParam'),
                'functionRes': functionInfo.get('funcRes'),
                'functionReturn': functionInfo.get('functionReturn')
            }
            taskInfo.append(cur)
    data = {
        'cimInfo': [{
            'contractKey': '合同名',
            'contractValue': contractInfo.get('name')
        }, {
            'contractKey': '合同描述',
            'contractValue': contractInfo.get('desc')
        }, {
            'contractKey': '合同签约方',
            'contractValue': contractInfo.get('party').strip('[').strip(']')
        }],
        'dataInfo': dataInfo,
        'resInfo': resInfo,
        'taskInfo': taskInfo
    }
    return data


if __name__ == '__main__':
    modelConvert.truncateCimDB()
    modelConvert.truncatePimDB()
    app.run(host='127.0.0.1', port=9014, )  # 运行app
    # slither.sshUploadFile()
