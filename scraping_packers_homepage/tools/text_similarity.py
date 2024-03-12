#pip install fuzzywuzzy
#pip install python-Levenshtein  # 속도향상에 도움됨 


from fuzzywuzzy import fuzz



def measure_text_similarity(token1, token2, method="TOKEN_SORT_RATIO"):
    if method == "TOKEN_SORT_RATIO":
        # 두 문자열 간의 Token Sort Ratio 유사도 계산
        similarity_score = fuzz.token_sort_ratio(token1, token2)

    return similarity_score
