from enum import Enum
from os import getenv
from typing import List, Dict, Callable
# from dataclasses import dataclass, asdict
# from inspect import signature as inspectSignature
# from json import dumps as dumpJson
from json import loads as loadJson

from dotenv import load_dotenv
from requests import Response, get, patch, post, put

from local_logging import logger


class Host(Enum):
    PLATFORM = "api.platform.wizards.com"
    TABLETOP = "api.tabletop.wizards.com"


class Path(Enum):
    AUTH = "/auth/oauth/token"
    DEFAULT = "/silverbeak-griffin-service/graphql"
    PROFILE = "/profile"
    REGISTER = "/accounts/register"


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
        if 'data' in jsonResults.keys():
            logger.debug('Call successful!')
            logger.debug(jsonResults)
            return jsonResults['data']
        elif 'access_token' in jsonResults.keys():
            logger.debug('Call successful!')
            logger.debug(jsonResults)
            return jsonResults
        elif 'error' in jsonResults.keys():
            logger.warn(
                f"Found error {jsonResults['error']} in response body.")
            raise Exception(jsonResults['error'])
        else:
            logger.warn(f"Error: can't parse JSON:\n{jsonResults}")
            raise Exception(500)

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
    def headers(self) -> dict:
        authorization: str
        if self.path == Path.AUTH:
            load_dotenv()
            authorization = f'Basic {getenv("BASIC_CREDENTIALS")}'
        else:
            authorization = f'Bearer {self.access_token}'
        return {
            'Authorization': authorization,
            'Content-Type': 'application/json'
        }

    def login(self, refresh_token):
        self.host = Host.PLATFORM
        self.path = Path.AUTH
        json = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        results = self._post(json=json)
        return results
