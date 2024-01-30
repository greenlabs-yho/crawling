import vertexai
from google.cloud import aiplatform
from langchain.llms.vertexai import VertexAI

PROJECT_ID = "grainscanner"  # @param {type:"string"}
REGION = "asia-northeast3"  # @param {type:"string"}

# Initialize Vertex AI SDK
vertexai.init(project=PROJECT_ID, location=REGION)

# Text model instance integrated with langChain
llm = VertexAI(
    model_name="text-bison", #"gemini-pro",#"text-bison",
    max_output_tokens=1024,
    temperature=0.4,
    top_p=0.8,
    top_k=40,
    verbose=True,
    location=REGION
)

TARGET_COLUMN_LIST = ['homepage', 'extract_url', 'company_name', 'mail', 'phone', 'address', 'fax', 'products', 'error']