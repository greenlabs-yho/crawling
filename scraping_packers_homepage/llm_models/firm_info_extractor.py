
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json
import time

DEFAULT_RETRY_COUNT = 3

# 더불어 취급 products가 있다면 핵심 물품만 keyword list로 추출해주세요.
def get_firm_info_with_llm(llm, page_text, max_retry_count=DEFAULT_RETRY_COUNT):
    json_parser = SimpleJsonOutputParser()
    html_template = """
당신은 전문적인 HTML 텍스트 파서입니다. 
주어진 content는 글로벌 회사의 웹페이지 HTML에서 추출된 텍스트입니다. 
이 텍스트를 분석하여, 다음 정보를 추출해주세요:

1. 회사에 연락할 수 있는 email, phone, address 를 찾아내세요.
2. 취급하는 products 중 농산물 및 식품 재료에 해당하는 products를 keyword list 로 정리해주세요. 

분석 과정에서 텍스트의 문맥을 고려하여, 명확하게 식별 가능한 정보만을 추출하고 정리해야 합니다. 불명확하거나 관련 없는 정보는 제외해주세요.

        Format instructions:
        {format_instructions}

        ------------
        content:
        {page_text}
    """

    html_prompt_template = PromptTemplate(
        input_variables=["page_text"], 
        template=html_template, 
        output_parser=json_parser,
        partial_variables={
            "format_instructions": json_parser.get_format_instructions()# + "\n" + "json key are (email, phone, address, items)"
        }
    )

    html_chain = html_prompt_template | llm | json_parser
    retry_count = 0
    result_html_json = None
    last_error = None
    while retry_count < max_retry_count:
        try :
            result_html_json = html_chain.invoke({"page_text": page_text[:3000]})
            break
        except Exception as e:
            print(f'    ** retry[{retry_count+1}] - ', e)
            last_error = str(e)
            time.sleep(1)
        retry_count += 1

    if result_html_json:
        print('   ', '\n    '.join(json.dumps(result_html_json, indent=4, ensure_ascii=False).split('\n')))
        return result_html_json
    else:
        return {'error': last_error}