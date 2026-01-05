"""
модуль auth (система аутентификации и управления пользователями игры)

основные задачи модуля:
    - хранение и загрузка списка зарегистрированных пользователей
    - регистрация новых игроков
    - проверка логина и пароля при входе
    - управление текущей сессией (active user)
    - активация сохранённых артефактов игрока при авторизации

структура работы:
    1) при старте гарантируется существование каталога storage/
       и файла storage/users.txt

    2) пользователь может:
        - зарегистрироваться (register_user)
        - выполнить вход (login_user)

    3) после успешного входа:
        - имя игрока сохраняется как текущий пользователь сессии
        - загружаются его персональные артефакты
        - выполняется их активация в рамках текущей игры

вспомогательные функции:
    set_current_username / get_current_username —
        управление текущим активным пользователем

    load_users / save_user —
        работа с файлом хранения пользователей

совместимость:
    функция get_or_create_user сохранена для старых версий проекта
    и выполняет регистрацию или вход в зависимости от наличия игрока
"""


import os

from pathlib import Path
from artifacts import show_artifacts_on_login
from artifact_storage import load_player_artifacts_objects


USERS_FILE = Path("storage/users.txt")


def ensure_users_file():
    """
    гарантирует существование файла с пользователями

    parameters:
        none

    returns:
        none
    """
    # создаём директорию storage при необходимости
    os.makedirs("storage", exist_ok=True)

    # создаём файл, если его ещё нет
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8"):
            pass


def validate_credentials(login, password):
    """
    выполняет простую валидацию логина и пароля

    parameters:
        login — введённый логин
        password — введённый пароль

    returns:
        bool — True если данные допустимы, иначе False
    """

    if not login:
        print("логин не может быть пустым")
        return False

    if not password:
        print("пароль не может быть пустым")
        return False

    if " " in login or " " in password:
        print("логин и пароль не должны содержать пробелы")
        return False

    if len(password) < 3:
        print("пароль слишком короткий (минимум 3 символа)")
        return False

    return True


# текущий пользователь с активной сессией
CURRENT_USER = None


def set_current_username(username):
    """
    устанавливает имя текущего пользователя сессии
    """
    global CURRENT_USER
    CURRENT_USER = username


def get_current_username():
    """
    возвращает имя текущего пользователя
    или None, если вход ещё не выполнен
    """
    return CURRENT_USER


def load_users():
    """
    загружает пользователей из файла

    parameters:
        none

    returns:
        dict — словарь формата {логин: пароль}
    """

    ensure_users_file()

    users = {}

    with open(USERS_FILE, "r", encoding="utf-8") as f:

        for line in f:
            line = line.strip()

            if not line:
                continue

            parts = line.split(" ")

            # защита от кривых строк
            if len(parts) != 2:
                continue

            login, password = parts

            users[login] = password

    return users


def save_user(login, password):
    """
    добавляет нового пользователя в файл

    parameters:
        login — логин нового пользователя
        password — пароль нового пользователя

    returns:
        none — запись выполняется в файл
    """

    with open(USERS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{login} {password}\n")


def register_user(login, password):
    """
    регистрирует нового пользователя

    parameters:
        login — выбранный логин
        password — выбранный пароль

    returns:
        bool — True если регистрация прошла успешно
    """

    if not validate_credentials(login, password):
        return False

    users = load_users()

    if login in users:
        print("пользователь с таким логином уже существует")
        return False

    save_user(login, password)
    print("новый пользователь зарегистрирован")

    return True


def authenticate_user(login, password):
    """
    проверяет логин и пароль существующего пользователя

    parameters:
        login — введённый логин
        password — введённый пароль

    returns:
        bool — True если вход выполнен успешно
    """

    users = load_users()

    if login not in users:
        print("пользователь не найден")
        return False

    if users[login] != password:
        print("неверный пароль")
        return False

    return True


def login_user(login, password):
    """
    выполняет вход в игру и активирует сохранённые артефакты игрока

    parameters:
        login — логин игрока
        password — пароль игрока

    returns:
        bool — True если вход выполнен успешно
    """

    if not authenticate_user(login, password):
        return False

    print("успешный вход в игру")

    set_current_username(login)

    artifacts = load_player_artifacts_objects(login)

    if artifacts:
        print("\nактивация сохранённых артефактов...")
        show_artifacts_on_login(artifacts)

    else:
        print("\nу игрока пока нет сохранённых артефактов")

    return True


def get_or_create_user(login, password):
    """
    устаревшая совместимая обёртка

    parameters:
        login — логин пользователя
        password — пароль пользователя

    returns:
        bool — True если пользователь успешно зарегистрирован или вошёл
    """

    users = load_users()

    if login not in users:
        return register_user(login, password)

    return login_user(login, password)
