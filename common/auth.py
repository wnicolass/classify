from passlib.context import CryptContext

hash_context = CryptContext(schemes = ['bcrypt'], deprecated = 'auto')

def check_password(password: str, hashed_password: str) -> bool:
    return hash_context.verify(password, hashed_password)

def hash_password(password: str) -> str:
    return hash_context.hash(password)