"""
Игровые триггеры выдачи артефактов

Данный модуль НЕ содержит логики игры,
а только реагирует на события,
которые вызываются из сюжетных веток.
"""

from artifact_storage import give_artifact
from artifacts import ARTIFACTS


# ============ БАЗОВЫЕ ДОСТИЖЕНИЯ ============

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


# ============ ВЕТКА 3 — ДОЛГИЕ ПРОЕКТЫ ============

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
    (ускорение проекта / рост прибыли)
    """
    give_artifact(username, "lucky_event")
