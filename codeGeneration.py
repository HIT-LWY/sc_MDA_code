import ast

import pymysql

# 生成的代码内容
# 合约信息（合约名、合约注释、继承关系）
from nlp import serviceSelectionByProcess, serviceSelectionByFunction, selectMatchData, serviceSelectionByModifier

# 合约的函数
contractFunction = ""
# 合约的约束
contractModifier = ""

tab = '    '
contractName = ""
contractAnnotation = ""
contractClauses = ""
contractParties = ""
contractAllData = ''
# 为了避免重复生成modifier和function，需要添加标识
allModifierFlag = {}
allFunctionFlag = {}
allEventFlag = {}


def GenerateContractInfo():
    global contractName
    global contractAnnotation
    global contractClauses
    global contractParties
    global contractAllData
    conInfo = selectContractInfo()
    contractName = conInfo[0][0]
    contractAnnotation = conInfo[0][1]
    contractClauses = conInfo[0][2]
    contractParties = conInfo[0][3]
    contractAllData = conInfo[0][4]
    contractInfo = "//" + contractAnnotation + "\n" + "contract " + contractName + " "
    return contractInfo


# 生成合约链上的数据
def GenerateContractData():
    global contractAllData
    allDataList = contractAllData.strip('[').strip(']').split(',')
    contractVariable = ""
    for d in allDataList:
        variableInfo = selectOnchainData(d)
        # 筛选出非参数的数据，即变量
        if len(variableInfo) != 0:
            # (('int', 'public', '0', 'false', '0','[a,b,c]'),)
            # uint256 ifNotice = 0;
            if variableInfo[0][0] == 'struct':
                contractVariable += 'struct ' + d + '{\n\t'
                contentList = variableInfo[0][5].strip('[').strip(']').split(',')
                for c in contentList:
                    contractVariable += c + ';\n\t'
                contractVariable = contractVariable[:-1]
                contractVariable += '}\n'
            else:
                contractVariable += variableInfo[0][0] + " " + variableInfo[0][1] + " "
                if variableInfo[0][3] == 'true':
                    contractVariable += 'constant ' + d + ' '
                else:
                    contractVariable += d + ' '
                if variableInfo[0][4] == '0':
                    if variableInfo[0][2] != 'null':
                        contractVariable += '= ' + variableInfo[0][2]
                else:
                    contractVariable += '= ' + variableInfo[0][4]
                contractVariable += ';\n'
    # 合约方的地址生成
    addrParty = contractParties.strip('[').strip(']').split(',')
    # print(addrParty) ['name1', 'name2']
    rolesList = []
    for p in addrParty:
        roles = selectParty(p)
        for r in roles:
            # print(r) ('[tenant]',)
            rlist = r[0].strip('[').strip(']').split(',')
            for rl in rlist:
                if rl in rolesList:
                    pass
                else:
                    rolesList.append(rl)
    # print(rolesList) ['tenant', 'landlord']
    for role in rolesList:
        contractVariable += 'address ' + role + ';\n'
        # 生成角色地址的函数
        contractVariable += 'function set_' + role + '_address(address newAddr) public {\n' + tab + 'require(' \
                                                                                                    'msg.sender ==' \
                                                                                                    ' ' + role + \
                            ');\n' + tab + role + ' = newAddr;\n}\n'
        # 生成对角色检查的modifier
        contractVariable += 'modifier check_' + role + '(){\n' + tab + 'require(msg.sender == ' + role + ');\n' \
                            + tab + '_;\n}\n'
    return contractVariable


def AddFlagsForLMF():
    global allModifierFlag
    global allFunctionFlag
    global allEventFlag
    clausesList = contractClauses.strip('[').strip(']').split(',')
    for clause in clausesList:
        activities = selectActivityByClause(clause)
        processList = activities[0][0].strip('[').strip(']').split(',')
        for p in processList:
            process = selectProcessByName(p)
            pro_function = process[0][1]
            pro_functionList = pro_function.strip('[').strip(']').split(',')
            for fun in pro_functionList:
                if fun in allFunctionFlag:
                    pass
                else:
                    allFunctionFlag[fun] = False
                res = selectResByFuncName(fun)
                # print(res)
                if res[0][0] != 'null':
                    res_list = eval(res[0][0].strip('\"'))
                    for r in res_list:
                        if r in allModifierFlag:
                            pass
                        else:
                            allModifierFlag[r] = False
                logs = selectLogByFuncName(fun)
                # print(logs)
                if logs[0][0] != 'null':
                    logs_list = logs[0][0].strip('[').strip(']').split(',')
                    for log in logs_list:
                        if log not in allEventFlag:
                            allEventFlag[log] = False


def GenerateLog():
    global contractClauses
    clausesList = contractClauses.strip('[').strip(']').split(',')
    contractEvent = ""
    for clause in clausesList:
        activities = selectActivityByClause(clause)
        processList = activities[0][0].strip('[').strip(']').split(',')
        for p in processList:
            process = selectProcessByName(p)
            pro_function_list = process[0][1].strip('[').strip(']').split(',')
            for f in pro_function_list:
                events = selectLogByFuncName(f)
                if events[0][0] != 'null':
                    eventsList = events[0][0].strip('[').strip(']').split(',')
                    for e in eventsList:
                        if not allEventFlag[e]:
                            currentEvent = 'event ' + e + '('
                            logInfo = selectLogInfoByName(e)
                            if logInfo[0][0] != 'null':
                                param = ""
                                logParams = logInfo[0][0].strip('[').strip(']').split(',')
                                for lp in logParams:
                                    param += lp + ', '
                                param = param.strip(' ').strip(',')
                                currentEvent += param + ');\n\n'
                            else:
                                currentEvent += ');\n\n'
                            contractEvent += currentEvent
                            allEventFlag[e] = True
    return contractEvent


