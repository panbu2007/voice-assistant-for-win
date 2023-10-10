import difflib
from search import search_app_name
import numpy as np

nameList, pathList = search_app_name()

matchList = [['打开', '运行', '启动'], ['音量', '声音', '响', '弱', '轻', '重'], ['亮度', '暗']]
def get_closest_match(x, score_line=0.2):
    scores = []
    for m in matchList:
        current_score = 0
        for current_string in m:
            current_score = max(difflib.SequenceMatcher(None, x, current_string).ratio(), current_score)
        scores.append(current_score)
    print(scores)
    index = np.argsort(-np.array(scores))
    if scores[index[0]] <= score_line:
        return -1
    return index[0]

indexList = [['一', '二', '三'], ['1', '2', '3']]
def get_closest_index(x, score_line=0.3):
    max_score, index = 0, 0
    for m in indexList:
        for p, current_string in enumerate(m):
            score = difflib.SequenceMatcher(None, x, current_string).ratio()
            if difflib.SequenceMatcher(None, x, current_string).ratio() > max_score:
                max_score = score
                index = p
    #print(max_score, p)
    #if scores[index[0]] < score_line:
    #    return -1
    return index



def get_closest_app(x, score_line=0.5):
    '''
    high_three = [0]*3
    high_three_scores = [0]*3
    for current_string in nameList:
        current_score = difflib.SequenceMatcher(None, x, current_string).ratio()
        for i in range(3):
            if high_three_scores[i] < current_score:
                high_three_scores[i] = current_score
                high_three[i] = current_string
                break
    '''
    scores = []
    for current_string in nameList:
        current_score = difflib.SequenceMatcher(None, x.lower(), current_string.lower()).ratio()
        scores.append(current_score)
    print(scores)
    index = np.argsort(-np.array(scores))
    if scores[index[0]] > score_line:
        return [nameList[index[0]]], [pathList[index[0]]]
    return [nameList[index[i]] for i in range(3)], [pathList[index[i]] for i in range(3)]
