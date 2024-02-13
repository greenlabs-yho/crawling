from bs4 import BeautifulSoup, NavigableString, Tag, Comment, Doctype, ProcessingInstruction
from requests.adapters import HTTPAdapter, Retry
from urllib.parse import urlparse, urljoin
import requests, time, json

from scraping_packers_homepage.llm_models.a_tag_selector import get_url_list_with_llm
from scraping_packers_homepage.llm_models.firm_info_extractor import get_firm_info_with_llm

session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))


def change_protocol(url):
    # URL 파싱
    parsed_url = urlparse(url)
    # 프로토콜 추출
    protocol = parsed_url.scheme
    if protocol == 'http':
        return parsed_url._replace(scheme='https').geturl()
    elif protocol == 'https':
        return parsed_url._replace(scheme='http').geturl()

    return url


def recovery_url(trouble_url):
    import re
    # URL 패턴 정의
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, trouble_url)

    # 결과 출력
    result = set()
    for url in urls:
        result.add(url)

    print(f'    ** recovery url - from ({trouble_url}) / to ({result})')
    return result


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def extract_page(url, is_recursive=False):
    # 페이지 콘텐츠를 가져옵니다.

    if not url.startswith('http'):
        url = "https://" + url

    try :
        response = session.get(url, timeout=15, headers=headers)
    except requests.ConnectionError as ce:
        if not is_recursive:
            url_list = recovery_url(url)
            for sub_url in url_list:
                code, response = extract_page(sub_url, is_recursive=True)
                if code == 200:
                    return code, response
            return 500, None
        else:
            print(f'  ** error ({url})-', str(ce))
            return 500, None
    except Exception as e:
        print(f'  ** error ({url})-', str(e))
        return 500, None
    
    if response.status_code == 403:
        if not is_recursive:
            return extract_page(change_protocol(url), is_recursive=True)
    return response.status_code, response



SPLIT_LENGTH = 2000

def soup_to_splitted_text(soup):
    split_texts = []
    current_list = []
    total_len = 0

    for element in soup.descendants:  # body 태그의 자식 노드 순회
        if isinstance(element, NavigableString) and not isinstance(element, (Comment, Doctype, ProcessingInstruction)):
            txt = element.strip().replace('\n\n\n', ' ')
            parent = element.parent
            if txt and (parent and parent.name not in ['script', 'style', 'meta', 'noscript']): # 해당 tag 의 하위 텍스트는 모으지 않음
                current_list.append(txt)
                total_len += len(txt)
        elif isinstance(element, Tag):
            if element.name == 'div':  # div 가 나올때마다 split 여부를 체크함.
                if total_len > SPLIT_LENGTH:
                    split_texts.append('\n'.join(current_list))
                    current_list.clear()
                    total_len = 0

    # 마지막 남은 텍스트 추가
    if current_list:
        split_texts.append('\n'.join(current_list))

    if len(split_texts) > 1:
        print(f'    ** split text - chunk : {len(split_texts)}')
    
    return split_texts


import pandas as pd

def to_dataframe(json_data, target_column_list):
    normalized_df = pd.json_normalize(json_data)
    total_column_list = list(normalized_df.columns)

    merged_df = pd.DataFrame(columns=target_column_list)

    for target_col in target_column_list:
        related_cols = [col for col in total_column_list if target_col in col]

        def merge_row(row):
            merged_data = []
            for item in row.dropna():
                if isinstance(item, dict):
                    merged_data.append(json.dumps(item, ensure_ascii=False))
                elif isinstance(item, list):
                    merged_data.extend([str(x) for x in item])
                elif not pd.isnull(item):
                    merged_data.append(item)
            if merged_data:
                return ';\n'.join(merged_data)
            else:
                return ''

        if related_cols:
            merged_df[target_col] = normalized_df[related_cols].apply(merge_row, axis=1)

    return merged_df


def is_string_not_none_nan(value):
    if pd.notna(value) and isinstance(value, str) and value:
        return True
    return False


get_domain = lambda url: urlparse(url).netloc.replace('www.', '')
check_all_columns_true = lambda data_dict, target_column_list: all(data_dict.get(column, False) for column in target_column_list)


