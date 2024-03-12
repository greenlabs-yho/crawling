from ..env import session

def search(keyword, subscription_key, endpoint="https://api.bing.microsoft.com/v7.0/search", **kwargs):
    params = { 'q': keyword }
    headers = { 'Ocp-Apim-Subscription-Key': subscription_key }

    
    response = session.get(endpoint, headers=headers, params=params)
    response.raise_for_status()

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 403:
        raise Exception(f"[{response.status_code}] quota exceeded : {response.text}")
    else:
        raise Exception(f"[{response.status_code}] {response.text}")