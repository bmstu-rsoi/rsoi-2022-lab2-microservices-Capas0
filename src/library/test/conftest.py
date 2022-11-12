import pytest


@pytest.fixture
def person_data():
    return {
        'name': 'Adam',
        'age': 30,
        'work': 'Paradise Inc',
        'address': 'Heaven'
    }
