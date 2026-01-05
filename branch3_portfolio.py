"""
ветка 3 —
    инвестиционный портфель / долгие проекты / свапы

основная идея ветки:
    - игрок ведёт несколько долгих проектов одновременно
    - деньги замораживаются на время работ (freeze_turns)
    - каждый проект может дать бонус / задержку
    - соперник также выполняет проекты параллельно
    - рынок играет через редкие события

игровая модель:
    - проекты имеют тип, стоимость и длительность сборки
    - прибыль зависит от диапазона profit + бонусов события
    - завершённые проекты автоматически продаются
    - игрок может досрочно выйти из проекта с убытком
    - в портфеле можно запускать несколько машин

интеграция достижений:
    — first_deal         — первая успешная сделка
    — ten_deals          — 10 завершённых сделок
    — big_profit         — прибыль выше 100000 ₽
    — long_project       — завершён долгий проект (тип 3)
    — risky_abort        — досрочная продажа проекта
    — lucky_event        — сработало редкое позитивное событие

унифицированные сущности и функции:
    create_rival           — создание соперника ветки
    roll_event             — расчёт редких событий проекта
    advance_turn           — продвижение времени на один ход
    finish_ready_projects  — завершение готовых проектов
    start_project          — запуск нового проекта
    abandon_project        — досрочная продажа проекта
    play_branch3           — основной цикл ветки
"""


import random
from player import Deal, Rival, attach_portfolio
from player import check_force_exit
from auth import get_current_username
from artifacts_hooks import (
    try_first_deal,
    try_ten_deals,
    try_big_profit,
    try_long_project,
    try_risky_abort,
    try_lucky_event
)

PROJECT_TYPES = {
    1: {
        "name": "быстрый проект — лёгкая доработка",
        "buy": (60_000, 90_000),
        "profit": (8000, 25000),
        "freeze": (1, 2)
    },
    2: {
        "name": "средний проект — восстановление / частичный ремонт",
        "buy": (90_000, 140_000),
        "profit": (20000, 50000),
        "freeze": (2, 4)
    },
    3: {
        "name": "долгий проект — свап / крупная сборка",
        "buy": (120_000, 200_000),
        "profit": (45000, 120000),
        "freeze": (3, 6)
    }
}


# СОПЕРНИК
def create_rival():
    styles = {
        0: "осторожный проект-мейкер",
        1: "опытный мастер рынка",
        2: "агрессивный свап-энтузиаст"
    }

    style_id = random.randint(0, 2)

    rival = Rival(
        name=styles[style_id],
        style=style_id,
        mode=3,
        budget=random.randint(150_000, 300_000)
    )

    attach_portfolio(rival)

    print("\nна рынке проектов появился соперник:")
    print(rival.name)
    print("стартовый бюджет соперника:", rival.budget)

    return rival


# СЛУЧАЙНЫЕ СОБЫТИЯ
def roll_event(deal, username):
    """
    редкие события проекта
    """

    roll = random.random()

    # супер-удача (редко)
    if roll < 0.06:
        deal.freeze_turns = max(1, deal.freeze_turns - 1)
        deal.bonus_profit = random.randint(15000, 40000)

        print("\n[редкое событие] нашёлся коллекционер!")
        print("проект ускорен, потенциальная прибыль выросла")

        try_lucky_event(username)

        return "boost"

    # неприятность (умеренная)
    if roll < 0.18:
        deal.freeze_turns += 1
        deal.bonus_profit = -random.randint(5000, 15000)

        print("\n[неожиданная проблема] сложности в процессе работ")
        print("срок увеличен, часть бюджета потеряна")

        return "delay"

    # без события
    return None


# ПРОГРЕСС ПРОЕКТОВ
def advance_turn(player, rival):
    """
    продвигает время на один ход
    """

    player.portfolio.advance_all()
    rival.portfolio.advance_all()

    finish_ready_projects(player, is_rival=False)
    finish_ready_projects(rival, is_rival=True)


