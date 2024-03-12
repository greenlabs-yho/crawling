
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json
import time

DEFAULT_RETRY_COUNT = 3

prompt = """
Task: Determine Matching of Country and Product
Criteria: 
 - Assess if input country corresponds to actual country ({org_country}).
 - Evaluate if input product details match the actual product list:
  "{org_sku}".
Input: 
 - Country: {input_country}
 - Product: "{input_sku}"

Output Format: 
 - JSON indicating match status for country and product.
  {{"country": False, "product": False}}
    """

# 더불어 취급 products가 있다면 핵심 물품만 keyword list로 추출해주세요.
def check_firm_info_with_llm(llm, org_country, org_sku, input_country, input_sku, max_retry_count=DEFAULT_RETRY_COUNT):
    json_parser = SimpleJsonOutputParser()

    prompt_template = PromptTemplate(
        input_variables=["org_country", "org_sku", "input_country", "input_sku"], 
        template=prompt, 
        output_parser=json_parser,
    )

    chain = prompt_template | llm | json_parser
    retry_count = 0
    result_json = None
    last_error = None
    while retry_count < max_retry_count:
        try :
            result_json = chain.invoke({"org_country": org_country, "org_sku": org_sku, "input_country": input_country, "input_sku": input_sku})
            break
        except Exception as e:
            print(f'    ** retry[{retry_count+1}] - ', e)
            last_error = str(e)
            time.sleep(1)
        retry_count += 1

    if result_json:
        print(result_json)
        return result_json
    else:
        return {'error': last_error}