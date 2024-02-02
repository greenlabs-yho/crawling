
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.prompts import PromptTemplate
#from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json
import time

DEFAULT_RETRY_COUNT = 3

# 더불어 취급 products가 있다면 핵심 물품만 keyword list로 추출해주세요.
def select_comp_homepage_with_llm(llm, comp_name, search_result, max_retry_count=DEFAULT_RETRY_COUNT):
    html_template = """
다음 정보는 Google Custom Search JSON API를 통해 얻은 검색 결과의 일부입니다. 
"{comp_name}"라는 이름의 회사 홈페이지 URL을 찾는 것이 목표입니다.
제공된 JSON 데이터에서 "link" 요소의 값을 찾아주세요. 
해당 회사의 공식 홈페이지 링크가 명확하게 식별되면, 그 "link" 요소의 값을 반환해주세요. 
정확한 URL을 찾는 것이 불가능하다면, 빈 문자열("")을 반환해주세요.

Output Example1: "https://abc.com/"

Output Example2: ""

input data :
{search_result}
    """

    html_prompt_template = PromptTemplate(
        input_variables=["comp_name", "search_result"], 
        template=html_template, 
    )

    html_chain = html_prompt_template | llm
    retry_count = 0
    url = None
    last_error = None
    while retry_count < max_retry_count:
        try :
            url = html_chain.invoke({"comp_name": comp_name, "search_result": json.dumps(search_result, ensure_ascii=False)})
            break
        except Exception as e:
            print(f'    ** retry[{retry_count+1}] - ', e)
            last_error = str(e)
            time.sleep(1)
        retry_count += 1

    if url:
        print(url)
        return url
    else:
        return {'error': last_error}