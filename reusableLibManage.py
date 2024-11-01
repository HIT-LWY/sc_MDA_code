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
