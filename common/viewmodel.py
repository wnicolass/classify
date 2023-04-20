from asyncinit import asyncinit
from typing import Any
from common.auth import get_current_user

"""
    The ViewModel is responsable to prepare (and sometimes get) 
    the data that will be used in the view. These data can come 
    from different data sources, so they can need to be validated 
    and adapted.

    We are storing some information that can be useful in all 
    endpoints that returns a template as response, such as 
    the current user, his profile_image, his username.

    Also, is worth to know that each time we instantiate a ViewModel
    we have a user model instance inside of it too. So, we have access
    to all user properties.
    Example:

    vm = await ViewModel()

    vm.user.user_id
    vm.user.username
    vm.user.some_property_that_can_be_found_on_the_user_model
"""
@asyncinit
class ViewModel(dict):
    async def __init__(self, *args, **kargs):
        user = await get_current_user()
        all = {
            'success': None,
            'success_msg': None,
            'error': None,
            'error_msg': None,
            'user_id': user.user_id if user else None,
            'is_logged_in': user is not None,
            'username': user.username.split(' ')[0] if user else None,
            'profile_image': user.profile_image_url or '/public/assets/images/author-1.jpg' if user else None,
            'user': user
        }
        all.update(kargs)
        super().__init__(self, *args, **all)

    def __getattr__(self, name: str) -> Any:
        return self[name]
    
    def __setattr__(self, name: str, value: Any) -> Any:
        self[name] = value
