import logging
from enum import Enum
from os import getenv
from typing import List, Dict, Callable
# from dataclasses import dataclass, asdict
# from inspect import signature as inspectSignature
# from json import dumps as dumpJson
from json import loads as loadJson

from dotenv import load_dotenv
from requests import Response, get, patch, post, put

from schemas import WotcAuthResponse
from local_logging import logger


class Host(Enum):
    PLATFORM = "api.platform.wizards.com"
    TABLETOP = "api.tabletop.wizards.com"


class Path(Enum):
    AUTH = "/auth/oauth/token"
    DEFAULT = "/silverbeak-griffin-service/graphql"
    PROFILE = "/profile"
    REGISTER = "/accounts/register"


class WotcException(Exception):
    pass


class EmailAddressInUse(WotcException):
    pass


class AgeRequirement(WotcException):
    pass


class InvalidClientCredentials(WotcException):
    pass

class WOTCApi():
    access_token: str
    headers: dict
    host: Host
    path: Path
    url: str

    def __call(self, call: Callable, **kwargs) -> dict:
        longstr = [f'\nkey: {k},\n value: {v}' for k, v in kwargs.items()]
        longstr = ' '.join(longstr)
        msg = f'Sending {call.__name__.upper()} to endpoint {self.url} '
        msg += f"using kwargs: {longstr if len(longstr) > 0 else None}"
        logger.debug(msg)

        results: Response = call(self.url, **kwargs, headers=self.headers)
        jsonResults: dict = loadJson(results.content.decode('utf-8'))
        return self._response_parse(jsonResults)

    def _response_parse(self, response: dict) -> dict:
        if 'data' in response.keys():
            logger.debug('Call successful!')
            logger.debug(response)
            return response['data']
        elif 'access_token' in response.keys():
            logger.debug('Call successful!')
            logger.debug(response)
            return response
        elif 'error' in response.keys():
            error = response['error']
            logger.warning(f"Found error {error} in response body.")
            match error:
                case 'EMAIL ADDRESS IN USE':
                    raise EmailAddressInUse
                case 'AGE REQUIREMENT':
                    raise AgeRequirement
                case 'INVALID CLIENT CREDENTIALS':
                    raise InvalidClientCredentials
        else:
            logger.warning(f"Error: can't parse JSON:\n{response}")
            raise WotcException(f"Unknown response: {response}")

    def _patch(self, **kwargs) -> dict:
        return self.__call(patch, **kwargs)

    def _post(self, **kwargs) -> dict:
        return self.__call(post, **kwargs)

    def _put(self, **kwargs) -> dict:
        return self.__call(put, **kwargs)

    def _get(self, **kwargs) -> dict:
        return self.__call(get, **kwargs)

    @property
    def url(self) -> str:
        return 'https://' + self.host.value + self.path.value

    @property
    def authorization(self) -> str:
        if self.path == Path.AUTH:
            load_dotenv()
            # return getenv("WOTC_BASIC_CREDENTIALS")
            return f'Basic {getenv("WOTC_BASIC_CREDENTIALS")}'
        else:
            return f'Bearer {self.access_token}'

    @property
    def headers(self) -> dict:
        return {
            'Authorization': self.authorization,
            'Content-Type': 'application/json'
        }

    def login(self, refresh_token) -> WotcAuthResponse:
        self.host = Host.PLATFORM
        self.path = Path.AUTH
        json = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        logging.debug(self.headers)
        results = self._post(json=json)
        return WotcAuthResponse(**results)
