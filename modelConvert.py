import datetime
import json
import time
import xml.dom.minidom
import pymysql
import os
import matplotlib.pyplot as plt
import time
from codeGeneration import codeGenerate, outputCode
from nlp import serviceSelectionByProcess


def writeFile(content):
    Note = open('D:\研\低代码工具\myPlantuml\public\cim.txt', mode='a')
    Note.seek(0)
    Note.truncate()
    Note.write(content)
    Note.close()
    os.system("java -jar plantuml.jar -tsvg D:\\研\\低代码工具\\myPlantuml\\public\\cim.txt")


def parsePUML():
    # 从plantuml文件转换到xmi文件
    # os.system("java -jar plantuml.jar .\\plantUML_dia\\a.puml -xmi:star")
    os.system("java -jar plantuml.jar .\\tmp_cim\\cim.puml -xmi:star")

    # dom = xml.dom.minidom.parse('plantUML_dia/a.xmi')
    dom = xml.dom.minidom.parse('tmp_cim/cim.xmi')

    root = dom.documentElement
    contents = root.getElementsByTagName('XMI.content')
    model = contents[0].getElementsByTagName('UML:Model')
    namespace = model[0].getElementsByTagName('UML:Namespace.ownedElement')
    objects = namespace[0].getElementsByTagName('UML:Class')
    # 开始解析对象名和对象属性
    for obj in objects:
        name = obj.getAttribute('name')
        # 用：分隔对象名和类名
        objAndClass = name.split(':')
        objName = objAndClass[0]
        className = objAndClass[1]
        objId = obj.getAttribute('xmi.id')
        # 插入数据库
        insertObject(objName, className, objId)
        # 解析对象属性
        features = obj.getElementsByTagName('UML:Classifier.feature')
        attributes = features[0].getElementsByTagName('UML:Attribute')
        for attr in attributes:
            attribute = attr.getAttribute('name')
            # 属性的分隔：name = "123"，分离出name和它的值
            sitemap = attribute.split(' = ')
            attrName = sitemap[0]
            attrValue = sitemap[1]
            # 插入数据库
            insertAttributions(objId, attrName, attrValue)
    # 开始解析流
    associations = namespace[0].getElementsByTagName('UML:Association')
    for flow in associations:
        # 关联的名字
        flowName = flow.getAttribute('name')
        # print(flowName)
        connections = flow.getElementsByTagName('UML:Association.connection')
        connectionEnd = connections[0].getElementsByTagName('UML:AssociationEnd')
        # 流的指向端end和流的开始端start
        end = connectionEnd[0].getAttribute('type')
        start = connectionEnd[1].getAttribute('type')
        insertFlow(end, start, flowName)


