import os
import sys
import json
import subprocess
import uuid
import minecraft_launcher_lib

BASE_DIR = r"C:\EMCL"
VERSIONS_DIR = os.path.join(BASE_DIR, "versions")
PROFILES_FILE = os.path.join(BASE_DIR, "launcher_profiles.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

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

def load_config():
    global selected_version, nickname
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                nickname = data.get("nickname", "Player")
                selected_version = data.get("selected_version", None)
        except Exception:
            pass

def save_config():
    data = {
        "nickname": nickname,
        "selected_version": selected_version
    }
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

load_config()

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(r"""
 /$$$$$$$$ /$$      /$$  /$$$$$$  /$$      
| $$_____/| $$$    /$$$ /$$__  $$| $$      
| $$      | $$$$  /$$$$| $$  \__/| $$      
| $$$$$   | $$ $$/$$ $$| $$      | $$      
| $$__/   | $$  $$$| $$| $$      | $$      
| $$      | $$\  $ | $$| $$    $$| $$      
| $$$$$$$$| $$ \/  | $$|  $$$$$$/| $$$$$$$$
|________/|__/     |__/ \______/ |________/
    """)

def get_installed_versions():
    return minecraft_launcher_lib.utils.get_installed_versions(BASE_DIR)

def select_version_menu():
    global selected_version
    versions = get_installed_versions()
    print_header()
    if not versions:
        print("  [!] Локальных версий не найдено.")
        print("      Используйте пункт 'Скачать версию' для загрузки.\n")
        input("  Нажмите Enter для продолжения...")
        return

    print("  --- СПИСОК УСТАНОВЛЕННЫХ ВЕРСИЙ ---")
    for index, ver in enumerate(versions, start=1):
        marker = " [ВЫБРАНО]" if selected_version == ver['id'] else ""
        print(f"  [{index}] {ver['id']}{marker}")
    print("  [E] Назад в главное меню\n")

    while True:
        choice = input("  Выберите номер версии (или 'e' для возврата): ").strip()
        if choice.lower() == 'e':
            break
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(versions):
                selected_version = versions[idx - 1]['id']
                save_config()
                print(f"\n  [+] Выбрана версия: {selected_version}")
                input("  Нажмите Enter для продолжения...")
                break
            else:
                print("  Некорректный номер.")
        else:
            print("  Введите число или 'e'.")

def download_version_menu():
    global selected_version
    print_header()
    print("  [1/2] Получение списка официальных версий Mojang...")
    try:
        all_versions = minecraft_launcher_lib.utils.get_version_list()
        release_versions = [v for v in all_versions if v['type'] == 'release']
    except Exception as e:
        print(f"  [!] Ошибка загрузки списка версий: {e}")
        input("\n  Нажмите Enter для продолжения...")
        return

    page_size = 15
    total_pages = (len(release_versions) + page_size - 1) // page_size
    current_page = 0

    while True:
        print_header()
        start_idx = current_page * page_size
        end_idx = min(start_idx + page_size, len(release_versions))
        page_items = release_versions[start_idx:end_idx]

        print(f"  --- ОФИЦИАЛЬНЫЕ ВЕРСИИ (Страница {current_page + 1} из {total_pages}) ---\n")
        for idx, ver in enumerate(page_items, start=1):
            print(f"  [{idx}] Minecraft {ver['id']}")

        print("\n  [N] Следующая страница | [P] Предыдущая страница")
        print("  [E] Назад в главное меню\n")

        choice = input("  Выберите номер для скачивания (или действие): ").strip().lower()

        if choice == 'e':
            break
        elif choice == 'n':
            if current_page < total_pages - 1:
                current_page += 1
        elif choice == 'p':
            if current_page > 0:
                current_page -= 1
        elif choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(page_items):
                target_ver = page_items[idx - 1]['id']
                print_header()
                print(f"  [+] Загрузка версии {target_ver} с официального сервера Mojang...")
                print("  Пожалуйста, подождите, идет скачивание...\n")
                
                try:
                    minecraft_launcher_lib.install.install_minecraft_version(
                        target_ver, 
                        BASE_DIR, 
                        callback={"setStatus": lambda s: print(f"  {s}")}
                    )
                    selected_version = target_ver
                    save_config()
                    print(f"\n  [+] Версия {target_ver} успешно установлена и выбрана!")
                except Exception as e:
                    print(f"\n  [!] Ошибка при скачивании: {e}")
                
                input("\n  Нажмите Enter для продолжения...")
                break
            else:
                print("  Некорректный номер на текущей странице.")

def change_nickname_menu():
    global nickname
    print_header()
    print(f"  Текущий ник: {nickname}\n")
    new_nick = input("  Введите новый ник (или 'e' для отмены): ").strip()
    if new_nick.lower() == 'e':
        return
    if new_nick:
        nickname = new_nick
        save_config()
        print(f"\n  [+] Ник изменен на: {nickname}")
        input("  Нажмите Enter для продолжения...")

def open_emcl_folder():
    print_header()
    os.startfile(BASE_DIR)
    print(f"  [+] Папка открыта: {BASE_DIR}")
    print("  Возврат в главное меню...")
    subprocess.Popen(["timeout", "/t", "1"], shell=True).wait()

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
    print_header()
    if not selected_version:
        print("  [!] Версия не выбрана! Выберите или скачайте версию.")
        input("\n  Нажмите Enter для продолжения...")
        return

    print("=========================================================")
    print("                     КОНСОЛЬ ЛОГОВ                       ")
    print("=========================================================")
    print(f"  Запуск {selected_version} | Ник: {nickname}\n")

    print("  [1/2] Проверка локальных библиотек...")
    try:
        minecraft_launcher_lib.install.install_minecraft_version(selected_version, BASE_DIR)
    except Exception as e:
        print(f"  [!] Пропуск докачивания (офлайн): {e}")

    options = get_offline_options(nickname)

    print("  [2/2] Старт процесса Minecraft...\n")

    try:
        launch_command = minecraft_launcher_lib.command.get_minecraft_command(
            selected_version, 
            BASE_DIR, 
            options
        )
        process = subprocess.Popen(launch_command)
        process.wait()
    except Exception as e:
        print(f"\n  [Ошибка запуска]: {e}")
        input("\n  Нажмите Enter для продолжения...")

def main_menu():
    while True:
        print_header()
        print("=========================================================")
        print(f"  Директория: {BASE_DIR}")
        print(f"  Выбранная версия: {selected_version if selected_version else 'НЕ ВЫБРАНА'}")
        print(f"  Никнейм: {nickname}")
        print("=========================================================")
        print("  [1] Открыть папку EMCL")
        print("  [2] Выбрать установленную версию")
        print("  [3] Скачать официальную версию (Mojang)")
        print("  [4] Изменить никнейм")
        print("  [5] ЗАПУСТИТЬ ИГРУ")
        print("=========================================================\n")

        choice = input("  Выберите действие: ").strip()

        if choice == '1':
            open_emcl_folder()
        elif choice == '2':
            select_version_menu()
        elif choice == '3':
            download_version_menu()
        elif choice == '4':
            change_nickname_menu()
        elif choice == '5':
            launch_game()

if __name__ == "__main__":
    main_menu()
