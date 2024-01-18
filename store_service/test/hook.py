import requests


BASE_URL = "http://127.0.0.1:5000"


def register(register_data):
    endpoint = BASE_URL + "/stores"
    return requests.post(url=endpoint, json=register_data)


def delete_store(register_data, login_data):
    login_resp = login(register_data, login_data)
    endpoint = BASE_URL + "/stores/" + str(login_resp.json()['store_id'])

    return requests.delete(url=endpoint)


def login(register_data, login_data):
    register(register_data)
    endpoint = BASE_URL + "/stores/login"
    return requests.post(url=endpoint, json=login_data)


def get_store(register_data, login_data):
    login_resp = login(register_data, login_data)
    endpoint = BASE_URL + "/stores/" + str(login_resp.json()['store_id'])

    return requests.get(url=endpoint)


def update_store(register_data, login_data):
    pass