# CIM到PIM的转换
def convert():
    # 返回给前端的值
    result = ''
    # 根据类名完成对象的转换
    global newO
    objToClass = selectObjectByClass('Contract')

    # Note = open('tmp_cim/pim.puml', mode='a')
    Note = open('C:\\Users\\24476\Desktop\project-mda\pimfront\public\pim.txt', mode='a')

    # 清空文件
    Note.seek(0)
    Note.truncate()
    Note.write('@startuml\n')
    result += '@startuml\n'
    # 合约对象的转换
    annotation = ""
    clauses = ""
    participants = ""
    data = ""
    restrictions = ""
    for o in objToClass:
        # 合约对象名（CIM合约名）
        newO = o[0]
        writeTxt = "object " + "\"" + newO + ":" + "SmartContract\" " + "as " + newO
        Note.write(writeTxt + '\n')
        result += writeTxt + '\n'
        xmiId = o[1]
        # 该对象的属性
        attributions = selectAttrsById(xmiId)
        for a in attributions:
            newAttrName = a[0]
            newAttrValue = a[1]
            match newAttrName:
                case "description":
                    writeTxt = newO + " : " + "annotation = " + newAttrValue + '\n'
                    annotation = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
                case "clauses":
                    writeTxt = newO + " : " + newAttrName + " = " + newAttrValue + '\n'
                    clauses = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
                case "participants":
                    writeTxt = newO + " : " + newAttrName + " = " + newAttrValue + '\n'
                    participants = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
                case "data":
                    writeTxt = newO + " : " + newAttrName + " = " + newAttrValue + '\n'
                    data = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
                case "restrictions":
                    writeTxt = newO + " : " + newAttrName + " = " + newAttrValue + '\n'
                    restrictions = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
        insertSC(newO, annotation, restrictions, clauses, participants, data)
    # 参与方对象转换
    objToClass = selectObjectByClass('Participant')
    for o in objToClass:
        # 参与方对象名
        newO = o[0]
        writeTxt = "object " + "\"" + newO + ":" + "Participant\" " + "as " + newO
        Note.write(writeTxt + '\n')
        result += writeTxt + '\n'
        xmiId = o[1]
        role_names = ""
        # 该对象的属性
        attributions = selectAttrsById(xmiId)
        for a in attributions:
            newAttrName = a[0]
            newAttrValue = a[1]
            writeTxt = newO + " : " + "address" + " = " + "null" + '\n'
            Note.write(writeTxt)
            result += writeTxt
            match newAttrName:
                case "roleNames":
                    writeTxt = newO + " : " + newAttrName + " = " + newAttrValue + '\n'
                    role_names = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
        insertParticipants(newO, role_names)
    # 条款对象的转换
    objToClass = selectObjectByClass('Clause')
    for o in objToClass:
        # 条款信息
        newO = o[0]
        writeTxt = "object " + "\"" + newO + ":" + "ClauseInfo\" " + "as " + newO
        Note.write(writeTxt + '\n')
        result += writeTxt + '\n'
        xmiId = o[1]
        # 对象属性
        attributions = selectAttrsById(xmiId)
        domain = ""
        processes = ""
        for a in attributions:
            newAttrName = a[0]
            newAttrValue = a[1]
            match newAttrName:
                case "domain":
                    writeTxt = newO + " : " + newAttrName + " = " + newAttrValue + '\n'
                    domain = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
                case "exector":
                    writeTxt = newO + " : " + newAttrName + " = " + newAttrValue + '\n'
                    Note.write(writeTxt)
                    result += writeTxt
                case "patterns":
                    writeTxt = newO + " : " + "processes" + " = " + newAttrValue + '\n'
                    processes = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
        insertClause(newO, domain, processes)
    # 模式对象转换
    objToClass = selectObjectByClass('Pattern')
    for o in objToClass:
        # 模式对象
        newO = o[0]
        writeTxt = "object " + "\"" + newO + ":" + "Process\" " + "as " + newO
        Note.write(writeTxt + '\n')
        result += writeTxt + '\n'
        xmiId = o[1]
        description = ""
        functions = ""
        type_name = ""
        # 对象属性
        attributions = selectAttrsById(xmiId)
        for a in attributions:
            newAttrName = a[0]
            newAttrValue = a[1]
            match newAttrName:
                case "description":
                    writeTxt = newO + " : " + newAttrName + " = " + newAttrValue + '\n'
                    description = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
                case "tasks":
                    fixed_s = "[" + ",".join(f'"{item}"' for item in newAttrValue.strip("[]").split(",")) + "]"
                    list_from_string = json.loads(fixed_s)
                    functions = "["
                    for value in list_from_string:
                        if judgeTaskType(value):
                            functions += value
                            functions += ","
                    functions = functions.rstrip(',')
                    writeTxt = newO + " : " + "functions" + " = " + functions + ']' + '\n'
                    Note.write(writeTxt)
                    result += writeTxt
                case "type":
                    writeTxt = newO + " : " + newAttrName + " = " + newAttrValue + '\n'
                    type_name = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
        insertProcess(newO, type_name, description, functions)
    # 合约任务对象转换
    objToClass = selectObjectByClass('ContractTask')
    for o in objToClass:
        # 动作对象
        newO = o[0]
        writeTxt = "object " + "\"" + newO + ":" + "Function\" " + "as " + newO
        Note.write(writeTxt + '\n')
        result += writeTxt + '\n'
        xmiId = o[1]
        # 对象属性
        attributions = selectAttrsById(xmiId)
        # 三种属性都对应约束
        writeRestriction = newO + " : " + "functionRestriction" + " = "
        restrictions = []
        description = ""
        ifConstructor = ""
        ifUpdateData = ""
        ifGenerateTransaction = ""
        logs = ""
        dataNames = ""
        params = ""
        output = ""
        right = ""
        for a in attributions:
            newAttrName = a[0]
            newAttrValue = a[1]
            match newAttrName:
                case "description":
                    writeTxt = newO + " : " + "annotation" + " = " + newAttrValue + '\n'
                    description = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
                case "restricts":
                    if newAttrValue != "null":
                        restrictionString = newAttrValue.strip('[')
                        restrictionString = restrictionString.strip(']')
                        restrictionList = restrictionString.split(',')
                        for r in restrictionList:
                            restrictions.append(r)
                case "roleRight":
                    writeTxt = newO + " : " + "right" + " = " + newAttrValue + '\n'
                    right = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
                case "ifInitializeContract":
                    writeTxt = newO + " : " + "ifConstructor" + " = " + newAttrValue + '\n'
                    ifConstructor = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
                case "ifUpdateData":
                    writeTxt = newO + " : " + newAttrName + " = " + newAttrValue + '\n'
                    ifUpdateData = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
                case "ifGenerateTransaction":
                    writeTxt = newO + " : " + newAttrName + " = " + newAttrValue + '\n'
                    ifGenerateTransaction = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
                case "dataName":
                    if newAttrValue != "null":
                        dataString = newAttrValue.strip('[')
                        dataString = dataString.strip(']')
                        # 数据列表
                        dataList = dataString.split(',')
                        # 参数列表
                        param = []
                        # 链上数据列表
                        onChain = []
                        for d in dataList:
                            flag = selectDataType(d)
                            if flag == 0:
                                param.append(d)
                            else:
                                onChain.append(d)
                        if len(onChain) != 0:
                            writeTxt = newO + " : " + "dataNames" + " = " + str(onChain) + '\n'
                            dataNames = str(onChain)
                            Note.write(writeTxt)
                            result += writeTxt
                        else:
                            writeTxt = newO + " : " + "dataNames" + " = " + "null" + '\n'
                            dataNames = "null"
                            Note.write(writeTxt)
                            result += writeTxt
                        if len(param) != 0:
                            writeTxt = newO + " : " + "params" + " = " + str(param) + '\n'
                            params = str(param)
                            Note.write(writeTxt)
                            result += writeTxt
                        else:
                            writeTxt = newO + " : " + "params" + " = " + "null" + '\n'
                            params = "null"
                            Note.write(writeTxt)
                            result += writeTxt
                    else:
                        writeTxt = newO + " : " + "dataNames" + " = " + "null" + '\n'
                        dataNames = "null"
                        Note.write(writeTxt)
                        result += writeTxt
                        writeTxt = newO + " : " + "params" + " = " + "null" + '\n'
                        params = "null"
                        Note.write(writeTxt)
                        result += writeTxt
                case "logs":
                    writeTxt = newO + " : " + "logs" + " = " + newAttrValue + '\n'
                    logs = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
                case "outputType":
                    writeTxt = newO + " : " + "output" + " = " + newAttrValue + '\n'
                    output = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
        if len(restrictions) != 0:
            insertFunction(newO, description, str(restrictions), right, ifConstructor, ifUpdateData,
                           ifGenerateTransaction,
                           dataNames, params, logs, output)
            writeRestriction += str(restrictions) + '\n'
            Note.write(writeRestriction)
            result += writeRestriction
        else:
            insertFunction(newO, description, 'null', right, ifConstructor, ifUpdateData,
                           ifGenerateTransaction,
                           dataNames, params, logs, output)
            writeRestriction += 'null' + '\n'
            Note.write(writeRestriction)
            result += writeRestriction
    # 约束
    objToClass = selectObjectByClass('Restriction')
    for o in objToClass:
        # 约束对象
        newO = o[0]
        writeTxt = "object " + "\"" + newO + ":" + "Restriction\" " + "as " + newO
        Note.write(writeTxt + '\n')
        result += writeTxt + '\n'
        xmiId = o[1]
        description = ""
        res_type = ""
        dataNames = ""
        params = ""
        # 对象属性
        attributions = selectAttrsById(xmiId)
        for a in attributions:
            newAttrName = a[0]
            newAttrValue = a[1]
            match newAttrName:
                case "description":
                    writeTxt = newO + " : " + newAttrName + " = " + newAttrValue + '\n'
                    description = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
                case "dataNames":
                    dataString = newAttrValue.strip('[')
                    dataString = dataString.strip(']')
                    # 数据列表
                    dataList = dataString.split(',')
                    # 参数列表
                    param = []
                    # 链上数据列表
                    onChain = []
                    for d in dataList:
                        flag = selectDataType(d)
                        if flag == 0:
                            param.append(d)
                        else:
                            onChain.append(d)
                    if len(onChain) != 0:
                        dataNames = str(onChain)
                        writeTxt = newO + " : " + "dataNames" + " = " + dataNames + '\n'
                        Note.write(writeTxt)
                        result += writeTxt
                    else:
                        writeTxt = newO + " : " + "dataNames" + " = " + "null" + '\n'
                        dataNames = "null"
                        Note.write(writeTxt)
                        result += writeTxt
                    if len(param) != 0:
                        params = str(param)
                        params.replace('\'', '')
                        writeTxt = newO + " : " + "params" + " = " + params + '\n'
                        Note.write(writeTxt)
                        result += writeTxt
                    else:
                        writeTxt = newO + " : " + "params" + " = " + "null" + '\n'
                        params = "null"
                        Note.write(writeTxt)
                        result += writeTxt
                case "type":
                    writeTxt = newO + " : " + "pattern" + " = " + newAttrValue + '\n'
                    res_type = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
        insertRes(newO, res_type, description, dataNames, params)
    # 链上数据
    objToClass = selectObjectByClass('SimpleData')
    for o in objToClass:
        # 数据对象
        newO = o[0]
        writeTxt = "object " + "\"" + newO + ":" + "ContractData\" " + "as " + newO
        Note.write(writeTxt + '\n')
        result += writeTxt + '\n'
        xmiId = o[1]
        attributions = selectAttrsById(xmiId)
        c_type = ""
        visibility = ""
        value = ""
        ifConstant = ""
        unixTime = "0"
        description = ""
        ifTimeType = False
        for a in attributions:
            newAttrName = a[0]
            newAttrValue = a[1]
            match newAttrName:
                case "type":
                    if newAttrValue == 'time':
                        ifTimeType = True
                    writeTxt = newO + " : " + newAttrName + " = " + newAttrValue + '\n'
                    c_type = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
                case "initialValue":
                    # xxxx.xx.xx时间格式转unix时间
                    if ifTimeType:
                        year, month, day = map(int, newAttrValue.split('.'))
                        time_tuple = (year, month, day, 0, 0, 0, 0, 0, 0)
                        unix_timestamp = int(time.mktime(time_tuple))
                        newAttrValue = unix_timestamp
                    writeTxt = newO + " : " + "value" + " = " + f"{newAttrValue}" + '\n'
                    value = f"{newAttrValue}"
                    Note.write(writeTxt)
                    result += writeTxt
                case "ifPrivate":
                    if newAttrValue == "true":
                        writeTxt = newO + " : " + "visibility" + " = " + "private" + '\n'
                        visibility = "private"
                        Note.write(writeTxt)
                        result += writeTxt
                    else:
                        writeTxt = newO + " : " + "visibility" + " = " + "public" + '\n'
                        visibility = "public"
                        Note.write(writeTxt)
                        result += writeTxt
                case "ifMutable":
                    if newAttrValue == "true":
                        writeTxt = newO + " : " + "ifConstant" + " = " + "false" + '\n'
                        ifConstant = "false"
                        Note.write(writeTxt)
                        result += writeTxt
                    else:
                        writeTxt = newO + " : " + "ifConstant" + " = " + "true" + '\n'
                        ifConstant = "true"
                        Note.write(writeTxt)
                        result += writeTxt
                case "description":
                    writeTxt = newO + " : " + "description" + " = " + newAttrValue + '\n'
                    description = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
        insertContractData(newO, c_type, visibility, value, ifConstant, unixTime, "null", description)
    # 链上struct复合数据
    objToClass = selectObjectByClass('CombineData')
    for o in objToClass:
        # 数据对象
        newO = o[0]
        writeTxt = "object " + "\"" + newO + ":" + "CombinedData\" " + "as " + newO
        Note.write(writeTxt + '\n')
        result += writeTxt + '\n'
        xmiId = o[1]
        attributions = selectAttrsById(xmiId)
        c_type = "struct"
        visibility = ""
        value = ""
        ifConstant = ""
        unixTime = "0"
        allTypeName = ""
        description = ""
        for a in attributions:
            newAttrName = a[0]
            newAttrValue = a[1]
            match newAttrName:
                case "initialValue":
                    writeTxt = newO + " : " + "value" + " = " + newAttrValue + '\n'
                    value = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
                case "ifPrivate":
                    writeTxt = newO + " : " + "visibility" + " = " + "null" + '\n'
                    visibility = "null"
                    Note.write(writeTxt)
                    result += writeTxt
                case "ifMutable":
                    writeTxt = newO + " : " + "ifConstant" + " = " + "null" + '\n'
                    ifConstant = "null"
                    Note.write(writeTxt)
                    result += writeTxt
                case "description":
                    writeTxt = newO + " : " + "description" + " = " + newAttrValue + '\n'
                    description = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
                case "allTypeName":
                    writeTxt = newO + " : " + "allTypeName" + " = " + newAttrValue + '\n'
                    allTypeName = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
        insertContractData(newO, c_type, visibility, value, ifConstant, unixTime, allTypeName, description)
    # 链上时间数据
    objToClass = selectObjectByClass('Date')
    for o in objToClass:
        # 数据对象
        newO = o[0]
        writeTxt = "object " + "\"" + newO + ":" + "Date\" " + "as " + newO
        Note.write(writeTxt + '\n')
        result += writeTxt + '\n'
        xmiId = o[1]
        attributions = selectAttrsById(xmiId)
        c_type = "null"
        visibility = ""
        value = ""
        ifConstant = ""
        unixTime = ""
        description = ""
        for a in attributions:
            newAttrName = a[0]
            newAttrValue = a[1]
            match newAttrName:
                case "initialValue":
                    writeTxt = newO + " : " + "value" + " = " + newAttrValue + '\n'
                    value = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
                case "ifPrivate":
                    if newAttrValue == "true":
                        writeTxt = newO + " : " + "visibility" + " = " + "private" + '\n'
                        visibility = "private"
                        Note.write(writeTxt)
                        result += writeTxt
                    else:
                        writeTxt = newO + " : " + "visibility" + " = " + "public" + '\n'
                        visibility = "public"
                        Note.write(writeTxt)
                        result += writeTxt
                case "ifMutable":
                    if newAttrValue == "true":
                        writeTxt = newO + " : " + "ifConstant" + " = " + "false" + '\n'
                        ifConstant = "false"
                        Note.write(writeTxt)
                        result += writeTxt
                    else:
                        writeTxt = newO + " : " + "ifConstant" + " = " + "true" + '\n'
                        ifConstant = "true"
                        Note.write(writeTxt)
                        result += writeTxt
                case "standardTime":
                    x = time.strptime(newAttrValue, "%Y-%m-%d %H:%M:%S")
                    y = time.mktime(x)
                    z = str(round(y))
                    writeTxt = newO + " : " + "unixTime" + " = " + z + '\n'
                    unixTime = z
                    Note.write(writeTxt)
                    result += writeTxt
                case "description":
                    writeTxt = newO + " : " + "description" + " = " + newAttrValue + '\n'
                    description = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
        insertContractData(newO, c_type, visibility, value, ifConstant, unixTime, "null", description)
    # 链外数据，函数参数
    objToClass = selectObjectByClass('OffChainData')
    for o in objToClass:
        # 数据对象
        newO = o[0]
        writeTxt = "object " + "\"" + newO + ":" + "Param\" " + "as " + newO
        Note.write(writeTxt + '\n')
        result += writeTxt + '\n'
        xmiId = o[1]
        attributions = selectAttrsById(xmiId)
        p_type = ""
        description = ""
        for a in attributions:
            newAttrName = a[0]
            newAttrValue = a[1]
            match newAttrName:
                case "type":
                    writeTxt = newO + " : " + newAttrName + " = " + newAttrValue + '\n'
                    p_type = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
                case "description":
                    writeTxt = newO + " : " + newAttrName + " = " + newAttrValue + '\n'
                    description = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
        insertParam(newO, p_type, description)
    # 日志解析
    objToClass = selectObjectByClass('-')
    for o in objToClass:
        # 日志对象
        newO = o[0]
        writeTxt = "object " + "\"" + newO + ":" + "Log\" " + "as " + newO
        Note.write(writeTxt + '\n')
        result += writeTxt + '\n'
        xmiId = o[1]
        attributions = selectAttrsById(xmiId)
        params = ""
        for a in attributions:
            newAttrName = a[0]
            newAttrValue = a[1]
            match newAttrName:
                case "dataNames":
                    writeTxt = newO + " : " + newAttrName + " = " + newAttrValue + '\n'
                    params = newAttrValue
                    Note.write(writeTxt)
                    result += writeTxt
        insertLog(newO, params)
    # 对象及属性解析结束
    # 关联关系解析
    allFlows = selectFlow()
    for f in allFlows:
        end = f[0]
        start = f[1]
        label = f[2]
        # 开端的对象和类
        # (('Renting', 'Contract'),)
        objAndCla = selectObjAndClaById(start)
        objName = objAndCla[0][0]
        className = objAndCla[0][1]
        if className == 'Contract':
            # 尾端的对象和类
            objAndCla_end = selectObjAndClaById(end)
            objName_end = objAndCla_end[0][0]
            className_end = objAndCla_end[0][1]
            if className_end != 'OffChainData':
                # o18 <..o1: Partof
                writeTxt = objName_end + "<.. " + objName + ": " + label + '\n'
                Note.write(writeTxt)
                result += writeTxt
        if className == 'Clause':
            # 尾端的对象和类
            objAndCla_end = selectObjAndClaById(end)
            objName_end = objAndCla_end[0][0]
            # className_end = objAndCla_end[0][1]
            writeTxt = objName_end + "<.. " + objName + ": " + label + '\n'
            Note.write(writeTxt)
            result += writeTxt
        if className == 'Pattern':
            # 尾端的对象和类
            objAndCla_end = selectObjAndClaById(end)
            objName_end = objAndCla_end[0][0]
            className_end = objAndCla_end[0][1]
            if className_end != 'UserTask':
                writeTxt = objName_end + "<.. " + objName + ": " + label + '\n'
                Note.write(writeTxt)
                result += writeTxt
        if className == 'ContractTask':
            # 尾端的对象和类
            objAndCla_end = selectObjAndClaById(end)
            objName_end = objAndCla_end[0][0]
            writeTxt = objName_end + "<.. " + objName + ": " + label + '\n'
            Note.write(writeTxt)
            result += writeTxt
    # 全局约束的关联
    globalRes = selectObjectByClass('GlobalRestriction')
    for g in globalRes:
        # 每一个约束
        res = g[0]
        allFunctions = selectObjectByClass('Action')
        for a in allFunctions:
            functionName = a[0]
            functionId = a[1]
            allGloRes = selectGlobalRes(functionId)[0][0]
            allString = allGloRes.strip('[')
            allString = allString.strip(']')
            allList = allString.split(',')
            if res in allList:
                writeTxt = res + "<.. " + functionName + ": " + "Call" + '\n'
                Note.write(writeTxt)
                result += writeTxt
    # 在函数和数据之间增加流
    objToClass = selectObjectByClass('ContractTask')
    for o in objToClass:
        # 动作对象
        newO = o[0]
        paramListStr = selectParamByFunction(newO)
        paramStr = paramListStr[0][0]
        paramStr = paramStr.strip('[')
        paramStr = paramStr.strip(']')
        paramList = paramStr.split(',')
        for p in paramList:
            p = p.strip('\'')
            if p != 'null':
                writeTxt = p + "<.." + newO + ": " + "Accept" + '\n'
                Note.write(writeTxt)
                result += writeTxt
        dataListStr = selectDataByFunction(newO)
        dataList = dataListStr[0][0].strip('[').strip(']').replace("'", "").split(',')
        for d in dataList:
            writeTxt = d + "<.." + newO + ": " + "Accept" + '\n'
            Note.write(writeTxt)
            result += writeTxt
    # 在约束和数据之间增加流
    objToClass = selectObjectByClass('Restriction')
    for o in objToClass:
        # 动作对象
        newO = o[0]
        paramListStr = selectParamByRes(newO)
        paramStr = paramListStr[0][0]
        paramStr = paramStr.strip('[')
        paramStr = paramStr.strip(']')
        paramList = paramStr.split(',')
        for p in paramList:
            p = p.strip('\'')
            if p != 'null':
                writeTxt = p + "<.." + newO + ": " + "Accept" + '\n'
                Note.write(writeTxt)
                result += writeTxt
        dataListStr = selectDataByRes(newO)
        dataList = dataListStr[0][0].strip('[').strip(']').replace("'", "").split(',')
        for d in dataList:
            if d != 'null':
                writeTxt = d + "<.." + newO + ": " + "Accept" + '\n'
                Note.write(writeTxt)
                result += writeTxt
    Note.write('@enduml\n')
    result += '@enduml\n'
    Note.close()
    os.system("java -jar plantuml.jar -tsvg C:\\Users\\24476\Desktop\project-mda\pimfront\public\pim.txt")
    return result


