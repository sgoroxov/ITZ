"""
save_system.py

модуль отвечает за сохранение и загрузку
прогресса игрока через систему артефактов

в сохранении хранятся:
    список идентификаторов полученных артефактов
"""

from artifact_storage import (
    load_artifacts_ids,
    save_artifacts_ids,
    load_player_artifacts_objects
)


def load_player_progress():
    """
        загружает артефакты игрока из сохранения

        returns:
            list — список объектов артефактов игрока
    """

    return load_player_artifacts_objects()


def save_player_artifacts(artifacts):
    """
        сохраняет обновлённый список артефактов игрока

        parameters:
            artifacts — список объектов артефактов

        returns:
            none — идентификаторы записываются в файл
    """

    ids = [a.id for a in artifacts]
    save_artifacts_ids(ids)

    print("\nпрогресс сохранён — артефакты записаны")
