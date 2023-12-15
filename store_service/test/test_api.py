from hook import *
from fixtures import *


def test_register(register_data):
    resp = register(register_data)

    assert resp.status_code == 201
    assert resp.json()['result'] == 'success'


def test_login(register_data, login_data):
    resp = login(register_data, login_data)

    assert resp.status_code == 200
    assert resp.json()['access_token'] is not None


def test_get_store(register_data, login_data):
    resp = get_store(register_data, login_data)

    assert resp.status_code == 200
    assert resp.json()['store']['store_id'] is not None



