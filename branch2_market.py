"""
ветка 2 —
    экономическая ветка перепродажи автомобилей

модель ветки:
    - покупка автомобиля замораживает часть бюджета
    - сделка может зависнуть на несколько ходов
    - игрок принимает решение: ждать, продавать в ноль или срочно сливать
    - параллельно развивается линия соперника на рынке
    - результат сделки зависит от состояния рынка и силы конкурента

игровые сущности:
    Rival — соперник-перекуп с собственным бюджетом и стилем игры
    игрок — управляет бюджетом и принятием решений по сделке

достижения (артефакты):
    - первая успешная сделка
    - 10 завершённых сделок
    - крупная прибыль
    - рискованная досрочная продажа
    - долгий проект / затянувшаяся сделка

унифицированные функции:
    generate_rival   — создать соперника и его параметры
    show_hint        — вывести психологическое давление соперника
    calc_profit      — рассчитать прибыль сделки
    apply_profit     — применить финансовый результат
    finalize_rival   — завершить сделку соперника
    play_branch2     — основной игровой цикл ветки
"""


import random
from player import Rival
from player import check_force_exit
from auth import get_current_username
from artifacts_hooks import (
    try_first_deal,
    try_ten_deals,
    try_big_profit,
    try_long_project,
    try_risky_abort,
)


RIVAL_HINTS = {
    0: [
        "конкурент замечает: рынок начинает проседать",
        "соперник говорит: такие машины могут застояться"
    ],
    1: [
        "конкурент говорит: рынок непредсказуем",
        "он отмечает: иногда ожидание оправдывается"
    ],
    2: [
        "соперник давит: время — деньги, рынок не ждёт",
        "конкурент бросает фразу: я бы уже слил и взял другую"
    ]
}


def generate_rival():
    """
    создаёт соперника для рыночной сделки

    returns:
        Rival — npc соперник
    """

    styles = {
        0: ("осторожный перекуп", (-5000, 20000)),
        1: ("обычный игрок рынка", (-15000, 40000)),
        2: ("агрессивный риск-перекуп", (-40000, 90000))
    }

    style_id = random.randint(0, 2)
    name, profit_range = styles[style_id]

    rival = Rival(
        name=name,
        budget=random.randint(120_000, 190_000),
        style=style_id,
        mode=2,
        profit_range=profit_range
    )

    print("\nна рынке:", name)
    print("стартовый бюджет соперника:", rival.budget)

    return rival


def show_hint(rival):
    """
    иногда выводит психологическое давление соперника
    """

    if random.random() > 0.35:
        return

    phrase = random.choice(RIVAL_HINTS[rival.style])

    print(phrase)


def calc_profit(car_quality):
    """
    рассчитывает итоговую прибыль сделки игрока
    """

    profit_ranges = {
        0: (-15000, 5000),
        1: (-5000, 12000),
        2: (3000, 25000),
        3: (10000, 40000),
        4: (25000, 70000)
    }

    low, high = profit_ranges[car_quality]
    return random.randint(low, high)


def apply_profit(player, rival, amount):
    """
    применяет прибыль / убыток к бюджету игрока
    с учётом влияния соперника на рынок
    """

    # соперник сильнее → давит рынок
    if rival.budget > player.budget:
        print("\nсоперник переиграл вас (-15%)")
        amount = int(amount * 0.85)

    # игрок богаче → действует увереннее
    elif rival.budget < player.budget:
        print("\nрынок на вашей стороне (+10%)")
        amount = int(amount * 1.10)

    print("итог сделки:", amount)

    player.change_budget(amount)


def finalize_rival(rival):
    """
    завершает сделку соперника
    соперник влияет на рынок и может обогнать игрока
    """

    low, high = rival.profit_range
    amount = random.randint(low, high)

    rival.finalize_profit(amount)

    if amount > 30000:
        print("соперник усилил позиции на рынке")
    elif amount < -20000:
        print("соперник провалил сделку и теряет влияние")


