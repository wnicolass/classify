from typing import Any
from common.auth import get_current_auth_user

class ViewModel(dict):
    def __init__(self, *args, **kargs):
        user_id = get_current_auth_user()
        all = {
            'error': None,
            'error_msg': None,
            'user_id': user_id,
            'is_logged_in': user_id is not None
        }
        all.update(kargs)
        super().__init__(self, *args, **all)

    def __getattr__(self, name: str) -> Any:
        return self[name]
    
    def __setattr__(self, name: str, value: Any) -> Any:
        self[name] = value
