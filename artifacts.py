"""
Модуль artefacts (системы достижений игры)

Назначение:
    В модуле описываются игровые артефакты — коллекционные достижения
    игрока, которые выдаются при выполнении особых условий в сюжетных ветках.

Структура:
    • класс Artifact — описывает единичный артефакт
    • словарь ARTIFACTS — реестр всех доступных достижений
    • get_artifact_by_id() — безопасный доступ к объекту по ID
    • show_artifacts_on_login() — вывод уже полученных артефактов

Использование:
    Артефакты не влияют на игровой процесс напрямую,
    но служат системой прогресса и наградой за ключевые действия игрока.

    Получение артефактов выполняется через модуль artifacts_hooks.py,
    а сохранение — через artifact_storage.py.
"""


class Artifact:
    """
    Класс единичного артефакта (достижения)

    id   — программный идентификатор
    name — отображаемое название
    desc — описание условия получения
    """

    def __init__(self, artifact_id, name, desc):
        self.artifact_id = artifact_id
        self.name = name
        self.desc = desc


# РЕГИСТР ДОСТУПНЫХ АРТЕФАКТОВ
ARTIFACTS = {

    "first_deal": Artifact(
        "first_deal",
        "Первая кровь",
        "Совершена первая успешная сделка"
    ),

    "ten_deals": Artifact(
        "ten_deals",
        "Настоящий перекуп",
        "Завершено 10 сделок"
    ),

    "big_profit": Artifact(
        "big_profit",
        "Жирный куш",
        "Получена прибыль выше 100000 ₽"
    ),

    "long_project": Artifact(
        "long_project",
        "Терпеливый механик",
        "Успешно завершён долгий проект"
    ),

    "risky_abort": Artifact(
        "risky_abort",
        "На грани",
        "Проект досрочно продан с риском"
    ),

    "lucky_event": Artifact(
        "lucky_event",
        "Космическая удача",
        "Сработало редкое событие улучшения проекта"
    ),
}


def get_artifact_by_id(id_):
    """
    Возвращает объект артефакта по ID,
    либо None, если такого ID нет в реестре
    """
    return ARTIFACTS.get(id_)


def show_artifacts_on_login(artifacts):
    """
    выводит список полученных артефактов при входе в игру

    parameters:
        artifacts — список объектов Artifact
    """

    if not artifacts:
        return

    print("\nполученные артефакты игрока:")

    for art in artifacts:
        print(f" • {art.name} — {art.desc}")