def get_domain_a_tag_list(soup, main_url):
    a_list = soup.find_all('a', href=True)
    main_domain = get_domain(main_url)
    distinct_a_list = {}
    for link in a_list:
        full_url = urljoin(main_domain, link.get('href')).strip('/')
        # 
        if get_domain(full_url).startswith(main_domain) and urlparse(full_url).path and not full_url.endswith('.pdf'):
            distinct_a_list[full_url] = link
    
    if distinct_a_list:
        return list(distinct_a_list.values())
    return []


def soup_to_firm_info(soup, llm, target_column_list):
    try :
        firm_info_list = []
        text_list = soup_to_splitted_text(soup)
        for text_content in text_list:
            info = get_firm_info_with_llm(llm, text_content)
            if info:
                firm_info_list.append(info)
    except Exception as e:
        firm_info_list.append({'error': str(e)})
        
    sub_df = to_dataframe(firm_info_list, target_column_list)
    return sub_df


def check_exists_column_contents(df, target_column_list):
    results = {}
    for column in target_column_list:
        # 해당 컬럼이 DataFrame에 존재하고, 값이 하나라도 있는지 확인
        results[column] = df[column].apply(is_string_not_none_nan).any()
    return results


def split_url_list(distinct_a_list):
    result_listset = []
    tmp_list = []

    decompose_tag_list = ['svg', 'path', 'img']

    total = 0
    for a in distinct_a_list:
        for decompose_tag in decompose_tag_list:
            for t in a.find_all(decompose_tag):
                t.decompose()

        str_a = str(a)
        if total and total + len(str_a) > SPLIT_LENGTH:
            result_listset.append(tmp_list)
            total = 0
            tmp_list = []
        else:
            total += len(str_a)
            tmp_list.append(a)
    if tmp_list:
        result_listset.append(tmp_list)
    
    return result_listset


def get_url_list(llm, distinct_a_list):
    total_result_list = []
    url_list_set = split_url_list(distinct_a_list)
    for url_list in url_list_set:
        sub_result_list = get_url_list_with_llm(llm, url_list)
        if sub_result_list:
            total_result_list.extend(sub_result_list)

    return total_result_list


def run(main_url, llm, target_column_list, required_column_list=['mail', 'phone', 'address', 'products']):
    print(f'** [main page] 조회 - {main_url}')
    status, response = extract_page(main_url)

    result_df = pd.DataFrame(columns=target_column_list)
    if status == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        print(f'  ** [llm] contact 정보 & products 추출')
        sub_df = soup_to_firm_info(soup, llm, target_column_list)
        sub_df['homepage'] = main_url
        sub_df['extract_url'] = main_url
        result_df = pd.concat([result_df, sub_df], ignore_index=True)


        exists_columns = check_exists_column_contents(sub_df, target_column_list)
        if check_all_columns_true(exists_columns, required_column_list):
            return result_df

        print(f'  ** a tag 추출')
        distinct_a_list = get_domain_a_tag_list(soup, main_url)
        if distinct_a_list:
            print(f'  ** [llm] 회사 정보와 관련있는 a tag 선별')
            page_list = get_url_list(llm, distinct_a_list)
        
            for sub_url in page_list:
                print(f'  ** [sub page] 조회 - {sub_url}')
                sub_status, sub_response = extract_page(sub_url)
                if sub_status == 200:
                    sub_soup = BeautifulSoup(sub_response.content, 'html.parser')

                    print(f'  ** [llm] contact 정보 & products 추출')
                    sub_df = soup_to_firm_info(sub_soup, llm, target_column_list)
                    sub_df['homepage'] = main_url
                    sub_df['extract_url'] = sub_url

                    result_df = pd.concat([result_df, sub_df], ignore_index=True)

                    exists_columns = check_exists_column_contents(result_df, target_column_list)
                    if check_all_columns_true(exists_columns, required_column_list):
                        return result_df
                else:
                    print(f'    [{sub_status}] : 조회 실패')
        else:
            print(f'    [empty]')
    else:
        print(f'    [{status}] : 조회 실패')

    return result_df
