def gettoken():
    import requests
    url = "http://127.0.0.1:2531/v2/api/tools/getTokenId"
    payload = {}
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text

gettoken()


