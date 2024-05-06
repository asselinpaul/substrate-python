import logging
import platform
from typing import Any, Dict, Union, Optional
from typing_extensions import Literal

import httpx
import distro

from ._version import __version__

log: logging.Logger = logging.getLogger(__name__)


class OtherPlatform:
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return f"Other:{self.name}"


Platform = Union[
    OtherPlatform,
    Literal[
        "MacOS",
        "Linux",
        "Windows",
        "FreeBSD",
        "OpenBSD",
        "iOS",
        "Android",
        "Unknown",
    ],
]


class OtherArch:
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return f"other:{self.name}"


Arch = Union[OtherArch, Literal["x32", "x64", "arm", "arm64", "unknown"]]


def get_platform() -> Platform:
    system = platform.system().lower()
    platform_name = platform.platform().lower()
    if "iphone" in platform_name or "ipad" in platform_name:
        return "iOS"
    if system == "darwin":
        return "MacOS"
    if system == "windows":
        return "Windows"
    if "android" in platform_name:
        return "Android"
    if system == "linux":
        distro_id = distro.id()
        if distro_id == "freebsd":
            return "FreeBSD"
        if distro_id == "openbsd":
            return "OpenBSD"
        return "Linux"
    if platform_name:
        return OtherPlatform(platform_name)
    return "Unknown"


def get_architecture() -> Arch:
    python_bitness, _ = platform.architecture()
    machine = platform.machine().lower()
    if machine in ("arm64", "aarch64"):
        return "arm64"
    if machine == "arm":
        return "arm"
    if machine == "x86_64":
        return "x64"
    if python_bitness == "32bit":
        return "x32"
    if machine:
        return OtherArch(machine)
    return "unknown"


class APIResponse:
    def __init__(
        self,
        status_code: int,
        json: Any,
        headers: Any,
        request: Dict[str, Any],
    ):
        self._status_code = status_code
        self._json = json
        self._headers = headers
        self._request = request

    @property
    def json(self) -> Optional[Dict[str, Any]]:
        return self._json

    @property
    def headers(self) -> Any:
        return self._headers

    @property
    def request(self) -> Dict[str, Any]:
        return self._request

    @property
    def status_code(self) -> int:
        return self._status_code


class APIClient:
    _api_key: str
    _base_url: str
    _client: httpx.Client
    _async_client: httpx.AsyncClient
    _version: str
    _backend: str
    _additional_headers: Dict[str, Any]

    def __init__(
        self,
        api_key: str,
        base_url: str,
        backend: str,
        timeout: float,
        additional_headers: Dict[str, Any] = {},
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._backend = backend
        self._additional_headers = additional_headers
        self._client = httpx.Client(timeout=timeout, follow_redirects=True)
        self._async_client = httpx.AsyncClient(timeout=timeout, follow_redirects=True)
        self._version = __version__

    @property
    def user_agent(self) -> str:
        return f"{self.__class__.__name__}/Python {self._version}"

    @property
    def auth_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self._api_key}"}

    @property
    def platform_headers(self) -> Dict[str, str]:
        version_parts = self._version.split(".")
        date = version_parts[0][-8:]
        api_version = f"{date[:4]}-{date[4:6]}-{date[6:]}"
        return {
            "X-Substrate-Lang": "python",
            "X-Substrate-Package-Version": self._version,
            "X-Substrate-Version": api_version,
            "X-Substrate-OS": str(get_platform()),
            "X-Substrate-Arch": str(get_architecture()),
            "X-Substrate-Runtime": platform.python_implementation(),
            "X-Substrate-Runtime-Version": platform.python_version(),
        }

    @property
    def default_headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
            "X-Substrate-Backend": self._backend,
            **self.platform_headers,
            **self.auth_headers,
            **self._additional_headers,
        }

    def post_compose(self, dag: Dict[str, Any]) -> APIResponse:
        url = f"{self._base_url}/compose"
        body = {"dag": dag}
        http_response = self._client.post(url, headers=self.default_headers, json=body)
        _json = None
        try:
            _json = http_response.json()
        except Exception as exc:
            log.debug("Could not read JSON from response data due to %s - %s", type(exc), exc)
        res = APIResponse(
            status_code=http_response.status_code,
            json=_json,
            headers=http_response.headers,
            request=body,
        )
        return res

    async def async_post_compose(self, dag: Dict[str, Any]) -> APIResponse:
        url = f"{self._base_url}/compose"
        body = {"dag": dag}
        http_response = await self._async_client.post(url, headers=self.default_headers, json=body)
        _json = None
        try:
            _json = http_response.json()
        except Exception as exc:
            log.debug("Could not read JSON from response data due to %s - %s", type(exc), exc)
        res = APIResponse(
            status_code=http_response.status_code,
            json=_json,
            headers=http_response.headers,
            request=body,
        )
        return res
