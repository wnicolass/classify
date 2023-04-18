from datetime import date
import re
from typing import List

MIN_DATE = date.fromisoformat('1920-01-01')

def get_min_max_price(ads: List):
    max = 0
    min = ads[0].price
    for ad in ads:
        if min > ad.price:
            min = ad.price
        elif max < ad.price:
            max = ad.price
    return min, max 

def is_valid_iso_date(iso_date: str) -> bool:
    try:
        date.fromisoformat(iso_date)
    except ValueError:
        return False
    else:
        return True
    
def is_valid_birth_date(birth_date: str) -> bool:
        return (is_valid_iso_date(birth_date) and date.fromisoformat(birth_date) >= MIN_DATE and date.fromisoformat(birth_date) <= date.today())

def make_test_regex_fn(regex: str):
    compiled_regex = re.compile(regex)
    def test_regex_fn(value: str) -> bool:
        return bool(re.fullmatch(compiled_regex, value))
    return test_regex_fn

def handle_phone(phone_number: str) -> str:
    return re.sub(r'\+|\s', '', phone_number.strip())

is_valid_email = make_test_regex_fn(
    r"[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*"
)

is_valid_password = make_test_regex_fn(
     r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[~`!@#$%^&*()_\-+={[}\]|\\:;"\'<,>.?/]).{6,20}'
)

is_valid_username = make_test_regex_fn(
    r'^(?!.*\d)(?!.*[~`!@#$%^&*()_\-+={[}\]|\\:;"\'<,>.?/]).{2,}$'
)

is_valid_txt_field = make_test_regex_fn(
    r'^(?!.*[~`!@#$%^&*()_\-+={[}\]|\\:;"\'<,>.?/]{4,}).*$'
)

is_valid_price = make_test_regex_fn(
    r'^(?!0,0\d)(\d{1,6},\d{2})$'
)

is_valid_phone_number = make_test_regex_fn(
    r'(^(\d\s?){9}$)|(^\+(\d\s?){12}$)'
)