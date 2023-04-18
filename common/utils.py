from datetime import date
import regex

MIN_DATE = date.fromisoformat('1920-01-01')

def is_valid_iso_date(iso_date: str) -> bool:
    try:
        date.fromisoformat(iso_date)
    except ValueError:
        return False
    else:
        return True
    
def is_valid_birth_date(birth_date: str) -> bool:
        return (is_valid_iso_date(birth_date) and date.fromisoformat(birth_date) >= MIN_DATE and date.fromisoformat(birth_date) <= date.today())

def make_test_regex_fn(reg: str):
    compiled_regex = regex.compile(reg)
    def test_regex_fn(value: str) -> bool:
        return bool(regex.fullmatch(compiled_regex, value))
    return test_regex_fn

def handle_phone(phone_number: str) -> str:
    return regex.sub(r'\+|\s', '', phone_number.strip())

def add_plus_sign_to_phone_number(phone_number: str) -> str:
    if phone_number is not None:    
        if len(phone_number) == 12:
            phone_number = "+" + phone_number
    return phone_number

is_valid_email = make_test_regex_fn(
    r"[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*"
)

is_valid_password = make_test_regex_fn(
     r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[~`!@#$%^&*()_\-+={[}\]|\\:;"\'<,>.?/]).{6,20}'
)

is_valid_username = make_test_regex_fn(
    r'^(\p{L}{2,}\p{Zs}?)+$'
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