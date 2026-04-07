from shared.lib.basicError.src.main import BasicError
from shared.lib.basicError.src.main import errorWrapper
import requests
from typing import Any, Tuple, Optional

# TODO: エラーハンドリング
class Client:

    # @errorWrapper("InvalidFormat")
    def __init__(self, key: str = None):
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type" : "application/json",
            "Accept": "application/json"
        })
        if key:
            self.session.headers.update({
                "Authorization": f"Bearer {key}"
            })
            
    @errorWrapper("NetworkConnectionFailed")
    def get(self, url:str, params:dict = None) -> Tuple[bool, Any, Optional[BasicError]]:
        try:
            response = self.session.get(url, params=params)
            return True, self._handle_response(response), None
        except requests.exceptions.RequestException as e:
            return False, None, BasicError("InterServiceAuthError", str(e))
    
    @errorWrapper("NetworkConnectionFailed")
    def post(self, url: str, data: dict = None) -> Tuple[bool, Any, Optional[BasicError]]:
        try:
            response = self.session.post(url, json=data)
            return True, self._handle_response(response), None
        except requests.exceptions.RequestException as e:
            return False, None, BasicError("InterServiceAuthError", str(e))
    
    @errorWrapper("NetworkConnectionFailed")
    def put(self, url:str, data:dict = None) -> Tuple[bool, Any, Optional[BasicError]]:
        try:
            response = self.session.put(url, json=data)
            return True, self._handle_response(response), None
        except requests.exceptions.RequestException as e:
            return False, None, BasicError("InterServiceAuthError", str(e))
        
    
    @errorWrapper("NetworkConnectionFailed")
    def delete(self, url: str, data: dict = None) -> Tuple[bool, Any, Optional[BasicError]]:
        try:
            response = self.session.delete(url, json=data)
            return True, self._handle_response(response), None
        except requests.exceptions.RequestException as e:
            return False, None, BasicError("InterServiceAuthError", str(e))

    
    
    def _handle_response(self, response: requests.Response) -> Tuple[bool, Any, Optional[BasicError]]:
        try:
            response.raise_for_status()
            data = response.json()
            return True, data, None
        except requests.exceptions.HTTPError as e:
            # raise RuntimeError(f"API Error {response.status_code}: {response.text}") from e
            status = response.status_code
            # レスポンス内容に応じてエラーキーをマッピング（例）
            if status == 400:
                return False, None, BasicError("MissingRequiredParameter")
            elif status == 401:
                return False, None, BasicError("AuthenticationFailed")
            elif status == 403:
                return False, None, BasicError("InsufficientPermissions")
            elif status == 404:
                return False, None, BasicError("RecordNotFound")
            elif status == 409:
                return False, None, BasicError("DuplicateInput")
            elif status == 429:
                return False, None, BasicError("RequestLimitExceeded")
            elif 500 <= status < 600:
                return False, None, BasicError("ServerInternalException")
            else:
                return False, None, BasicError("UnknownError")
        except ValueError:
            # raise RuntimeError("Invalid JSON response")
            return False, None, BasicError("InvalidFormat")
        except Exception:
            # 想定外の例外
            return False, None, BasicError("UnknownError")