def finish_ready_projects(entity, is_rival):
    """
    завершает готовые проекты игрока и соперника
    """

    for deal in list(entity.portfolio.deals):
        if not deal.is_ready():
            continue

        info = PROJECT_TYPES[deal.type]

        low, high = info["profit"]
        base_profit = random.randint(low, high)

        profit = base_profit + deal.bonus_profit

        # закрываем сделку
        entity.portfolio.finish(deal, (profit, profit))

        # начисляем прибыль
        entity.change_budget(profit)

        who = "соперника" if is_rival else "игрока"

        print(f"\n[проект завершён — {who}]")
        print("машина подготовлена и продана")
        print("результат сделки:", profit)
        print("текущий бюджет:", entity.budget)

        if not is_rival:
            username = get_current_username()

            # первая сделка / 10 сделок
            try_first_deal(entity, username)
            try_ten_deals(entity, username)

            # долгий проект
            try_long_project(deal, username)

            # крупная прибыль
            try_big_profit(profit, username)


# СОЗДАНИЕ ПРОЕКТА
def start_project(player, project_type):
    info = PROJECT_TYPES[project_type]

    price = random.randint(*info["buy"])
    freeze = random.randint(*info["freeze"])

    print("\nзапущен новый проект:")
    print(info["name"])
    print("стоимость покупки автомобиля:", price)
    print("предполагаемая длительность работ:", freeze, "ходов")

    player.change_budget(-price)

    deal = Deal(
        deal_type=project_type,
        buy_price=price,
        freeze_turns=freeze
    )

    deal.bonus_profit = 0

    deal.owner = player

    username = get_current_username()
    roll_event(deal, username)

    player.portfolio.add(deal)


# ДОСРОЧНЫЙ ВЫХОД ИЗ ПРОЕКТА
def abandon_project(player):
    """
    игрок может продать проект недособранным
    """

    if not player.portfolio.deals:
        print("\nу вас нет активных проектов")
        return

    print("\nвыберите проект для выхода:")

    for i, d in enumerate(player.portfolio.deals):
        info = PROJECT_TYPES[d.type]
        print(f"{i+1} — {info['name']} (ходов осталось: {d.freeze_turns})")

    idx = int(input("номер проекта: ")) - 1
    deal = player.portfolio.deals[idx]

    loss = random.randint(8000, 20000)

    print("\nпроект продан на стадии сборки")
    print("убыток:", loss)

    player.change_budget(-loss)
    player.portfolio.remove(deal)

    username = get_current_username()
    try_risky_abort(username)


# ОСНОВНАЯ ФУНКЦИЯ ВЕТКИ
def play_branch3(player):
    """
    Ветка 3 — инвестиционный портфель

    логика:
        — проекты живут циклами (ходами)
        — каждый ход может произойти событие
        — игрок управляет проектами в портфеле
        — соперник ведёт свои проекты параллельно

        принудительный выход:
            --  — завершить ветку
    """

    print("\n=== Ветка 3 — Инвестиционный портфель ===\n")

    # стартовые параметры ветки
    player.budget = 300_000
    player.win_target = 900_000

    print("стартовый бюджет:", player.budget)

    attach_portfolio(player)
    rival = create_rival()

    cycle = 0       # номер хода

    while True:

        cycle += 1
        print(f"\n--- ход портфеля {cycle} ---")

        advance_turn(player, rival)

        # проверка на проигрыш
        if player.check_over():
            return

        print("\nваше решение:")
        print("1 — начать новый проект")
        print("2 — продать незавершённый проект")
        print("3 — подождать продвижения работ")
        print("-- — выйти из ветки")

        action = input("\nвыбор: ").strip()

        # --- ПРИНУДИТЕЛЬНЫЙ ВЫХОД ---
        if action == "--":
            print("\nвы покинули ветку проектов…")
            return

        if action == "1":
            print("\nвыберите тип проекта:")
            print("1 — быстрая доработка")
            print("2 — восстановление")
            print("3 — крупная сборка / свап")

            p = int(input("тип: "))
            start_project(player, p)
            continue

        if action == "2":
            abandon_project(player)
            continue

        if action == "3":
            print("\nвы решили просто продолжить работы")
            continue

        print("\nневерный ввод — ход пропущен")

        if check_force_exit():
            print("\nпринудительный выход из ветки…")
            return

        # точка выхода между циклами
        print("\nнажмите Enter — продолжить")
        print("-- — выйти из ветки")

        if input("действие: ").strip() == "--":
            print("\nвыход из ветки 3…")
            return
