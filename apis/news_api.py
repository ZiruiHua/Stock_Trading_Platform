from django.http import JsonResponse

import json
import requests

api_base_url = 'https://newsapi.org/v1/articles?source=bloomberg&sortBy=top&apiKey={0}'

def get_headlines(errors):
    api_key = '90034b841ee44bd29fe0b5412dea45ef' # TODO: obscure API key
    url = api_base_url.format(api_key)
    r = requests.get(url)
    json_output = r.json()
    if json_output['status'] == "ok":
        i = 0
        for j in json_output['articles']:
            j['id'] = i
            i = i + 1
        return json_output['articles'][0:4]
    errors.append('API service is down.')
    return []