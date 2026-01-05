"""
модуль игровых сущностей

содержит основные классы логической модели игры:
    - Player      — основной игрок
    - Rival       — соперник (npc) для всех веток
    - Deal        — долгосрочный проект (ветка 3)
    - Portfolio   — портфель активных проектов

в модуле реализуются:

    финансовая модель:
        - изменение бюджета
        - фиксация прибыли / убытков
        - проверка банкротства игрока

    игровая прогрессия:
        - достижение целевого капитала
        - учёт завершённых сделок
        - хранение полученных артефактов

    поддержка веток:
        ветка 1 — переговоры с перекупом
        ветка 2 — торговля на рынке машин
        ветка 3 — проекты и долгие сделки

класс Rival расширяет Player и добавляет:
    - режим поведения (mode)
    - стиль взаимодействия
    - продвижение сделки (ветка 2)
    - работу с портфелем проектов (ветка 3)

портфель Portfolio предоставляет базовые операции:
    - добавление проекта
    - продвижение хода
    - завершение сделки
    - досрочное удаление проекта
"""


# ОСНОВНОЙ ИГРОК
class Player:
    """
    базовый класс игрока

    параметры:
        name  — имя игрока
        budget — стартовый бюджет
        role — роль персонажа (числовой код)

    модель ролей:
        1 — переговорщик (ветка 1)
        2 — перекуп рынка (ветка 2)
        3 — проект-мейкер / механик (ветка 3)
        0 — npc / соперник
    """

    def __init__(self, name, budget=0, role=1):
        self.name = name
        self.budget = budget
        self.role = role

        self.is_bankrupt = False
        self.win_target = None

        self.completed_deals = []
        self.artifacts = []

    # финансы

    def change_budget(self, amount):
        """
        изменяет бюджет игрока

        amount > 0 — прибыль
        amount < 0 — траты / убыток
        """

        self.budget += amount

        print(f"\n[бюджет игрока] изменение: {amount}")
        print(f"текущий баланс: {self.budget}")

        if self.budget <= 0:
            self.budget = 0
            self.is_bankrupt = True
            print("\nигра окончена — деньги закончились")

    # завершение игры

    def check_over(self):
        """
        проверяет банкротство
        """
        return self.is_bankrupt

    def check_win(self):
        """
        проверяет, достиг ли игрок целевого капитала
        """

        if self.win_target is None:
            return False

        if self.budget >= self.win_target:
            print("\n=== ПОЗДРАВЛЯЕМ — ВЕТКА ЗАВЕРШЕНА УСПЕШНО ===")
            print(f"достигнут целевой капитал: {self.budget} ₽")
            return True

        return False


# СОПЕРНИК (NPC)
class Rival(Player):
    """
    универсальный соперник (npc)

    режимы:
        mode = 1 — переговоры (ветка 1)
        mode = 2 — рынок сделок (ветка 2)
        mode = 3 — долгие проекты (ветка 3)

    style:
        0 — спокойный
        1 — хитрый
        2 — агрессивный

    дополнительные поля:
        state — стадия сделки (mode 2)
        profit_range — диапазон прибыли (mode 2)
        profit — итог сделки (mode 2)

        portfolio — набор активных проектов (mode 3)
    """

    def __init__(self, name, style, mode, budget=0, profit_range=None):
        super().__init__(name=name, budget=budget, role=0)

        self.style = style
        self.mode = mode

        # рынок / сделки (ветка 2)
        self.state = 0
        self.profit_range = profit_range
        self.profit = 0

        # проекты (ветка 3)
        self.portfolio = None

        if self.mode == 2 and self.profit_range:
            print("диапазон прибыли:", self.profit_range)

    # ветка 1

    def describe_behavior(self):
        styles = {
            0: "спокойный переговорщик",
            1: "хитрый и мутный торгаш",
            2: "жёсткий давящий перекуп"
        }
        return styles.get(self.style, "неизвестный тип поведения")

    # ветка 2

    def progress_deal(self):
        """
        продвигает этап сделки соперника
        """

        if self.mode != 2:
            return

        self.state += 1

        stages = {
            1: "подготовка машины",
            2: "просмотры и звонки",
            3: "переговоры с покупателем"
        }

        if self.state in stages:
            print(f"[соперник] стадия сделки: {stages[self.state]}")

    # изменение бюджета без печати
    def change_budget(self, amount):
        self.budget += amount

    def finalize_profit(self, amount):
        """
        завершает сделку соперника
        """

        if self.mode != 2:
            return

        self.profit = amount
        self.change_budget(amount)

        print("\n[финал сделки соперника]")
        print("результат сделки:", amount)
        print("итоговый бюджет:", self.budget)

    # ветка 3
    def ensure_portfolio(self, attach_portfolio_fn):
        """
        лениво подключает портфель проектов
        (используется в ветке 3)
        """

        if self.portfolio is None:
            attach_portfolio_fn(self)
            print("[соперник] создан портфель проектов")

    def add_project(self, deal):
        """
        соперник берёт проект в работу
        """

        if self.mode != 3:
            return

        self.portfolio.add(deal)
        print("[соперник] начал новый проект")

    def advance_projects(self):
        """
        продвигает ход всех проектов соперника
        """

        if self.mode != 3:
            return

        self.portfolio.advance_all()
        print("[соперник] проекты продвинулись на ход")


# СДЕЛКИ / ПРОЕКТЫ (Ветка 3)
class Deal:
    """
    проект / долгосрочная сделка

    поля:
        type — тип проекта (1 / 2 / 3)
        buy_price — стоимость входа
        freeze_turns — длительность работ

        passed — сколько ходов прошло
    """

    def __init__(self, deal_type, buy_price, freeze_turns):
        self.type = deal_type
        self.buy_price = buy_price
        self.freeze_turns = freeze_turns
        self.passed = 0

    def advance(self):
        self.passed += 1

    def is_ready(self):
        return self.passed >= self.freeze_turns


class Portfolio:
    """
    портфель активных проектов игрока / соперника
    """

    def __init__(self):
        self.deals = []

    def add(self, deal):
        self.deals.append(deal)

    def active_count(self):
        return len(self.deals)

    def advance_all(self):
        for d in self.deals:
            d.advance()

    def finish(self, deal, profit_range):
        self.deals.remove(deal)
        return profit_range

    def remove(self, deal):
        """Удаление проекта без завершения (досрочная продажа)"""
        if deal in self.deals:
            self.deals.remove(deal)


def attach_portfolio(entity):
    """
    добавляет объекту портфель проектов
    """
    entity.portfolio = Portfolio()


# УТИЛИТЫ
def check_force_exit():
    """
    проверяет, хочет ли игрок выйти из ветки вручную

    специальная команда:
        --  — принудительный выход

    returns:
        True  — если нужно завершить ветку
        False — если игра продолжается
    """

    print("\nнажмите Enter чтобы продолжить раунд")
    print("или введите -- для выхода из ветки")

    cmd = input("> ").strip()

    return cmd == "--"
