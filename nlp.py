import numpy as np
import pymysql
from sentence_transformers import SentenceTransformer, util
from sympy.tensor import tensor

model = SentenceTransformer('./model/all-MiniLM-L6-v2')


# 流程模板层的匹配
def serviceSelectionByProcess(processDesc):
    # 获取复用库的所有描述和对应的Id
    pro = getAllProcess()
    sentences = []
    for p in pro:
        sentences.append(p[1])
    # sentences = ['Apply to adapt abstract IP as a work',
    #              'The votes of each committee member are recorded',
    #              'Release a new work',
    #              'Release shares of new works',
    #              ]
    # 'register the results of all the votes'
    # 输入的等待匹配的句子
    sentences_cur = [processDesc]
    # Compute embeddings
    embeddings = model.encode(sentences, convert_to_tensor=True)
    embeddings_cur = model.encode(sentences_cur, convert_to_tensor=True)
    # Compute cosine-similarities for each sentence with each other sentence
    cosine_scores = util.cos_sim(embeddings, embeddings_cur)
    # sentence = 'Send a request to adapt the ip into a work'
    # Find the pairs with the highest cosine similarity scores
    # print(cosine_scores)
    pro_np = np.array(pro)
    selected_tensor = cosine_scores[cosine_scores[:, 0] > 0.55]
    res = []
    if len(selected_tensor) == 0:
        print('没有符合条件的数据')
    elif len(selected_tensor) != 1:
        # 对挑选的数据进行降序排列
        sorted_indexes = np.argsort(-selected_tensor[:, 0])
        # 根据排序结果对应到id数组上
        sorted_ids = pro_np[cosine_scores[:, 0] > 0.55][sorted_indexes[0:len(sorted_indexes)]]
        # print(sorted_ids)
        # 输出id数组的排序结果
        res = sorted_ids[:, 0].astype(int)
        # print(res)
    else:
        max_index = cosine_scores.argmax()
        res.append(pro[max_index][0])
    # max_scores = cosine_scores.max()
    # max_index = cosine_scores.argmax()
    # processId = pro[max_index][0]
    # if max_scores < 0.55:
    #     print("No matching sentence found.")
    # else:
    #     print(f"Most similar sentence: {sentences[max_index]}")
    # print(res)
    return res


def serviceSelectionByFunction(funcDesc):
    functions = getAllFunction()
    sentences = []
    for f in functions:
        sentences.append(f[1])
    # print(funcDesc)
    sentences_cur = [funcDesc]
    # Compute embeddings
    embeddings = model.encode(sentences, convert_to_tensor=True)
    embeddings_cur = model.encode(sentences_cur, convert_to_tensor=True)
    # Compute cosine-similarities for each sentence with each other sentence
    cosine_scores = util.cos_sim(embeddings, embeddings_cur)
    # sentence = 'Send a request to adapt the ip into a work'
    # Find the pairs with the highest cosine similarity scores
    # print(cosine_scores)
    func_np = np.array(functions)
    selected_tensor = cosine_scores[cosine_scores[:, 0] > 0.55]
    # max_scores = cosine_scores.max()
    # max_index = cosine_scores.argmax()
    res = []
    if len(selected_tensor) == 0:
        print('没有符合条件的数据')
    elif len(selected_tensor) != 1:
        # 对挑选的数据进行降序排列
        sorted_indexes = np.argsort(-selected_tensor[:, 0])
        # 根据排序结果对应到id数组上
        sorted_ids = func_np[cosine_scores[:, 0] > 0.55][sorted_indexes[0:len(sorted_indexes)]]
        # print(sorted_ids)
        # 输出id数组的排序结果
        res = sorted_ids[:, 0].astype(int)
        # print(res)
    else:
        max_index = cosine_scores.argmax()
        res.append(functions[max_index][0])
    # if max_scores < 0.5:
    #     print("No matching sentence found.")
    # else:
    #     print(f"Most similar sentence: {sentences[max_index]}")
    return res


# 匹配约束
def serviceSelectionByModifier(modiDesc):
    modifiers = getAllModifier()
    sentences = []
    for m in modifiers:
        sentences.append(m[1])
    sentences_cur = [modiDesc]
    embeddings = model.encode(sentences, convert_to_tensor=True)
    embeddings_cur = model.encode(sentences_cur, convert_to_tensor=True)
    cosine_scores = util.cos_sim(embeddings, embeddings_cur)
    modi_np = np.array(modifiers)
    selected_tensor = cosine_scores[cosine_scores[:, 0] > 0.55]
    res = []
    if len(selected_tensor) == 0:
        print('没有符合条件的数据')
    elif len(selected_tensor) != 1:
        sorted_indexes = np.argsort(-selected_tensor[:, 0])
        sorted_ids = modi_np[cosine_scores[:, 0] > 0.55][sorted_indexes[0:len(sorted_indexes)]]
        res = sorted_ids[:, 0].astype(int)
    else:
        max_index = cosine_scores.argmax()
        res.append(modifiers[max_index][0])
    return res


# 数据匹配，第一个参数为一句话，第二个参数为列表
def selectMatchData(desc, sentences):
    sentences_cur = [desc]
    embeddings = model.encode(sentences, convert_to_tensor=True)
    embeddings_cur = model.encode(sentences_cur, convert_to_tensor=True)
    cosine_scores = util.cos_sim(embeddings, embeddings_cur)
    max_scores = cosine_scores.max()
    # sentences的索引
    max_index = cosine_scores.argmax()
    # print(max_scores)
    return max_index


def connectReusableLib():
    conn = pymysql.connect(host='localhost', user='root', password='lwy2000712/', database='reuse_lib', charset='utf8')
    return conn


def getAllProcess():
    conn = connectReusableLib()
    cur = conn.cursor()
    sql = "select process_id, description from reusable_process_service"
    cur.execute(sql)
    processes = cur.fetchall()
    cur.close()
    conn.close()
    return processes


def getAllFunction():
    conn = connectReusableLib()
    cur = conn.cursor()
    sql = "select function_id, description from reusable_function_service"
    cur.execute(sql)
    functions = cur.fetchall()
    cur.close()
    conn.close()
    return functions


def getAllModifier():
    conn = connectReusableLib()
    cur = conn.cursor()
    sql = "select modifier_id, description from reusable_modifier_service"
    cur.execute(sql)
    modifier = cur.fetchall()
    cur.close()
    conn.close()
    return modifier
