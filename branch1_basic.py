"""
ветка 1 —
    переговорная сцена с перекупом

модель ветки:
    - игрок выбирает стратегию поведения в переговорах
    - соперник реагирует в зависимости от стиля общения
    - итог сделки определяется числовой моделью взаимодействия
    - результат может дать прибыль, ноль или убыток

игровые сущности:
    Rival — соперник-продавец с собственным стилем торга
    игрок — принимает решения и управляет своим бюджетом

достижения (артефакты):
    - первая успешная сделка
    - 10 завершённых сделок
    - крупная прибыль
    - редкое удачное стечение обстоятельств

таблицы логики:
    ACTION_TEXT        — стратегии игрока
    RIVAL_STYLE_TEXT   — поведение соперника
    OUTCOME_TEXT       — текстовое описание исходов
    OUTCOME_VALUES     — числовые диапазоны прибыли / убытка

унифицированные функции:
    generate_rival   — создать соперника переговоров
    choose_action    — запросить стратегию игрока
    calc_outcome     — рассчитать исход встречи
    apply_outcome    — применить финансовый результат
    play_branch1     — основной игровой цикл ветки
"""


import random
from player import Rival, safe_int
from player import check_force_exit
from auth import get_current_username
from artifacts_hooks import (
    try_first_deal,
    try_ten_deals,
)


# коды действий игрока
ACTION_TEXT = {
    1: "жёсткий торг по цене",
    2: "быстро забрать машину",
    3: "перехитрить разговором",
    4: "уйти и вернуться позже"
}

# коды поведения соперника
RIVAL_STYLE_TEXT = {
    0: "спокойный продавец",
    1: "хитрый перекуп",
    2: "агрессивный переговорщик"
}

# коды финансовых исходов
OUTCOME_TEXT = {
    0: "сделка сорвалась",
    1: "небольшой плюс",
    2: "уверенный профит",
    3: "небольшой минус",
    4: "крупная потеря",
    5: "редкий джекпот",
    6: "почти без изменений"
}

# диапазоны прибыли / убытка
OUTCOME_VALUES = {
    1: (3000, 10000),
    2: (12000, 30000),
    3: (-8000, -3000),
    4: (-30000, -15000),
    5: (35000, 65000),
    6: (-2000, 2000)
}


def generate_rival():
    """
    создаёт соперника для переговорной сделки

    returns:
        Rival — объект npc соперника
    """

    styles = {
        0: "спокойный перекуп",
        1: "хитрый перекуп",
        2: "агрессивный переговорщик"
    }

    style_id = random.randint(0, 2)

    rival = Rival(
        name="перекуп с авито",
        budget=0,
        style=style_id,
        mode=1
    )

    print(f"\nСоперник: {styles[style_id]}")

    return rival


def choose_action():
    """
    выводит варианты действий и возвращает выбор игрока
    """

    print("\nВыберите стратегию поведения:")

    for code, text in ACTION_TEXT.items():
        print(code, "-", text)

    action = safe_int("\nВаш выбор: ")

    if action is None:
        print("ход пропущен")
        return 0

    return action


def calc_outcome(player_action, rival_style):
    """
    рассчитывает исход сделки

    используем числовую матрицу поведения
    """

    outcome_matrix = {

        # 1 — жёсткий торг
        1: {
            0: 2,   # против спокойного — хороший плюс
            1: 1,   # против хитрого — небольшой плюс
            2: 3    # против агрессивного — небольшой минус
        },

        # 2 — забрать быстро
        2: {
            0: 6,   # нейтрально
            1: 1,   # иногда небольшой плюс
            2: 4    # против агрессивного — риск крупного минуса
        },

        # 3 — перехитрить
        3: {
            0: 1,
            1: 0,   # хитрый соперник ломает схему
            2: 4
        },

        # 4 — уйти и вернуться
        4: {
            0: 6,
            1: 2,  # иногда рынок играет на руку
            2: 0
        }
    }

    return outcome_matrix[player_action][rival_style]


def apply_outcome(player, outcome_code):
    """
    применяет финансовый результат к бюджету игрока
    """

    username = get_current_username()

    if outcome_code == 0:
        print("\nСделка сорвалась — денег не заработано")
        return

    low, high = OUTCOME_VALUES[outcome_code]
    amount = random.randint(low, high)

    print("\nФинансовый результат:", OUTCOME_TEXT[outcome_code])
    print("Изменение бюджета:", amount)

    player.change_budget(amount)

    player.completed_deals.append(amount)

    # первая успешная сделка
    try_first_deal(player, username)
    # счётчик завершённых сделок
    try_ten_deals(player, username)


def play_branch1(player):
    """
    запуск ветки переговоров с перекупом
    """

    print("\n=== Ветка 1 — Переговоры за машину ===\n")

    player.budget = 80_000
    player.win_target = 150_000

    print("стартовый бюджет:", player.budget)

    while True:

        rival = generate_rival()

        action = choose_action()

        outcome_code = calc_outcome(action, rival.style)

        apply_outcome(player, outcome_code)

        # авто-завершение игры
        if player.check_win():
            return

        if player.check_over():
            return

        print("\nраунд завершён")

        if check_force_exit():
            print("\nпринудительный выход из ветки…")
            return

        print("\nначинается новый раунд…")
