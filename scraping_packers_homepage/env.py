import vertexai
from google.cloud import aiplatform
from langchain.llms.vertexai import VertexAI

import requests
from requests.adapters import HTTPAdapter, Retry

requests.adapters.DEFAULT_POOLSIZE = 50
retries = Retry(total=3)
# 세션을 생성하고 ConnectionPool 크기를 설정
session = requests.Session()
session.mount('https://', requests.adapters.HTTPAdapter(pool_connections=50, pool_maxsize=50, max_retries=retries))


PROJECT_ID = "grainscanner"  # @param {type:"string"}
REGION = "asia-northeast3"  # @param {type:"string"}

# Initialize Vertex AI SDK
vertexai.init(project=PROJECT_ID, location=REGION)

# Text model instance integrated with langChain
llm = VertexAI(
    model_name="text-bison", #"gemini-pro",#"text-bison",
    max_output_tokens=1024,
    temperature=0,
    top_p=0.8,
    top_k=40,
    verbose=True,
    location=REGION
)

TARGET_COLUMN_LIST = ['homepage', 'extract_url', 'company_name', 'mail', 'phone', 'address', 'fax', 'products', 'error']