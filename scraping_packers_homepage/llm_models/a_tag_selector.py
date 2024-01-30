
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers.json import SimpleJsonOutputParser
import json
import time

DEFAULT_RETRY_COUNT = 3

def get_url_list_with_llm(llm, a_tag_list, max_retry_count=DEFAULT_RETRY_COUNT):
    json_parser = SimpleJsonOutputParser()

    filter_template = """
        당신은 유능하고 경험 많은 웹 제작자입니다.
        다음 global 회사 홈페이지에 태그된  a태그 리스트를 보고 
        회사에 contact 할 수 있는 정보를 담은 a태그와 
        취급 product를 설명하는 a태그만 골라서 href attribute를 추출해주세요.
        판단은 엄격하게 진행해주세요.

        Format instructions:
        ["href attribute", "href attribute"]

        -----------------------
        content :
        {a_tag_list}
    """

    filter_prompt_template = PromptTemplate(
        input_variables=["a_tag_list"], 
        template=filter_template, 
        output_parser=json_parser,
        partial_variables={
            "format_instructions": json_parser.get_format_instructions()
        }
    )

    chain = filter_prompt_template|llm|json_parser

    retry_count = 0
    last_error = None
    result_additional_filter_json = None
    while retry_count < max_retry_count:
        try:
            result_additional_filter_json = chain.invoke({"a_tag_list": a_tag_list})
            break
        except Exception as e:
            print(f'    ** retry[{retry_count+1}] - ', e)
            last_error = str(e)
            time.sleep(3)
        retry_count += 1

    if result_additional_filter_json:
        print('   ', result_additional_filter_json)
        return result_additional_filter_json
    else:
        return {'error': last_error}