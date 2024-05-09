import hashlib


def read_secret_key() -> tuple:
    # Чтение секрета из файла
    # возвращаем tuple из ошибки и ответа
    try:
        f = open("secret_key", "r")
        key = f.read()
        return False, key
    except FileNotFoundError:
        return True, "File secret_key doesn't exist"

def hash_password(password_for_hash: str) -> str:
    "Переводит пароль в hash"
    password_bytes = password_for_hash.encode('utf-8')
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()