def connectDB():
    conn = pymysql.connect(host='localhost', user='root', password='lwy2000712/', database='mda', charset='utf8')
    return conn


def insertObject(objName, className, xmiId):
    conn = connectDB()
    cur = conn.cursor()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = "insert into objects (obj_name,class_name,xmi_id,create_time,update_time) \
                          values('%s','%s','%s','%s','%s')" % \
          (objName, className, xmiId, dt, dt)
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


def insertAttributions(xmiId, attrName, attrValue):
    conn = connectDB()
    cur = conn.cursor()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = "insert into attributes (xmi_id, attr_name, attr_value, create_time,update_time) \
          values('%s','%s','%s','%s','%s')" % \
          (xmiId, attrName, attrValue, dt, dt)
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


def insertFlow(end, start, label):
    conn = connectDB()
    cur = conn.cursor()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = "insert into flows (end, start, label, create_time, update_time)  \
          values('%s','%s','%s','%s','%s')" % \
          (end, start, label, dt, dt)
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


def selectObjectByClass(className):
    conn = connectDB()
    cur = conn.cursor()
    sql = "select distinct obj_name,xmi_id from objects where class_name = '%s'" % \
          className
    cur.execute(sql)
    objs = cur.fetchall()
    cur.close()
    conn.close()
    return objs


