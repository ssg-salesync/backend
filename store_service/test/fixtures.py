from hook import *
import pytest


@pytest.fixture
def register_data(login_data):
    data = {
        "username": login_data['username'],
        "password": login_data['password'],
        "owner_name": "pytest",
        "phone": "01012341234",
        "store_name": "pytest store",
        "address": "pytest address",
        "store_type": "pytest type"
    }

    yield data

    delete_store(data, login_data)


@pytest.fixture
def login_data():
    yield {
        "username": "pytest",
        "password": "pytest"
    }


