import pytest

from wotcApi import WOTCApi
from wotcApi import InvalidClientCredentials, WotcException, EmailAddressInUse, AgeRequirement


def test_response_parse_generic_data():
    response = WOTCApi()._response_parse({'data': 'foo'})
    assert response == 'foo'


def test_response_parse_access_token():
    response = WOTCApi()._response_parse({'access_token': 'bar'})
    assert response == {'access_token': 'bar'}


def test_response_parse_invalid_login():
    with pytest.raises(Exception) as e_info:
        WOTCApi()._response_parse({'error': 'INVALID CLIENT CREDENTIALS'})
    assert e_info.type == InvalidClientCredentials


def test_response_parse_duplicate_email():
    with pytest.raises(Exception) as e_info:
        WOTCApi()._response_parse({'error': 'EMAIL ADDRESS IN USE'})
    assert e_info.type == EmailAddressInUse


def test_response_parse_age_restriction():
    with pytest.raises(Exception) as e_info:
        WOTCApi()._response_parse({'error': 'AGE REQUIREMENT'})
    assert e_info.type == AgeRequirement


def test_response_parse_garbage_input():
    with pytest.raises(Exception) as e_info:
        WOTCApi()._response_parse({'some': 'garbage'})
    assert e_info.type == WotcException
