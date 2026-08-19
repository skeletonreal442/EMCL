import os
import sys
import subprocess
import uuid
import minecraft_launcher_lib

BASE_DIR = r"C:\EMCL"
VERSIONS_DIR = os.path.join(BASE_DIR, "versions")
PROFILES_FILE = os.path.join(BASE_DIR, "launcher_profiles.json")

REQUIRED_DIRS = [
    BASE_DIR,
    VERSIONS_DIR,
    os.path.join(BASE_DIR, "mods"),
    os.path.join(BASE_DIR, "assets"),
    os.path.join(BASE_DIR, "libraries")
]

for folder in REQUIRED_DIRS:
    if not os.path.exists(folder):
        os.makedirs(folder)

if not os.path.exists(PROFILES_FILE):
    with open(PROFILES_FILE, "w", encoding="utf-8") as f:
        f.write('{"profiles": {}}')

selected_version = None
nickname = "Player"

def get_versions():
    return minecraft_launcher_lib.utils.get_installed_versions(BASE_DIR)

def select_version_menu():
    global selected_version
    versions = get_versions()
    if not versions:
        print(f"\n[!] В папке '{VERSIONS_DIR}' не найдено версий!")
        input("\nНажмите Enter для продолжения...")
        return

    print("\n--- СПИСОК ВЕРСИЙ ---")
    for index, ver in enumerate(versions, start=1):
        marker = " [ВЫБРАНО]" if selected_version == ver['id'] else ""
        print(f" {index}. {ver['id']}{marker}")
    print(" E. Назад в главное меню")

    while True:
        choice = input("\nВыберите номер версии (или 'e' для возврата): ").strip()
        if choice.lower() == 'e':
            break
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(versions):
                selected_version = versions[idx - 1]['id']
                print(f"[+] Выбрана версия: {selected_version}")
                input("\nНажмите Enter для продолжения...")
                break
            else:
                print("Некорректный номер.")
        else:
            print("Введите число или 'e'.")

def change_nickname_menu():
    global nickname
    print(f"\nТекущий ник: {nickname}")
    print("E. Назад в главное меню")
    new_nick = input("\nВведите новый ник (или 'e' для отмены): ").strip()
    if new_nick.lower() == 'e':
        return
    if new_nick:
        nickname = new_nick
        print(f"[+] Ник изменен на: {nickname}")
        input("\nНажмите Enter для продолжения...")

def open_versions_folder():
    os.startfile(VERSIONS_DIR)
    print(f"\n[+] Папка открыта: {VERSIONS_DIR}")
    print("E. Назад в главное меню")
    while True:
        choice = input("\nВведите 'e' для возврата в меню: ").strip()
        if choice.lower() == 'e':
            break

def get_offline_options(nick):
    options = {
        "username": nick,
        "uuid": str(uuid.uuid3(uuid.NAMESPACE_DNS, nick)),
        "token": "0",
        "jvmArguments": ["-Xmx4G", "-Xms2G"]
    }

    if hasattr(minecraft_launcher_lib, "account"):
        if hasattr(minecraft_launcher_lib.account, "get_offline_account_information"):
            try:
                acc_info = minecraft_launcher_lib.account.get_offline_account_information(nick)
                options["username"] = acc_info.get("username", nick)
                options["uuid"] = acc_info.get("uuid", options["uuid"])
                options["token"] = acc_info.get("token", "0")
                return options
            except Exception:
                pass

    if hasattr(minecraft_launcher_lib, "utils"):
        if hasattr(minecraft_launcher_lib.utils, "generate_test_options"):
            try:
                test_opts = minecraft_launcher_lib.utils.generate_test_options()
                test_opts["username"] = nick
                test_opts["jvmArguments"] = options["jvmArguments"]
                return test_opts
            except Exception:
                pass

    return options

def launch_game():
    global selected_version, nickname
    if not selected_version:
        print("\n[!] Версия не выбрана! Перейдите в пункт 2 и выберите версию.")
        input("\nНажмите Enter для продолжения...")
        return

    os.system('cls' if os.name == 'nt' else 'clear')
    print("==========================================")
    print("             КОНСОЛЬ ЛОГОВ                ")
    print("==========================================")
    print(f"Подготовка к запуску {selected_version} | Ник: {nickname}")

    print("[1/2] Проверка файлов игры и библиотек...")
    try:
        minecraft_launcher_lib.install.install_minecraft_version(selected_version, BASE_DIR)
    except Exception as e:
        print(f"[!] Предупреждение при проверке файлов (офлайн режим): {e}")

    options = get_offline_options(nickname)

    print("[2/2] Запуск процесса Minecraft...")
    print("При закрытии игры или этой консоли процесс завершится.\n")

    try:
        launch_command = minecraft_launcher_lib.command.get_minecraft_command(
            selected_version, 
            BASE_DIR, 
            options
        )
        process = subprocess.Popen(launch_command)
        process.wait()
    except Exception as e:
        print(f"\n[Ошибка запуска]: {e}")
        input("\nНажмите Enter для продолжения...")

def main_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("==========================================")
        print("             EasyMCLauncher               ")
        print("==========================================")
        print(f" Директория: {BASE_DIR}")
        print(f" Выбранная версия: {selected_version if selected_version else 'НЕ ВЫБРАНА'}")
        print(f" Никнейм: {nickname}")
        print("==========================================")
        print(" 1. Открыть папку versions")
        print(" 2. Выбрать версию игры")
        print(" 3. Изменить никнейм")
        print(" 4. ЗАПУСТИТЬ ИГРУ")
        print("==========================================")

        choice = input("Выберите действие: ").strip()

        if choice == '1':
            open_versions_folder()
        elif choice == '2':
            select_version_menu()
        elif choice == '3':
            change_nickname_menu()
        elif choice == '4':
            launch_game()

if __name__ == "__main__":
    main_menu()