# 生成代码
def codeGenerate():
    # global contractInfo
    # global contractVariable
    global contractFunction
    global contractModifier
    # global contractEvent
    # conInfo = selectContractInfo()
    # contractName = conInfo[0][0]
    # contractAnnotation = conInfo[0][1]
    # contractClauses = conInfo[0][2]
    # contractParties = conInfo[0][3]
    # 链上和链下数据
    # contractAllData = conInfo[0][4]
    # 生成合约的最外框的合约描述和合约名字
    # contractInfo += "//" + contractAnnotation + "\n" + "contract " + contractName + " "
    # 合约数据的生成
    # allDataList = contractAllData.strip('[').strip(']').split(',')
    # ['ifAgreeRenew', 'renewalTime', 'duration', 'advanceNoticetime', 'ifNotice']
    # for d in allDataList:
    #     variableInfo = selectOnchainData(d)
    #     # 筛选出非参数的数据，即变量
    #     if len(variableInfo) != 0:
    #         # print(variableInfo)
    #         # (('int', 'public', '0', 'false', '0','[a,b,c]'),)
    #         # uint256 ifNotice = 0;
    #         if variableInfo[0][0] == 'struct':
    #             contractVariable += 'struct ' + d + '{\n\t'
    #             contentList = variableInfo[0][5].strip('[').strip(']').split(',')
    #             for c in contentList:
    #                 contractVariable += c + ';\n\t'
    #             contractVariable = contractVariable[:-1]
    #             contractVariable += '}\n'
    #         else:
    #             contractVariable += variableInfo[0][0] + " " + variableInfo[0][1] + " "
    #             if variableInfo[0][3] == 'true':
    #                 contractVariable += 'constant ' + d + ' '
    #             else:
    #                 contractVariable += d + ' '
    #             if variableInfo[0][4] == '0':
    #                 if variableInfo[0][2] != 'null':
    #                     contractVariable += '= ' + variableInfo[0][2]
    #             else:
    #                 contractVariable += '= ' + variableInfo[0][4]
    #             contractVariable += ';\n'
    # print(contractVariable)
    # 合约方的地址生成
    # addrParty = contractParties.strip('[').strip(']').split(',')
    # # print(addrParty) ['name1', 'name2']
    # rolesList = []
    # for p in addrParty:
    #     roles = selectParty(p)
    #     for r in roles:
    #         # print(r) ('[tenant]',)
    #         rlist = r[0].strip('[').strip(']').split(',')
    #         for rl in rlist:
    #             if rl in rolesList:
    #                 pass
    #             else:
    #                 rolesList.append(rl)
    # # print(rolesList) ['tenant', 'landlord']
    # for role in rolesList:
    #     contractVariable += 'address ' + role + ';\n'
    #     # 生成角色地址的函数
    #     contractFunction += 'function set_' + role + '_address(address newAddr) public {\n' + tab + 'require(' \
    #                                                                                                 'msg.sender ==' \
    #                                                                                                 ' ' + role + \
    #                         ');\n' + tab + role + ' = newAddr;\n}\n'
    #     # 生成对角色检查的modifier
    #     contractModifier += 'modifier check_' + role + '(){\n' + tab + 'require(msg.sender == ' + role + ');\n' \
    #                         + tab + '_;\n}\n'
    # 不需要复用库的部分已经生成结束，下面遍历条款内容
    # allModifierFlag = {}
    # allFunctionFlag = {}
    # allEventFlag = {}
    # for clause in clausesList:
    #     activities = selectActivityByClause(clause)
    #     processList = activities[0][0].strip('[').strip(']').split(',')
    #     for p in processList:
    #         process = selectProcessByName(p)
    #         pro_function = process[0][1]
    #         pro_functionList = pro_function.strip('[').strip(']').split(',')
    #         for fun in pro_functionList:
    #             if fun in allFunctionFlag:
    #                 pass
    #             else:
    #                 allFunctionFlag[fun] = False
    #             res = selectResByFuncName(fun)
    #             # print(res)
    #             if res[0][0] != 'null':
    #                 res_list = eval(res[0][0].strip('\"'))
    #                 for r in res_list:
    #                     if r in allModifierFlag:
    #                         pass
    #                     else:
    #                         allModifierFlag[r] = False
    #             logs = selectLogByFuncName(fun)
    #             # print(logs)
    #             if logs[0][0] != 'null':
    #                 logs_list = logs[0][0].strip('[').strip(']').split(',')
    #                 for log in logs_list:
    #                     if log not in allEventFlag:
    #                         allEventFlag[log] = False
    # 生成所有的event
    # for clause in clausesList:
    #     activities = selectActivityByClause(clause)
    #     processList = activities[0][0].strip('[').strip(']').split(',')
    #     for p in processList:
    #         process = selectProcessByName(p)
    #         pro_function_list = process[0][1].strip('[').strip(']').split(',')
    #         for f in pro_function_list:
    #             events = selectLogByFuncName(f)
    #             if events[0][0] != 'null':
    #                 eventsList = events[0][0].strip('[').strip(']').split(',')
    #                 for e in eventsList:
    #                     currentEvent = 'event ' + e + '('
    #                     logInfo = selectLogInfoByName(e)
    #                     if logInfo[0][0] != 'null':
    #                         param = ""
    #                         logParams = logInfo[0][0].strip('[').strip(']').split(',')
    #                         for lp in logParams:
    #                             param += lp + ', '
    #                         param = param.strip(' ').strip(',')
    #                         currentEvent += param + ');\n\n'
    #                     else:
    #                         currentEvent += ');\n\n'
    #                     contractEvent += currentEvent
    clausesList = contractClauses.strip('[').strip(']').split(',')
    for clause in clausesList:
        activities = selectActivityByClause(clause)
        # 每一个条款中包含的流程，也就是activity
        processList = activities[0][0].strip('[').strip(']').split(',')
        for p in processList:
            # 只会返回一个process
            process = selectProcessByName(p)
            pro_desc = process[0][0]
            pro_function = process[0][1]
            pro_functionList = pro_function.strip('[').strip(']').split(',')
            pro_functionsNum = len(pro_functionList)
            # 匹配约束，函数关联约束，约束匹配约束
            allModifierInProcess = []
            for func in pro_functionList:
                res = selectResByFuncName(func)
                if res[0][0] != 'null':
                    res_list = eval(res[0][0].strip('\"'))
                    for r in res_list:
                        if r not in allModifierInProcess:
                            allModifierInProcess.append(r)
            # print(allModifierInProcess)
            # 约束的生成
            for m in allModifierInProcess:
                modifierDeclaration = ""
                paramStringModi = ""
                if not allModifierFlag[m]:
                    allModifierFlag[m] = True
                    modifierInfo = selectResInfoByName(m)
                    modi_description = modifierInfo[0][0]
                    modi_data = modifierInfo[0][1]
                    modi_param = modifierInfo[0][2]
                    modifierDeclaration += 'modifier ' + m
                    if modi_param != 'null':
                        modi_param_list = eval(modi_param.strip('\"'))
                        for mp in modi_param_list:
                            paramType = selectTypeByParamName(mp)
                            paramStringModi += paramType[0][0] + ' ' + mp + ', '
                    paramStringModi = paramStringModi.strip(' ').strip(',')
                    modifierDeclaration += '(' + paramStringModi + ')' + '{\n'
                    # 根据语义进行匹配
                    matchModifierList = serviceSelectionByModifier(modi_description)
                    modifier_flag = False
                    successModifierId = 0
                    # m 是PIM中的Modifier
                    for matchId in matchModifierList:
                        # 检查
                        modifierInLib = selectModifierById(matchId)
                        modifierInLib_params = modifierInLib[0][0]
                        modifierInLib_data = modifierInLib[0][1]
                        if modifierInLib_params != 'null' and modi_param != 'null':
                            modifierInLib_params_list = modifierInLib_params.strip('[').strip(']').split(',')
                            if len(modifierInLib_params_list) != len(eval(modi_param.strip('\"'))):
                                continue
                        else:
                            if modi_param != 'null':
                                continue
                        # 检查关联数据个数是否一致
                        if modifierInLib_data != 'null' and modi_data != 'null':
                            modifierInLib_data_list = modifierInLib_data.strip('[').strip(']').split(',')
                            if len(modifierInLib_data_list) != len(eval(modi_data.strip('\"'))):
                                continue
                        else:
                            if modi_data != 'null':
                                continue
                        modifier_flag = True
                        successModifierId += matchId
                        break
                    # 匹配成功
                    if modifier_flag:
                        modifierInLib = selectModifierById(successModifierId)
                        modifierInLib_params = modifierInLib[0][0]
                        modifierInLib_data = modifierInLib[0][1]
                        modifierInLib_code = modifierInLib[0][2]
                        middleCode = modifierInLib_code
                        # 开始替换参数
                        if modifierInLib_params != 'null':
                            for param in modifierInLib_params.strip('[').strip(']').split(','):
                                paramInfo = selectParamByNameInLib(param)
                                # (('The length of the renewal', 'int'),)
                                param_Desc = paramInfo[0][0]
                                param_Type = paramInfo[0][1]
                                matchParam = []
                                matchParamDesc = []
                                modi_param_list = eval(modi_param.strip('\"'))
                                for pim_param in modi_param_list:
                                    param_pim = selectParam(pim_param)
                                    param_pim_type = param_pim[0][0]
                                    param_pim_desc = param_pim[0][1]
                                    if param_pim_type == param_Type:
                                        matchParam.append(pim_param)
                                        matchParamDesc.append(param_pim_desc)
                                if len(matchParam) == 1:
                                    if param == matchParam[0]:
                                        middleCode = modifierInLib_code
                                    else:
                                        middleCode = replaceDataName(middleCode, param, matchParam[0])
                                elif len(matchParam) > 1:
                                    paramIndex = selectMatchData(param_Desc, matchParamDesc)
                                    paramName = matchParam[paramIndex]
                                    middleCode = modifierInLib_code
                                    middleCode = replaceDataName(middleCode, param, paramName)
                        if modifierInLib_data != 'null':
                            for reuse_data in modifierInLib_data.strip('[').strip(']').split(','):
                                reuse_data_info = selectDataByNameInLib(reuse_data)
                                # print(reuse_data_info)
                                # print(reuse_data)
                                data_Desc = reuse_data_info[0][0]
                                data_Type = reuse_data_info[0][1]
                                matchData = []
                                matchDataDesc = []
                                modi_data_list = eval(modi_data.strip('\"'))
                                for pim_data in modi_data_list:
                                    data_pim = selectDataTypeAndDescByName(pim_data)
                                    data_pim_type = data_pim[0][0]
                                    data_pim_desc = data_pim[0][1]
                                    if data_pim_type == data_Type:
                                        matchData.append(pim_data)
                                        matchDataDesc.append(data_pim_desc)
                                if len(matchData) == 1:
                                    if reuse_data == matchData[0]:
                                        pass
                                    else:
                                        middleCode = replaceDataName(middleCode, reuse_data, matchData[0])
                                elif len(matchData) > 1:
                                    dataIndex = selectMatchData(data_Desc, matchDataDesc)
                                    dataName = matchData[dataIndex]
                                    middleCode = replaceDataName(middleCode, reuse_data, dataName)
                        # 约束的数据替换结束
                        middleCode = tab + middleCode.replace('\n', '\n' + tab) + '\n' + tab + '_;\n' + '}\n'
                        currentModifier = modifierDeclaration + middleCode
                        # print(middleCode)
                        contractModifier += currentModifier
            # 计算关联的数据的个数
            allDataInAllFunctionList = []
            allModifier = []
            for func in pro_functionList:
                # (("['autoRenewTime', 'duration']",),)
                allDataInFunction = selectFunctionDataByName(func)
                # ['autoRenewTime', 'duration']
                if allDataInFunction[0][0] != 'null':
                    allDataInFunctionList = eval(allDataInFunction[0][0].strip('\"'))
                    for a in allDataInFunctionList:
                        if a in allDataInAllFunctionList:
                            pass
                        else:
                            allDataInAllFunctionList.append(a)
                # 计算约束中的数据 (("['checkNotice', 'validity']",),)
                allModifierInFunction = selectResByFuncName(func)
                # print(allModifierInFunction)
                if allModifierInFunction[0][0] != 'null':
                    allModifierInFunctionList = eval(allModifierInFunction[0][0].strip('\"'))
                    for aM in allModifierInFunctionList:
                        if aM in allModifier:
                            pass
                        else:
                            allModifier.append(aM)
            # print(allModifier)
            for modifier in allModifier:
                # (("['signDate', 'duration', 'advanceNoticeTime']",),)
                allModifierData = selectResDataByName(modifier)
                allModifierDataList = eval(allModifierData[0][0].strip('\"'))
                # print(allModifierDataList)
                for aMd in allModifierDataList:
                    if aMd in allDataInAllFunctionList:
                        pass
                    else:
                        allDataInAllFunctionList.append(aMd)
            allFunctionDataNum = len(allDataInAllFunctionList)
            # print(allDataInAllFunctionList)
            # 计算输入的数据的个数
            allParamInAllFunctionList = []
            for func in pro_functionList:
                allParamInFunction = selectFunctionParamByName(func)
                if allParamInFunction[0][0] != 'null':
                    allParamInFunctionList = eval(allParamInFunction[0][0].strip('\"'))
                    for ap in allParamInFunctionList:
                        if ap in allParamInAllFunctionList:
                            pass
                        else:
                            allParamInAllFunctionList.append(ap)
            allFunctionParamNum = len(allParamInAllFunctionList)
            # print(allParamInAllFunctionList)
            # 返回阈值大于0.55的列表,降序
            matchProcessList = serviceSelectionByProcess(pro_desc)
            # 是否匹配成功
            flag = False
            successProcessId = 0
            # matchProcess 是流程的id
            for matchProcess in matchProcessList:
                # 只会返回一个
                r_processInfo = selectProcessInLibById(matchProcess)
                # on_chain_data, input, output, call_id, atomic_service, participants
                r_relatedData = r_processInfo[0][0]
                r_relatedInput = r_processInfo[0][1]
                # 暂时不检查流程的输出
                r_relatedCall = r_processInfo[0][3]
                r_functions = r_processInfo[0][4]
                # 检查数据个数是否一致
                r_relatedDataList = r_relatedData.strip('[').strip(']').split(',')
                if len(r_relatedDataList) != allFunctionDataNum:
                    # print(r_relatedDataList)
                    # print(allFunctionDataNum)
                    continue
                # 检查函数个数是否一致
                r_functionsList = r_functions.strip('[').strip(']').split(',')
                if len(r_functionsList) != pro_functionsNum:
                    continue
                # 检查参数个数是否一致
                r_relatedInputList = r_relatedInput.strip('[').strip(']').split(',')
                if len(r_relatedInputList) != allFunctionParamNum:
                    continue
                # 匹配成功
                flag = True
                successProcessId = matchProcess
                break
            # 流程匹配成功
            if flag:
                reuse_functions = selectAtomicService(successProcessId)
                reuseFunctionsList = reuse_functions[0][0].strip('[').strip(']').split(',')
                # 无需检查直接匹配，然后数据替换即可 pro_functionList
                # 获取流程下pro_functionList函数的所有描述构成一句话
                pimFunctionDesc = []
                for f in pro_functionList:
                    pim_desc = selectDescByName(f)
                    pim_desc_content = pim_desc[0][0]
                    pimFunctionDesc.append(pim_desc_content)
                # 流程中的全部函数
                for rF in reuseFunctionsList:
                    reuse = selectDescInLibByName(rF)
                    reuse_desc = reuse[0][0]
                    reuse_params = reuse[0][1]
                    reuse_output = reuse[0][2]
                    reuse_call_service = reuse[0][3]
                    reuse_data = reuse[0][4]
                    reuse_lib = reuse[0][5]
                    reuse_code = reuse[0][6]
                    # 匹配，返回最高值的pimFunctionDesc索引
                    func_index = selectMatchData(reuse_desc, pimFunctionDesc)
                    # 匹配成功返回的函数名字
                    matchFunctionName = pro_functionList[func_index]
                    if not allFunctionFlag[matchFunctionName]:
                        allFunctionFlag[matchFunctionName] = True
                        # 根据函数名获取全部的PIM函数信息
                        pim_func = selectAllFunctionInfoByName(matchFunctionName)
                        pim_desc = pim_func[0][0]
                        pim_modi = pim_func[0][1]
                        pim_right = pim_func[0][2]
                        pim_ifConstructor = pim_func[0][3]
                        pim_ifUpdateData = pim_func[0][4]
                        pim_ifGenerateTransaction = pim_func[0][5]
                        pim_dataNames = pim_func[0][6]
                        pim_param = pim_func[0][7]
                        pim_logs = pim_func[0][8]
                        pim_output = pim_func[0][9]
                        paramString = ""
                        modifier = ""
                        right = ""
                        ifUpdateData = ""
                        returns = ""
                        ifGenerateTransaction = ""
                        # 获取流程中的函数全部信息
                        functionDeclaration = ""
                        middleCode = reuse_code
                        # 生成函数的声明部分
                        if pim_param != 'null':
                            func_param_list = eval(pim_param.strip('\"'))
                            for funcParam in func_param_list:
                                paramType = selectTypeByParamName(funcParam)
                                paramString += paramType[0][0] + ' ' + funcParam + ', '
                        paramString = paramString.strip(' ').strip(',')
                        # 约束
                        if pim_modi != 'null':
                            func_modi_list = eval(pim_modi.strip('\"'))
                            for funcModi in func_modi_list:
                                modifier += funcModi + ' '
                        # 角色权限
                        if pim_right != 'null':
                            func_right_list = pim_right.strip('[').strip(']').split(',')
                            if len(func_right_list) == 1:
                                if " and " in func_right_list[0]:
                                    func_right_list = func_right_list[0].split(" ")
                                    func_right_list.remove("and")
                                    for funcRight in func_right_list:
                                        right += 'check_' + funcRight + ' '
                                else:
                                    right += 'check_' + func_right_list[0] + ' '
                            else:
                                right = 'check_'
                                for funcRight in func_right_list:
                                    right += funcRight + '_'
                                right = right[:-1]
                                right += ' '
                        if pim_ifConstructor == 'false':
                            ifUpdateData = " view"
                        if pim_ifGenerateTransaction == 'true':
                            ifGenerateTransaction = " payable"
                        # 函数返回值
                        if pim_output != 'null':
                            func_output_list = pim_output.strip('[').strip(']').split(',')
                            for re in func_output_list:
                                returns += re + ', '
                        returns = returns[:-2]
                        if pim_ifConstructor == 'false':
                            functionDeclaration += 'function ' + matchFunctionName + '(' + paramString + ') public ' + \
                                                   ifUpdateData + ifGenerateTransaction + ' ' + modifier + right + \
                                                   'returns ' + '(' + returns + ') ' + '{\n'
                        else:
                            functionDeclaration += 'constructor' + '(' + paramString + ')' + '{\n'
                        functionDeclaration = functionDeclaration.replace('returns () ', '')
                        if reuse_params != 'null':
                            for param in reuse_params.strip('[').strip(']').split(','):
                                paramInfo = selectParamByNameInLib(param)
                                param_Desc = paramInfo[0][0]
                                param_Type = paramInfo[0][1]
                                matchParam = []
                                matchParamDesc = []
                                func_param_list = eval(pim_param.strip('\"'))
                                for paramInPim in func_param_list:
                                    param_pim = selectParam(paramInPim)
                                    param_pim_type = param_pim[0][0]
                                    param_pim_desc = param_pim[0][1]
                                    if param_pim_type == param_Type:
                                        matchParam.append(paramInPim)
                                        matchParamDesc.append(param_pim_desc)
                                # print(matchParam)
                                if len(matchParam) == 1:
                                    if param == matchParam[0]:
                                        middleCode = reuse_code
                                    else:
                                        middleCode = reuse_code
                                        middleCode = replaceDataName(middleCode, param, matchParam[0])
                                elif len(matchParam) > 1:
                                    paramIndex = selectMatchData(param_Desc, matchParamDesc)
                                    paramName = matchParam[paramIndex]
                                    middleCode = reuse_code
                                    middleCode = replaceDataName(middleCode, param, paramName)
                        if reuse_data != 'null':
                            for r_data in reuse_data.strip('[').strip(']').split(','):
                                reuse_data_info = selectDataByNameInLib(r_data)
                                data_Desc = reuse_data_info[0][0]
                                data_Type = reuse_data_info[0][1]
                                matchData = []
                                matchDataDesc = []
                                for pim_data in eval(pim_dataNames.strip('\"')):
                                    data_pim = selectDataTypeAndDescByName(pim_data)
                                    data_pim_type = data_pim[0][0]
                                    data_pim_desc = data_pim[0][1]
                                    if data_pim_type == data_Type:
                                        matchData.append(pim_data)
                                        matchDataDesc.append(data_pim_desc)
                                if len(matchData) == 1:
                                    if reuse_data == matchData[0]:
                                        pass
                                    else:
                                        middleCode = replaceDataName(middleCode, reuse_data, matchData[0])
                                elif len(matchData) > 1:
                                    dataIndex = selectMatchData(data_Desc, matchDataDesc)
                                    dataName = matchData[dataIndex]
                                    middleCode = replaceDataName(middleCode, reuse_data, dataName)
                        # 数据替换结束，在匹配成功的情况下，继续生成代码，middle为中间生成的函数体
                        middleCode = tab + middleCode.replace('\n', '\n' + tab)
                        functionBody = middleCode + '\n}\n'
                        currentFunction = functionDeclaration + functionBody
                        contractFunction += currentFunction
                # print(contractFunction)
            else:
                # 流程匹配失败，启动对函数的匹配
                # 获取PIM下的所有函数
                for functionName in pro_functionList:
                    # print(allFunctionFlag)
                    if not allFunctionFlag[functionName]:
                        allFunctionFlag[functionName] = True
                        functionInfo = selectAllFunctionInfoByName(functionName)
                        func_desc = functionInfo[0][0]
                        func_modi = functionInfo[0][1]
                        func_right = functionInfo[0][2]
                        func_ifConstructor = functionInfo[0][3]
                        func_ifUpdateData = functionInfo[0][4]
                        func_ifGenerateTransaction = functionInfo[0][5]
                        func_dataNames = functionInfo[0][6]
                        func_param = functionInfo[0][7]
                        func_logs = functionInfo[0][8]
                        func_output = functionInfo[0][9]
                        # 生成函数的声明部分
                        functionDeclaration = ""
                        paramString = ""
                        ifUpdateData = ""
                        ifGenerateTransaction = ""
                        modifier = ""
                        right = ""
                        returns = ""
                        # 函数体
                        functionBody = ""
                        # 获取参数信息
                        if func_param != 'null':
                            func_param_list = eval(func_param.strip('\"'))
                            for funcParam in func_param_list:
                                paramType = selectTypeByParamName(funcParam)
                                paramString += paramType[0][0] + ' ' + funcParam + ', '
                        paramString = paramString.strip(' ').strip(',')
                        # 获取该函数的约束内容
                        if func_modi != 'null':
                            func_modi_list = eval(func_modi.strip('\"'))
                            for funcModi in func_modi_list:
                                modifier += funcModi + ' '
                        # 角色权限
                        if func_right != 'null':
                            func_right_list = func_right.strip('[').strip(']').split(',')
                            if len(func_right_list) == 1:
                                if " and " in func_right_list[0]:
                                    func_right_list = func_right_list[0].split(" ")
                                    func_right_list.remove("and")
                                    for funcRight in func_right_list:
                                        right += 'check_' + funcRight + ' '
                                else:
                                    right += 'check_' + func_right_list[0] + ' '
                            else:
                                right = 'check_'
                                for funcRight in func_right_list:
                                    right += funcRight + '_'
                                right = right[:-1]
                                right += ' '
                        if func_ifUpdateData == 'false':
                            ifUpdateData = " view"
                        if func_ifGenerateTransaction == 'true':
                            ifGenerateTransaction = " payable"
                        # 函数返回值
                        if func_output != 'null':
                            func_output_list = func_output.strip('[').strip(']').split(',')
                            for re in func_output_list:
                                returns += re + ', '
                        returns = returns[:-2]
                        if func_ifConstructor == 'false':
                            functionDeclaration += 'function ' + functionName + '(' + paramString + ') public ' + \
                                                   ifUpdateData + ifGenerateTransaction + ' ' + modifier + right + \
                                                   'returns ' + '(' + returns + ') ' + '{\n'
                        else:
                            functionDeclaration += 'constructor' + '(' + paramString + ')' + '{\n'
                        functionDeclaration = functionDeclaration.replace('returns () ', '')
                        # 根据语义匹配生成函数体
                        # 在复用库中匹配到合适的函数
                        matchFunctionList = serviceSelectionByFunction(func_desc)
                        # print(matchFunctionList)
                        # 匹配是否成功以及成功的复用库中函数的id
                        func_flag = False
                        successFunctionId = 0
                        for matchId in matchFunctionList:
                            # 检查
                            functionInLib = selectFunctionInLibById(matchId)
                            # (('null', 'null', 'null', 'ifAgreeFinish', 'null'),)
                            functionInLib_params = functionInLib[0][0]
                            functionInLib_output = functionInLib[0][1]
                            functionInLib_data = functionInLib[0][3]
                            # 检查参数是否一致
                            if functionInLib_params != 'null' and func_param != 'null':
                                functionInLib_params_list = functionInLib_params.strip('[').strip(']').split(',')
                                if len(functionInLib_params_list) != len(eval(func_param.strip('\"'))):
                                    continue
                            else:
                                if func_param != 'null':
                                    continue
                            # 检查返回值个数是否一致
                            if functionInLib_output != 'null' and func_output != 'null':
                                functionInLib_output_list = functionInLib_output.strip('[').strip(']').split(',')
                                if len(functionInLib_output_list) != len(func_output.strip('[').strip(']').split(',')):
                                    continue
                            else:
                                if func_output != 'null':
                                    continue
                            # 检查关联的数据个数是否一致
                            if functionInLib_data != 'null' and func_dataNames != 'null':
                                functionInLib_data_list = functionInLib_data.strip('[').strip(']').split(',')
                                func_data_list = eval(func_dataNames.strip('\"'))
                                if len(functionInLib_data_list) != len(func_data_list):
                                    continue
                            else:
                                if func_dataNames != 'null':
                                    continue
                            func_flag = True
                            successFunctionId += matchId
                            break
                        # print(successFunctionId) 匹配成功开始匹配数据，然后生成代码
                        if func_flag:
                            functionInLib = selectFunctionInLibById(successFunctionId)
                            # (('null', 'null', 'null', 'ifAgreeFinish', 'null'),)
                            functionInLib_params = functionInLib[0][0]
                            functionInLib_output = functionInLib[0][1]
                            functionInLib_call_service = functionInLib[0][2]
                            functionInLib_data = functionInLib[0][3]
                            functionInLib_external_lib = functionInLib[0][4]
                            functionInLib_code = functionInLib[0][5]
                            # 需要替换两次，第一次将code中的参数替换，第二次将code中的数据替换，所以需要一个中间代码变量
                            # 这个位置不是+=，因为一次循环里只产生一个middleCode
                            middleCode = functionInLib_code
                            # 查询参数的描述，匹配参数
                            # print(functionInLib_code)
                            if functionInLib_params != 'null':
                                for param in functionInLib_params.strip('[').strip(']').split(','):
                                    # 先匹配类型，如果类型只有一个相对应，就直接替换。有多个的话，再进行语义匹配，减少匹配的数量，提高精准度。
                                    paramInfo = selectParamByNameInLib(param)
                                    # (('The length of the renewal', 'int'),)
                                    param_Desc = paramInfo[0][0]
                                    param_Type = paramInfo[0][1]
                                    matchParam = []
                                    matchParamDesc = []
                                    # PIM函数中的参数
                                    func_param_list = eval(func_param.strip('\"'))
                                    for pim_param in func_param_list:
                                        # 查询类型和描述
                                        param_pim = selectParam(pim_param)
                                        param_pim_type = param_pim[0][0]
                                        param_pim_desc = param_pim[0][1]
                                        if param_pim_type == param_Type:
                                            matchParam.append(pim_param)
                                            matchParamDesc.append(param_pim_desc)
                                    if len(matchParam) == 1:
                                        # 只有一个类型对应的上的情况下就不需要匹配了 lib：param； PIM ：matchParam[0]
                                        if param == matchParam[0]:
                                            middleCode = functionInLib_code
                                        else:
                                            # 替换逻辑
                                            middleCode = functionInLib_code
                                            middleCode = replaceDataName(middleCode, param, matchParam[0])
                                    elif len(matchParam) > 1:
                                        # 需要进行匹配 lib：param_Desc，单句； Pim：matchParamDesc ；列表
                                        paramIndex = selectMatchData(param_Desc, matchParamDesc)
                                        paramName = matchParam[paramIndex]
                                        middleCode = functionInLib_code
                                        middleCode = replaceDataName(middleCode, param, paramName)
                            if functionInLib_data != 'null':
                                for reuse_data in functionInLib_data.strip('[').strip(']').split(','):
                                    # 匹配类型
                                    reuse_data_info = selectDataByNameInLib(reuse_data)
                                    data_Desc = reuse_data_info[0][0]
                                    data_Type = reuse_data_info[0][1]
                                    matchData = []
                                    matchDataDesc = []
                                    # PIM中的函数列表
                                    func_data_list = eval(func_dataNames.strip('\"'))
                                    for pim_data in func_data_list:
                                        # 查询类型和描述
                                        data_pim = selectDataTypeAndDescByName(pim_data)
                                        data_pim_type = data_pim[0][0]
                                        data_pim_desc = data_pim[0][1]
                                        if data_pim_type == data_Type:
                                            matchData.append(pim_data)
                                            matchDataDesc.append(data_pim_desc)
                                    if len(matchData) == 1:
                                        if reuse_data == matchData[0]:
                                            pass
                                        else:
                                            middleCode = replaceDataName(middleCode, reuse_data, matchData[0])
                                    elif len(matchData) > 1:
                                        dataIndex = selectMatchData(data_Desc, matchDataDesc)
                                        dataName = matchData[dataIndex]
                                        middleCode = replaceDataName(middleCode, reuse_data, dataName)
                            # 数据替换结束，在匹配成功的情况下，继续生成代码，middle为中间生成的函数体
                            middleCode = tab + middleCode.replace('\n', '\n' + tab)
                            functionBody = middleCode + '\n}\n'
                            currentFunction = functionDeclaration + functionBody
                            contractFunction += currentFunction
                            # print("currentFunction")
                        else:
                            # 流程匹配失败，函数匹配失败，TODO 空洞补全
                            pass
                # 外层输出的函数内容，流程匹配失败，对函数的匹配的代码生成结果
                # print(contractFunction)


