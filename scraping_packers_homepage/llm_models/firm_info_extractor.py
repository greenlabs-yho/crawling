
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
        당신은 유능한 global html parsor 입니다. 
        주어진 html 은 global 회사의 웹페이지입니다. 
        회사에 contact 할 수 있는 email, phone, address 을 추출해주세요. 
        더불어 취급 products가 있다면 핵심 물품만 keyword list로 추출해주세요.
        
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
            result_html_json = html_chain.invoke({"page_text": page_text})
            break
        except Exception as e:
            print(f'    ** retry[{retry_count+1}] - ', e)
            last_error = str(e)
            time.sleep(1)
        retry_count += 1

    if result_html_json:
        print('   ', '\n    '.join(json.dumps(result_html_json, indent=4).split('\n')))
        return result_html_json
    else:
        return {'error': last_error}