"""
Система хранения артефактов игрока

ВНИМАНИЕ:
Артефакты являются ПЕРСОНАЛЬНЫМИ
и сохраняются отдельно для каждого пользователя.

Формат хранения:

    storage/artifacts_<username>.json

Хранилище содержит только список ID,
а объекты артефактов восстанавливаются через каталог ARTIFACTS.
"""

import os
import json

from artifacts import get_artifact_by_id


STORAGE_DIR = "storage"


def ensure_storage_dir():
    """
    Гарантирует существование директории хранения артефактов
    """
    os.makedirs(STORAGE_DIR, exist_ok=True)


def get_user_file(username):
    """
    Возвращает путь к файлу хранилища артефактов
    для конкретного пользователя
    """
    ensure_storage_dir()
    return os.path.join(STORAGE_DIR, f"artifacts_{username}.json")


# ============ ЗАГРУЗКА ============

def load_artifacts_ids(username):
    """
    Загружает список ID артефактов пользователя

    возвращает:
        list[str] — если файл существует
        []        — если файл отсутствует или повреждён
    """

    file_path = get_user_file(username)

    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data if isinstance(data, list) else []

    except Exception:
        return []


# ============ СОХРАНЕНИЕ ============

def save_artifacts_ids(username, ids):
    """
    Перезаписывает файл списка артефактов пользователя
    """

    file_path = get_user_file(username)

    ensure_storage_dir()

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(ids, f, ensure_ascii=False, indent=4)


# ============ ВЫДАЧА АРТЕФАКТА ============

def give_artifact(username, artifact_id):
    """
    Выдаёт артефакт конкретному игроку,
    если раньше он его не получал

    возвращает:
        True  — если артефакт выдан впервые
        False — если уже был получен
    """

    ids = load_artifacts_ids(username)

    # Уже есть — повторно не выдаём
    if artifact_id in ids:
        return False

    artifact = get_artifact_by_id(artifact_id)
    if not artifact:
        return False

    ids.append(artifact_id)
    save_artifacts_ids(username, ids)

    print("\n[достижение получено]")
    print(artifact.name)
    print(artifact.desc)

    return True


# ============ ВОССТАНОВЛЕНИЕ ОБЪЕКТОВ ============

def load_player_artifacts_objects(username):
    """
    Загружает артефакты игрока как ОБЪЕКТЫ,
    а не просто ID

    используется для отображения коллекции игрока
    """

    ids = load_artifacts_ids(username)
    result = []

    for a_id in ids:
        art = get_artifact_by_id(a_id)
        if art:
            result.append(art)

    return result

def grant_artifact(username, artifact):
    """
    КОСТЫЛЬ (не успеваю по времени грамотно завершить)
    теперь система хранения — по ID и на пользователя.

    Данная функция принимает объект артефакта
    и выполняет корректную выдачу.
    """

    if not artifact:
        return False

    return give_artifact(username, artifact.id)