# 对代码进行数据替换
def replaceDataName(code, reuseName, pimName):
    while reuseName in code:
        i = code.find(reuseName)
        # 当找到第一个匹配的子串时，判断其前后是否都不为字母
        if (i == 0 or not code[i - 1].isalpha()) and \
                (i + len(reuseName) == len(code) or not code[i + len(reuseName)].isalpha()):
            # 如果符合条件，使用切片和加法运算符完成替换
            return code[:i] + pimName + code[i + len(reuseName):]
    return code


# 组装生成的结果，输出到文件
def outputCode():
    contractInfo = GenerateContractInfo()
    contractVariable = GenerateContractData()
    contractEvent = GenerateLog()
    global contractFunction
    global contractModifier
    # global contractEvent
    contractVariable = tab + contractVariable.replace('\n', '\n' + tab)
    contractModifier = tab + contractModifier.replace('\n', '\n' + tab)
    contractFunction = tab + contractFunction.replace('\n', '\n' + tab)
    contractEvent = tab + contractEvent.replace('\n', '\n' + tab)
    code = contractInfo + ' {\n' + contractVariable + '\n' + contractModifier + '\n' + \
           contractFunction + '\n' + contractEvent + '\n}'
    Note = open('code_result/licencePSM.sol', mode='a')
    Note.seek(0)
    Note.truncate()
    Note.write(code)