def selectAttrsById(xmiId):
    conn = connectDB()
    cur = conn.cursor()
    sql = "select distinct attr_name,attr_value from attributes where xmi_id = '%s'" % \
          xmiId
    cur.execute(sql)
    attrs = cur.fetchall()
    cur.close()
    conn.close()
    return attrs


# 返回是链上数据还是函数参数，1为链上数据,0为函数参数，2为错误
def selectDataType(dataName):
    # print(dataName + '\n')
    conn = connectDB()
    cur = conn.cursor()
    sql = "select distinct class_name from objects where obj_name = '%s'" % \
          dataName
    cur.execute(sql)
    # print(dataName)
    className = cur.fetchall()
    # print(className)
    flag = 1
    if className[0][0] == "OffChainData":
        flag = 0
    cur.close()
    conn.close()
    return flag


# 返回所有的关联关系
def selectFlow():
    conn = connectDB()
    cur = conn.cursor()
    sql = "select distinct end, start, label from flows"
    cur.execute(sql)
    flows = cur.fetchall()
    cur.close()
    conn.close()
    return flows


def selectObjAndClaById(xmiId):
    conn = connectDB()
    cur = conn.cursor()
    sql = "select distinct obj_name, class_name from objects where xmi_id = '%s'" % \
          xmiId
    cur.execute(sql)
    objAndCla = cur.fetchall()
    cur.close()
    conn.close()
    return objAndCla


