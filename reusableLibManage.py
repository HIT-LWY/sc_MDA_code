import pymysql


def connectReusableLib():
    conn = pymysql.connect(host='localhost', user='root', password='lwy2000712/', database='reuse_lib', charset='utf8')
    return conn


connection = connectReusableLib()


def getAllContract():
    cur = connection.cursor()
    sql = "select contract_id, name, `desc` from contract"
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    return res


def getContractCode(contractId):
    cur = connection.cursor()
    sql = "select code from contract where contract_id = '%s'" % contractId
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    return res[0][0]


def updateContract(contractId, contractName, contractDesc, contractCode):
    cur = connection.cursor()
    sql = "update contract set name='%s', `desc`='%s', code='%s' where contract_id='%s'" % (
        contractName, contractDesc, contractCode, contractId)
    cur.execute(sql)
    connection.commit()
    cur.close()


def addContract(contractName, contractDesc, contractCode):
    cur = connection.cursor()
    sql = "insert into contract (name, `desc`, code) values ('%s','%s','%s')" % (
        contractName, contractDesc, contractCode)
    cur.execute(sql)
    connection.commit()
    cur.close()


def getAllPattern():
    cur = connection.cursor()
    sql = "select process_id, process_name, domain, description, functions from reusable_pattern"
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    return res


def getAllClass():
    cur = connection.cursor()
    sql = "select DISTINCT domain from reusable_pattern where domain IS NOT NULL"
    cur.execute(sql)
    res = cur.fetchall()
    return res


def updatePattern(patternId, patternName, patternDomain, patternDesc, patternFunctions):
    cur = connection.cursor()
    sql = "update reusable_pattern set process_name = '%s', domain = '%s', description = '%s', " \
          "functions = '%s' where process_id = '%s'" \
          % (patternName, patternDomain, patternDesc, patternFunctions, patternId)
    cur.execute(sql)
    connection.commit()
    cur.close()


def deletePattern(patternId):
    cur = connection.cursor()
    sql = "delete from reusable_pattern where process_id = '%s'" % patternId
    cur.execute(sql)
    connection.commit()
    cur.close()