def connectDB():
    conn = pymysql.connect(host='localhost', user='root', password='lwy2000712/', database='mda', charset='utf8')
    return conn


def connectReusableLib():
    conn = pymysql.connect(host='localhost', user='root', password='lwy2000712/', database='reuse_lib', charset='utf8')
    return conn


# 查找合约信息
# 当前是为了测试，所以查询一个合约，数据库中也只有一个，后续可以传入id查询
def selectContractInfo():
    conn = connectDB()
    cur = conn.cursor()
    sql = "select name, annotation, clauses, participants, data from smart_contract"
    cur.execute(sql)
    conInfo = cur.fetchall()
    cur.close()
    conn.close()
    return conInfo


# 根据数据名查找数据
def selectOnchainData(name):
    conn = connectDB()
    cur = conn.cursor()
    sql = "select type, visibility, value, ifConstant, unix_date, allTypeName from contract_data where name = '%s'" % name
    cur.execute(sql)
    dataInfo = cur.fetchall()
    cur.close()
    conn.close()
    return dataInfo


# 查找参与方的角色
def selectParty(name):
    conn = connectDB()
    cur = conn.cursor()
    sql = "select role_names from participants where name = '%s'" % name
    cur.execute(sql)
    addrParty = cur.fetchall()
    cur.close()
    conn.close()
    return addrParty


