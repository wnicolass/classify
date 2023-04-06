from asyncinit import asyncinit
from typing import Any
from common.auth import get_current_auth_user

@asyncinit
class ViewModel(dict):
    async def __init__(self, *args, **kargs):
        user = await get_current_auth_user()
        all = {
            'success': None,
            'success_msg': None,
            'error': None,
            'error_msg': None,
            'user_id': user.user_id if user else None,
            'is_logged_in': user is not None,
            'username': user.username.split(' ')[0] if user else None
        }
        all.update(kargs)
        super().__init__(self, *args, **all)

    def __getattr__(self, name: str) -> Any:
        return self[name]
    
    def __setattr__(self, name: str, value: Any) -> Any:
        self[name] = value
