"""
модуль отвечает за сохранение и загрузку
прогресса игрока через систему артефактов

основная идея хранения прогресса:
    — у каждого пользователя свой набор артефактов
    — артефакты сохраняются по имени аккаунта
    — при входе они подгружаются и активируются

функции модуля:
    load_player_progress   — загрузить артефакты текущего игрока
    save_player_artifacts  — сохранить обновлённый список артефактов
"""


from auth import get_current_username
from artifact_storage import (
    save_artifacts_ids,
    load_player_artifacts_objects
)


def load_player_progress():
    """
    загружает прогресс игрока (его артефакты)
    теперь — персонально для текущего пользователя
    """

    username = get_current_username()

    if not username:
        return []

    return load_player_artifacts_objects(username)


def save_player_artifacts(artifacts):
    """
        сохраняет обновлённый список артефактов игрока

        parameters:
            artifacts — список объектов артефактов

        returns:
            none — идентификаторы записываются в файл
    """
    username = get_current_username()
    if not username:
        return

    ids = [a.id for a in artifacts]
    save_artifacts_ids(username, ids)

    print("\nпрогресс сохранён — артефакты записаны")