# 查找条款下的所有活动
def selectActivityByClause(name):
    conn = connectDB()
    cur = conn.cursor()
    # print(name)
    sql = "select processes from clause_info where name = '%s'" % name
    cur.execute(sql)
    activities = cur.fetchall()
    cur.close()
    conn.close()
    return activities


# 根据流程名查找流程
def selectProcessByName(name):
    conn = connectDB()
    cur = conn.cursor()
    sql = "select description, functions, participants from process where name = '%s'" % name
    cur.execute(sql)
    process = cur.fetchall()
    cur.close()
    conn.close()
    return process


# 根据id查询复用库中的流程信息
def selectProcessInLibById(process_id):
    conn = connectReusableLib()
    cur = conn.cursor()
    sql = "select on_chain_data, input, output, call_id, atomic_service, participants " \
          "from reusable_process_service where process_id = '%s'" % process_id
    cur.execute(sql)
    r_processInfo = cur.fetchall()
    cur.close()
    conn.close()
    return r_processInfo


# 根据函数名字查询PIM中函数的数据个数
def selectFunctionDataByName(name):
    conn = connectDB()
    cur = conn.cursor()
    sql = "select dataNames from allfunctions where name = '%s'" % name
    cur.execute(sql)
    allData = cur.fetchall()
    cur.close()
    conn.close()
    return allData


