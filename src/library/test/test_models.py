import pytest
from marshmallow import ValidationError

from ..app.schemas import PersonSchema


class TestPerson:

    def test_valid_data(self, person_data):
        person = PersonSchema().load(person_data)
        for key, value in person_data.items():
            assert getattr(person, key) == value

    def test_empty_name(self, person_data):
        del person_data['name']
        with pytest.raises(ValidationError) as err:
            PersonSchema().load(person_data)
        assert err.type is ValidationError
        assert 'name' in err.value.messages
        assert 'Missing data for required field.' in err.value.messages['name']

    def test_invalid_name(self, person_data):
        person_data['name'] = 0
        with pytest.raises(ValidationError) as err:
            PersonSchema().load(person_data)
        assert err.type is ValidationError
        assert 'name' in err.value.messages
        assert 'Not a valid string.' in err.value.messages['name']

    def test_invalid_age(self, person_data):
        person_data['age'] = 'zero'
        with pytest.raises(ValidationError) as err:
            PersonSchema().load(person_data)
        assert err.type is ValidationError
        assert 'age' in err.value.messages
        assert 'Not a valid integer.' in err.value.messages['age']

    def test_extra_field(self, person_data):
        person_data['id'] = 1
        with pytest.raises(ValidationError) as err:
            PersonSchema().load(person_data)
        assert err.type is ValidationError
        assert 'id' in err.value.messages
        assert 'Unknown field.' in err.value.messages['id']