def selectGlobalRes(xmiId):
    conn = connectDB()
    cur = conn.cursor()
    sql = "select distinct attr_value from attributes where attr_name = 'GlobalRestrictionNames' and " \
          "xmi_id = '%s'" % \
          xmiId
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res


# 清空CIM表
def truncateCimDB():
    conn = connectDB()
    cur = conn.cursor()
    sql = "truncate table objects"
    cur.execute(sql)
    sql = "truncate table flows"
    cur.execute(sql)
    sql = "truncate table attributes"
    cur.execute(sql)
    cur.close()
    conn.close()


# 保存PIM中生成代码的部分
# 插入表smart_contract
def insertSC(name, annotation, restrictions, clauses, participants, data):
    conn = connectDB()
    cur = conn.cursor()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = "insert into smart_contract (`name`, `annotation`, `restrictions`, `clauses`, `participants`, `data`, `create_time`, " \
          "`update_time`) values('%s','%s','%s','%s','%s','%s','%s','%s')" % \
          (name, annotation, restrictions, clauses, participants, data, dt, dt)
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


# 插入表restriction
def insertRes(name, res_type, description, dataNames, params):
    conn = connectDB()
    cur = conn.cursor()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = """insert into restrictions (res_name, type, res_description, data_names, res_params, create_time, update_time) 
    values ("%s","%s","%s","%s","%s","%s","%s")""" % \
          (name, res_type, description, dataNames, params, dt, dt)
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