def play_branch2(player):
    """
    запуск ветки перепродажи автомобилей

    логика:
        - игроку показывается найденный автомобиль
        - отображается цена и риск заморозки сделки
        - игрок решает, входить в сделку или пропустить
        - после покупки запускается механика сделки

    принудительный выход:
        --  — выход из ветки между сделками
    """

    print("\n=== Ветка 2 — Перекупские сделки на рынке ===\n")

    username = get_current_username()

    player.budget = 150_000
    player.win_target = 350_000

    print("стартовый бюджет ветки 2:", player.budget)

    while True:

        print("\n--- новый поиск автомобиля")

        # качество машины
        car_quality = random.randint(0, 4)

        quality_names = {
            0: "убитая машина с рисками",
            1: "уставший бюджетный вариант",
            2: "средний рынок",
            3: "ухоженный автомобиль",
            4: "редкий ликвидный экземпляр"
        }

        freeze_chance = {
            0: 0.25,
            1: 0.45,
            2: 0.65,
            3: 0.80,
            4: 0.92
        }

        freeze_durations = {
            0: (0, 1),
            1: (1, 2),
            2: (1, 3),
            3: (2, 4),
            4: (3, 5)
        }

        chance = freeze_chance[car_quality]
        base_price = random.randint(80_000, 160_000)

        print("\nНайдена машина:")
        print("тип:", quality_names[car_quality])
        print("цена:", base_price)
        print("шанс заморозки сделки:", int(chance * 100), "%")

        print("\nваше решение:")
        print("1 — купить автомобиль и войти в сделку")
        print("2 — пропустить и искать дальше")
        print("-- — выйти из ветки")

        choice = input("\nвыбор: ").strip()

        if choice == "--":
            print("\nвыход из ветки 2")
            return

        if choice == "2":
            print("\nвы пропустили этот вариант — поиск продолжается")
            continue

        if choice != "1":
            print("\nневерный ввод — этот вариант пропущен")
            continue

        # покупка автомобиля

        print("\nпокупка автомобиля...")
        player.change_budget(-base_price)

        if player.check_over():
            return

        rival = generate_rival()

        # сделка не зависла
        if random.random() > chance:
            print("\nпокупатель найден сразу — сделка не зависла")

            profit = calc_profit(car_quality)
            apply_profit(player, rival, profit)

            if player.check_win():
                return

            finalize_rival(rival)

        else:
            # сделка зависла
            min_f, max_f = freeze_durations[car_quality]
            freeze_turns = random.randint(min_f, max_f)

            print(f"\nсделка зависла на {freeze_turns} хода(ов)")

            for step in range(freeze_turns):

                print(f"\n--- ход сделки {step + 1}")

                show_hint(rival)

                print("\nваше решение:")
                print("1 — продолжать ждать")
                print("2 — продать в ноль")
                print("3 — срочно слить в минус")
                print("-- — выйти из ветки после сделки")

                action = input("выбор: ").strip()

                if action == "--":
                    print("\nпринудительный выход из ветки")
                    return

                if action == "2":
                    print("\nпродажа без прибыли")
                    player.change_budget(base_price)
                    break

                if action == "3":
                    loss = random.randint(5000, 20000)
                    print("срочная продажа в минус на", loss)
                    player.change_budget(base_price - loss)
                    try_risky_abort(username)
                    break

                rival.progress_deal()

            # сделка завершилась — считаем прибыль

            if freeze_turns >= 3:
                try_long_project(player, username)

            profit = calc_profit(car_quality)

            print("\nБазовый результат сделки игрока:", profit)

            apply_profit(player, rival, profit)

            if player.check_over():
                return

            finalize_rival(rival)

            print("\nсделка завершена")

            player.completed_deals.append(profit)

            try_first_deal(player, username)
            try_ten_deals(player, username)
            try_big_profit(player, username)

            if check_force_exit():
                print("\nпринудительный выход из ветки…")
                return

        # точка выхода между сделками
        print("\nнажмите Enter — продолжить")
        print("-- — выйти из ветки")

        cmd = input("действие: ").strip()

        if cmd == "--":
            print("\nвыход из ветки 2")
            return
