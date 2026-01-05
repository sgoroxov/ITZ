"""
main.py

главный модуль игры

реализует:
    - запуск программы
    - авторизацию / регистрацию игрока
    - создание объекта игрока
    - выбор игровой ветки
    - запуск игровой логики
"""

from player import Player
from auth import register_user, login_user
from branch1_basic import play_branch1
from branch2_market import play_branch2
from branch3_portfolio import play_branch3
from save_system import load_player_progress
from artifacts import activate_artifacts_on_login



def login_menu():
    """
    экран авторизации игрока

    returns:
        tuple (login, success)
    """

    print("\n=== Авторизация ===")

    login = input("логин: ")
    password = input("пароль: ")

    if login_user(login, password):
        return login, True

    print("\nне удалось выполнить вход\n")
    return login, False


def register_menu():
    """
    экран регистрации нового игрока

    returns:
        tuple (login, success)
    """

    print("\n=== Регистрация ===")

    login = input("придумайте логин: ")
    password = input("придумайте пароль: ")

    if register_user(login, password):
        return login, True

    print("\nрегистрация не выполнена\n")
    return login, False


def auth_cycle():
    """
    цикл меню входа / регистрации

    returns:
        str — логин авторизованного игрока
    """

    while True:

        print("\n1 — войти")
        print("2 — зарегистрироваться")
        print("3 — выйти из программы")

        choice = input("\nвыбор: ")

        if choice == "1":
            login, ok = login_menu()
            if ok:
                return login

        elif choice == "2":
            login, ok = register_menu()
            if ok:
                return login

        elif choice == "3":
            print("\nвыход...")
            exit()

        else:
            print("неверный пункт меню")


def start_game_mode(player):
    """
        предлагает игроку:
            восстановить сохранённые артефакты
            начать игру без бонусов

        parameters:
            player — объект игрока
    """

    print("\n=== запуск игры ===")
    print("1 — восстановить артефакты из сохранения")
    print("2 — начать без артефактов")

    choice = input("\nвыбор: ")

    if choice == "1":

        artifacts = load_player_progress()

        if len(artifacts) == 0:
            print("\nсохранённых артефактов нет")
            return

        print("\nзагружены артефакты игрока:")

        for a in artifacts:
            print("-", a.name, "(+", a.power, ")")

        # активация эффектов при входе в игру
        activate_artifacts_on_login(artifacts)

    else:
        print("\nигра начата без артефактов")


def game_loop(player):
    """
        основной игровой цикл

        позволяет запускать ветки
        пока игрок не завершит игру
    """

    print("\n=== выбор сюжетной ветки ===\n")

    print("1 — переговоры с перекупом")
    print("2 — перепродажа автомобилей")
    print("3 — инвестиционный портфель")

    while True:

        branch = input("\nваш выбор: ")

        if branch == "1":
            play_branch1(player)

        elif branch == "2":
            play_branch2(player)

        elif branch == "3":
            play_branch3(player)

        else:
            print("\nошибка — нужно ввести 1, 2 или 3")
            continue

        print("\nсыграть ещё одну ветку?")
        print("1 — продолжить")
        print("2 — выйти в меню")

        again = input("выбор: ")

        if again != "1":
            print("\nвыход в главное меню\n")
            break

def main():
    """
        точка входа в игру

        выполняет:
            - авторизацию
            - создание объекта игрока
            - выбор режима игры
            - запуск игрового цикла
    """

    login = auth_cycle()

    player = Player(name=login)

    player.artifacts = load_player_progress()
    print("\nзагружены артефакты:", len(player.artifacts))

    game_loop(player)


if __name__ == "__main__":
    main()