# 插入流程表
def insertProcess(name, type_name, description, functions):
    conn = connectDB()
    cur = conn.cursor()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = """insert into process (name, type_name, description, functions, create_time, update_time) 
        values ("%s","%s","%s","%s","%s","%s")""" % \
          (name, type_name, description, functions, dt, dt)
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


# 插入参与方表
def insertParticipants(name, role_names):
    conn = connectDB()
    cur = conn.cursor()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = """insert into participants (name, role_names, create_time, update_time) 
            values ("%s","%s","%s","%s")""" % \
          (name, role_names, dt, dt)
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


# 插入参数
def insertParam(name, p_type, description):
    conn = connectDB()
    cur = conn.cursor()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = """insert into param (name, type, description, create_time, update_time) 
                values ("%s","%s","%s","%s","%s")""" % \
          (name, p_type, description, dt, dt)
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


# 插入日志
def insertLog(name, params):
    conn = connectDB()
    cur = conn.cursor()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = """insert into log (name, params, create_time, update_time) 
                    values ("%s","%s","%s","%s")""" % \
          (name, params, dt, dt)
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


# 插入函数
def insertFunction(name, description, functionRestriction, rights, ifConstructor, ifUpdateData, ifGenerateTransaction,
                   dataNames, params, logs, output):
    conn = connectDB()
    cur = conn.cursor()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = """insert into allFunctions (name, description, functionRestriction, rights, ifConstructor, ifUpdateData, 
    ifGenerateTransaction, dataNames, params, logs, output, create_time, update_time) values ("%s","%s","%s","%s",
    "%s","%s", "%s","%s","%s","%s","%s","%s","%s")""" % \
          (
              name, description, functionRestriction, rights, ifConstructor, ifUpdateData, ifGenerateTransaction,
              dataNames,
              params,
              logs, output, dt, dt)
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