def selectFunctionParamByName(name):
    conn = connectDB()
    cur = conn.cursor()
    sql = "select params from allfunctions where name = '%s'" % name
    cur.execute(sql)
    allParam = cur.fetchall()
    cur.close()
    conn.close()
    return allParam


# 根据函数名查询所有的约束
def selectResByFuncName(name):
    conn = connectDB()
    cur = conn.cursor()
    # print(name)
    sql = "select functionRestriction from allfunctions where name = '%s'" % name
    cur.execute(sql)
    allRes = cur.fetchall()
    # print(allRes)
    cur.close()
    conn.close()
    return allRes


# 根据名字查询Modifier的数据
def selectResDataByName(res_name):
    conn = connectDB()
    cur = conn.cursor()
    sql = "select data_names from restrictions where res_name = '%s'" % res_name
    cur.execute(sql)
    alldata = cur.fetchall()
    cur.close()
    conn.close()
    return alldata


# 根据流程Id查询所有原子服务
def selectAtomicService(process_id):
    conn = connectReusableLib()
    cur = conn.cursor()
    sql = "select atomic_service from reusable_process_service where process_id = '%s'" % process_id
    cur.execute(sql)
    reuse_functions = cur.fetchall()
    cur.close()
    conn.close()
    return reuse_functions


