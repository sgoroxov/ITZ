"""
модуль aryefacts_hooks (триггеры выдачи игровых артефактов (достижений))

назначение:
    — модуль не содержит основной игровой логики
    — функции вызываются из сюжетных веток
    — каждая функция реагирует на конкретное игровое событие
    — при выполнении условия выдаётся артефакт текущему игроку

основные правила:
    — проверки не изменяют игровое состояние
    — функции не влияют на баланс и исход событий
    — только фиксируют факт достижения прогресса

интерфейс:
    try_first_deal(player, username)
    try_ten_deals(player, username)
    try_big_profit(amount, username)
    try_long_project(deal, username)
    try_risky_abort(username)
    try_lucky_event(username)

связанные модули:
    artifact_storage — хранение и загрузка артефактов
    artifacts        — описание артефактов
"""


from artifact_storage import give_artifact


def try_first_deal(player, username):
    """
    Выдаётся после первой успешной сделки
    """
    if len(player.completed_deals) == 1:
        give_artifact(username, "first_deal")


def try_ten_deals(player, username):
    """
    Выдаётся при достижении 10 завершённых сделок
    """
    if len(player.completed_deals) >= 10:
        give_artifact(username, "ten_deals")


def try_big_profit(amount, username):
    """
    Выдаётся за прибыль от сделки > 100000 ₽
    """
    if amount >= 100_000:
        give_artifact(username, "big_profit")


def try_long_project(deal, username):
    """
    Выдаётся за успешное завершение долгого проекта (тип 3)
    """
    if deal.type == 3:
        give_artifact(username, "long_project")


def try_risky_abort(username):
    """
    Проект был досрочно продан с риском
    """
    give_artifact(username, "risky_abort")


def try_lucky_event(username):
    """
    Сработало редкое положительное событие
    """
    give_artifact(username, "lucky_event")
