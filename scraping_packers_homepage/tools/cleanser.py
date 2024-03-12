import re

replacement_mapping = {
    'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A', 'Å': 'A', 'Ā': 'A', 
    'Æ': 'AE', 
    'Ç': 'C', 'Č': 'C', 
    'Ð': 'D', 
    'Đ': 'Dj', 
    'È': 'E', 'É': 'E', 'Ê': 'E', 'Ë': 'E', 'Ē': 'E', 
    'Ğ': 'G', 
    'I': 'I', 'Ì': 'I', 'Í': 'I', 'Î': 'I', 'Ï': 'I', 'Ī': 'I', 'İ': 'I', 
    'Ł': 'L', 
    'Ñ': 'N', 'Ń': 'N', 
    'Ò': 'O', 'Ó': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö': 'O', 'Ø': 'O', 'Ō': 'O', 
    'Ś': 'S', 'Ş': 'S', 'Š': 'S', 
    'Þ': 'TH', 
    'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'Ü': 'U', 'Ū': 'U', 
    'Ý': 'Y', 
    'Ź': 'Z', 'Ż': 'Z', 'Ž': 'Z', 
    'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a', 'å': 'a', 'ā': 'a', 
    'æ': 'ae', 
    'ç': 'c', 'č': 'c', 
    'ð': 'd', 
    'đ': 'dj', 
    'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e', 'ē': 'e', 
    'ğ': 'g', 
    'i': 'i', 'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i', 'ī': 'i', 'ı': 'i', 
    'ł': 'l', 
    'ñ': 'n', 'ń': 'n', 
    'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o', 'ø': 'o', 'ō': 'o', 
    'ś': 's', 'ş': 's', 'š': 's', 
    'ß': 'ss', 
    'þ': 'th', 
    'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u', 'ū': 'u', 
    'ý': 'y', 'ÿ': 'y', 
    'ź': 'z', 'ż': 'z', 'ž': 'z'}

def replace_special_characters(text):
    """
    주어진 텍스트에서 특수 문자를 영문으로 대체한다.
    """
    for original_char, replacement_char in replacement_mapping.items():
        text = text.replace(original_char, replacement_char)
    return text


def cleansing_comp_name(name: str, remove_space=False) -> str:
    name = replace_special_characters(name) # 영문으로 치환가능한 문자 치환
    name = name.lower()     # 소문자
    name = name.replace('&', 'and') # & 처리

    suffixes = [
        "ltd", "co", "co ltd", "coltd", "company limited", "companylimited",
        "private limited", "privatelimited", "limited", "llc", "sac", "sa", "inc",
        "co-op", "inc", "pty ltd", "ptyltd", "gmbh", "eirl", "sarl", "ltd sti", "ltdsti",        
    ]

    # 정규식 패턴 생성: 접미사들을 '|'로 연결하여 선택적으로 매치하도록 함
    # 각 접미사는 단어 경계(\b)로 둘러싸여 있으며, 접미사 앞에 공백이 있을 수 있음
    pattern = r'\b(?:' + '|'.join(re.escape(suffix) for suffix in suffixes) + r')\b'
    name = re.sub(pattern, '', name, flags=re.IGNORECASE)

    # 숫자 문자 외 모두 제거(특수문자, 공백)
    if remove_space:
        pattern = r'[^\w]'
    else:
        pattern = r'[^\w\s]'
    name = re.sub(pattern, '', name, flags=re.UNICODE)

    return name

# target_name = 'Greenlabs 한글 きゆん。 Esto es español, Bu Türkçe.1'
# search_name = 'Green Labs Llc'

# print(cleansing_name(target_name), "/", cleansing_name(search_name))