from ..env import session

def search(keyword, search_engine_id, api_key, **kwargs):
    query_params = {
        'q': keyword,
        'cx': search_engine_id,        
        'key': api_key
    }
    query_params.update(kwargs)
    headers= {
        "Accept": "application/json"
    }

    
    response = session.get('https://customsearch.googleapis.com/customsearch/v1', headers=headers, params=query_params, timeout=5)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"[{response.status_code}] response.content")