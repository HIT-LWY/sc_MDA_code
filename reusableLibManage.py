import pymysql


def connectReusableLib():
    conn = pymysql.connect(host='localhost', user='root', password='lwy2000712/', database='reuse_lib', charset='utf8')
    return conn


def getAllContract():
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "select contract_id, name, `desc` from contract"
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    connection.close()
    return res


def getContractCode(contractId):
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "select code from contract where contract_id = '%s'" % contractId
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    connection.close()
    return res[0][0]


def updateContract(contractId, contractName, contractDesc, contractCode):
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "update contract set name='%s', `desc`='%s', code='%s' where contract_id='%s'" % (
        contractName, contractDesc, contractCode, contractId)
    cur.execute(sql)
    connection.commit()
    cur.close()
    connection.close()


def addContract(contractName, contractDesc, contractCode):
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "insert into contract (name, `desc`, code) values ('%s','%s','%s')" % (
        contractName, contractDesc, contractCode)
    cur.execute(sql)
    connection.commit()
    cur.close()
    connection.close()


def getAllPattern():
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "select process_id, process_name, domain, description, functions from reusable_pattern"
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    connection.close()
    return res


def getAllClass():
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "select DISTINCT domain from reusable_pattern where domain IS NOT NULL"
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    connection.close()
    return res


def updatePattern(patternId, patternName, patternDomain, patternDesc, patternFunctions):
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "update reusable_pattern set process_name = '%s', domain = '%s', description = '%s', " \
          "functions = '%s' where process_id = '%s'" \
          % (patternName, patternDomain, patternDesc, patternFunctions, patternId)
    cur.execute(sql)
    connection.commit()
    cur.close()
    connection.close()


def deletePattern(patternId):
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "delete from reusable_pattern where process_id = '%s'" % patternId
    cur.execute(sql)
    connection.commit()
    cur.close()
    connection.close()


def getAllFunctions():
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "select function_name from reusable_function"
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    connection.close()
    return res


def addPattern(patternName, patternDomain, patternDesc, patternFunctions):
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "insert into reusable_pattern (process_name, domain, description, functions) " \
          "values ('%s', '%s', '%s', '%s')" % (patternName, patternDomain, patternDesc, patternFunctions)
    cur.execute(sql)
    connection.commit()
    cur.close()
    connection.close()


def getAllFunctionInfo():
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "select function_id, function_name, description, params, output, on_chain_data from reusable_function"
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    connection.close()
    return res


def getFunctionCode(functionId):
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "select code from reusable_function where function_id = '%s'" % functionId
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    connection.close()
    return res


def getAllParam():
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "select param_name from param_data"
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    connection.close()
    return res


def getAllChainData():
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "select data_name from con_data"
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    connection.close()
    return res


def deleteFunction(functionId):
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "delete from reusable_function where function_id = '%s'" % functionId
    cur.execute(sql)
    connection.commit()
    cur.close()
    connection.close()


def updateFunction(functionId, functionName, functionDesc, functionParam, output, chainData, code):
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "update reusable_function set function_name = '%s', description = '%s', params = '%s', " \
          "output = '%s', on_chain_data = '%s', code = '%s' where function_id = '%s'" \
          % (functionName, functionDesc, functionParam, output, chainData, code, functionId)
    cur.execute(sql)
    connection.commit()
    cur.close()
    connection.close()


def addFunction(functionName, functionDesc, functionParam, output, chainData, code):
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "insert into reusable_function (function_name, description, params, output, on_chain_data, code) " \
          "values ('%s', '%s', '%s', '%s', '%s', '%s')" % (functionName, functionDesc, functionParam, output, chainData, code)
    cur.execute(sql)
    connection.commit()
    cur.close()
    connection.close()


def getAllResInfo():
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "select modifier_id, modifier_name, pattern, description, params, data_names from reusable_modifier"
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    connection.close()
    return res


def getResCode(resId):
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "select code from reusable_modifier where modifier_id = '%s'" % resId
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    connection.close()
    return res


def updateRes(resId, resName, resPattern, resDesc, resParam, chainData, code):
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "update reusable_modifier set modifier_name = '%s', pattern = '%s', description = '%s', params = '%s', " \
          "data_names = '%s', code = '%s' where modifier_id = '%s'" \
          % (resName, resPattern, resDesc, resParam, chainData, code, resId)
    cur.execute(sql)
    connection.commit()
    cur.close()
    connection.close()


def deleteRes(resId):
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "delete from reusable_modifier where modifier_id = '%s'" % resId
    cur.execute(sql)
    connection.commit()
    cur.close()
    connection.close()


def addRes(resName, resPattern, resDesc, resParam, chainData, code):
    connection = connectReusableLib()
    cur = connection.cursor()
    sql = "insert into reusable_modifier (modifier_name, pattern, description, params, data_names, code) " \
          "values ('%s', '%s', '%s', '%s', '%s', '%s')" % (
              resName, resPattern, resDesc, resParam, chainData, code)
    cur.execute(sql)
    connection.commit()
    cur.close()
    connection.close()