# 插入合约数据
def insertContractData(name, c_type, visibility, value, ifConstant, unixTime, allTypeName, description):
    conn = connectDB()
    cur = conn.cursor()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = """insert into contract_data (name, type, visibility, value, ifConstant, unix_date, allTypeName, 
    description ,create_time, update_time) values ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")""" % \
          (name, c_type, visibility, value, ifConstant, unixTime, allTypeName, description, dt, dt)
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


# 插入条款
def insertClause(name, domain, processes):
    conn = connectDB()
    cur = conn.cursor()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = """insert into clause_info (name, domain, processes, create_time, update_time) 
                            values ("%s","%s","%s","%s","%s")""" % \
          (name, domain, processes, dt, dt)
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


# 清空PIM模型
def truncatePimDB():
    conn = connectDB()
    cur = conn.cursor()
    sql = "truncate table allFunctions"
    cur.execute(sql)
    sql = "truncate table clause_info"
    cur.execute(sql)
    sql = "truncate table contract_data"
    cur.execute(sql)
    sql = "truncate table log"
    cur.execute(sql)
    sql = "truncate table param"
    cur.execute(sql)
    sql = "truncate table participants"
    cur.execute(sql)
    sql = "truncate table process"
    cur.execute(sql)
    sql = "truncate table restrictions"
    cur.execute(sql)
    sql = "truncate table smart_contract"
    cur.execute(sql)
    cur.close()
    conn.close()