# 根据函数名查询函数的所有信息
def selectAllFunctionInfoByName(name):
    conn = connectDB()
    cur = conn.cursor()
    sql = """select description, functionRestriction, rights, ifConstructor, ifUpdateData, ifGenerateTransaction, 
    dataNames, params, logs, output from allfunctions where name = "%s" """ % name
    cur.execute(sql)
    functionInfo = cur.fetchall()
    cur.close()
    conn.close()
    return functionInfo


# 根据名字查询PIM参数中的类型和描述
def selectTypeByParamName(name):
    conn = connectDB()
    cur = conn.cursor()
    sql = """select type from param where name = "%s" """ % name
    cur.execute(sql)
    param = cur.fetchall()
    cur.close()
    conn.close()
    return param


# 根据id查询函数在库中的所有信息
def selectFunctionInLibById(function_id):
    conn = connectReusableLib()
    cur = conn.cursor()
    sql = "select params, output, call_service, on_chain_data, external_libraries, code from reusable_function_service " \
          "where function_id = '%s'" % function_id
    cur.execute(sql)
    functions = cur.fetchall()
    cur.close()
    conn.close()
    return functions


def selectParamByNameInLib(param_name):
    conn = connectReusableLib()
    cur = conn.cursor()
    sql = "select param_desc, type from param_data where param_name = '%s'" % param_name
    cur.execute(sql)
    param_name = cur.fetchall()
    cur.close()
    conn.close()
    return param_name