def judgeTaskType(name):
    conn = connectDB()
    cur = conn.cursor()
    sql = "select class_name from objects where obj_name = '%s'" % \
          name
    cur.execute(sql)
    typeName = cur.fetchall()
    cur.close()
    conn.close()
    if typeName[0][0] == "ContractTask":
        return True
    else:
        return False


def selectParamByFunction(functionName):
    conn = connectDB()
    cur = conn.cursor()
    sql = "select params from allfunctions where name = '%s'" % \
          functionName
    cur.execute(sql)
    params = cur.fetchall()
    cur.close()
    conn.close()
    return params


def selectDataByFunction(functionName):
    conn = connectDB()
    cur = conn.cursor()
    sql = "select dataNames from allfunctions where name = '%s'" % \
          functionName
    cur.execute(sql)
    params = cur.fetchall()
    cur.close()
    conn.close()
    return params


def selectParamByRes(resName):
    conn = connectDB()
    cur = conn.cursor()
    sql = "select res_params from restrictions where res_name = '%s'" % \
          resName
    cur.execute(sql)
    params = cur.fetchall()
    cur.close()
    conn.close()
    return params


def selectDataByRes(resName):
    conn = connectDB()
    cur = conn.cursor()
    sql = "select data_names from restrictions where res_name = '%s'" % \
          resName
    cur.execute(sql)
    params = cur.fetchall()
    cur.close()
    conn.close()
    return params


# if __name__ == '__main__':
#     truncateCimDB()
#     parsePUML()
#     truncatePimDB()
#     convert()
#     # codeGenerate()
#     outputCode()
    # data = {
    #     'Threshold value': [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7],
    #     'Accuracy': [0.96, 0.96, 0.96, 0.96, 0.92, 0.8, 0.8, 0.76, 0.72, 0.6, 0.6, 0.52, 0.48],
    #     'The number of correct matches': [24, 24, 24, 24, 23, 20, 20, 19, 18, 15, 15, 13, 12]
    # }
    #
    # plt.figure(figsize=(10, 6))  # 设置图表大小
    # plt.subplot(2, 1, 1)  # 创建第一个子图（2行1列，当前是第1个）
    # plt.plot(data['Threshold value'], data['Accuracy'], marker='o')  # 绘制折线图，并添加数据点
    # plt.title('The accuracy varies with the threshold')  # 设置图表标题
    # plt.xlabel('Threshold value')  # 设置x轴标签
    # plt.ylabel('Accuracy')  # 设置y轴标签
    # plt.subplot(2, 1, 2)
    # plt.plot(data['Threshold value'], data['The number of correct matches'], marker='o')
    # plt.title('The number of correct matches varies with the threshold')  # 设置图表标题
    # plt.xlabel('Threshold value')
    # plt.ylabel('The number of correct matches')
    # plt.tight_layout()
    # plt.show()