def selectParam(name):
    conn = connectDB()
    cur = conn.cursor()
    sql = "select type, description from param where name = '%s'" % name
    cur.execute(sql)
    param = cur.fetchall()
    cur.close()
    conn.close()
    return param


# 根据名字查询函数的所有信息
def selectDataByNameInLib(dataname):
    conn = connectReusableLib()
    cur = conn.cursor()
    # print(dataname)
    sql = "select data_desc, type from con_data where data_name = '%s'" % dataname
    cur.execute(sql)
    data_name = cur.fetchall()
    cur.close()
    conn.close()
    return data_name


# PIM根据名字查询类型和描述
def selectDataTypeAndDescByName(name):
    conn = connectDB()
    cur = conn.cursor()
    # print(name)
    sql = "select type, description from contract_data where name = '%s'" % name
    cur.execute(sql)
    data = cur.fetchall()
    # print(data)
    cur.close()
    conn.close()
    return data


# 获取Pim的函数描述
def selectDescByName(name):
    conn = connectDB()
    cur = conn.cursor()
    sql = "select description from allfunctions where name = '%s'" % name
    cur.execute(sql)
    desc = cur.fetchall()
    cur.close()
    conn.close()
    return desc


def selectDescInLibByName(name):
    conn = connectReusableLib()
    cur = conn.cursor()
    sql = "select description, params, output, call_service, on_chain_data, external_libraries, code from " \
          "reusable_function_service where function_name = '%s'" % name
    cur.execute(sql)
    desc = cur.fetchall()
    cur.close()
    conn.close()
    return desc


def selectResInfoByName(name):
    conn = connectDB()
    cur = conn.cursor()
    sql = "select res_description, data_names, res_params from restrictions where res_name = '%s'" % name
    cur.execute(sql)
    desc = cur.fetchall()
    cur.close()
    conn.close()
    return desc


def selectModifierById(modifier_id):
    conn = connectReusableLib()
    cur = conn.cursor()
    sql = "select params, data_names, code from reusable_modifier_service where modifier_id = '%s'" % modifier_id
    cur.execute(sql)
    modi = cur.fetchall()
    cur.close()
    conn.close()
    return modi


def selectLogByFuncName(name):
    conn = connectDB()
    cur = conn.cursor()
    sql = "select logs from allfunctions where name = '%s'" % name
    cur.execute(sql)
    logs = cur.fetchall()
    cur.close()
    conn.close()
    return logs


def selectLogInfoByName(name):
    conn = connectDB()
    cur = conn.cursor()
    sql = "select params from logs where name = '%s'" % name
    cur.execute(sql)
    logs = cur.fetchall()
    cur.close()
    conn.close()
    return logs
