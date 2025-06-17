import json
import os
import random
import string
import getpass

from colorama import init, Fore, Style
init(autoreset=True)

from cryptography.fernet import Fernet

DATA_FILE = "passwords.json"
MASTER_FILE = "master.key"
SECURITY_FILE = "security.json"
SECURITY_QUESTIONS = [
    "İlk evcil hayvanınızın adı nedir?",
    "En sevdiğiniz öğretmenin adı nedir?",
    "Doğduğunuz şehir nedir?",
    "Çocukluk lakabınız nedir?",
    "En sevdiğiniz renk nedir?"
]

def setup_security_question():
    if not os.path.exists(SECURITY_FILE):
        print(Fore.YELLOW + "\n Güvenlik sorusu belirleyin (şifre sıfırlama için gereklidir).")
        for idx, q in enumerate(SECURITY_QUESTIONS, 1):
            print(f"{idx}. {q}")
        while True:
            try:
                choice = int(input("Bir güvenlik sorusu seçin (numara): "))
                if 1 <= choice <= len(SECURITY_QUESTIONS):
                    question = SECURITY_QUESTIONS[choice-1]
                    break
                else:
                    print("Geçersiz seçim.")
            except ValueError:
                print("Lütfen sayı girin.")
        answer = getpass.getpass("Cevabınız: ").strip()
        key = load_key()
        entry = {
            "question": question,
            "answer": encrypt(answer, key)
        }
        with open(SECURITY_FILE, "w") as f:
            json.dump(entry, f)
        print(Fore.GREEN + " Güvenlik sorusu kaydedildi!\n")


def setup_master_password():
    if not os.path.exists(MASTER_FILE):
        print(Fore.YELLOW + "\n İlk defa giriş yapıyorsunuz. Ana parola oluşturun.")
        while True:
            pw1 = getpass.getpass("Yeni ana parola: ")
            pw2 = getpass.getpass("Tekrar: ")
            if pw1 == pw2 and len(pw1) >= 6:
                key = load_key()
                encrypted_pw = encrypt(pw1, key)
                with open(MASTER_FILE, "w") as f:
                    f.write(encrypted_pw)
                print(Fore.GREEN + "Ana parola kaydedildi!\n")
                break
            else:
                print(Fore.RED + "Parolalar uyuşmuyor veya çok kısa. Tekrar deneyin.")
        setup_security_question()

def verify_security_question():
    if not os.path.exists(SECURITY_FILE):
        print(Fore.RED + "Güvenlik sorusu ayarlanmamış.")
        return False
    with open(SECURITY_FILE, "r") as f:
        entry = json.load(f)
    key = load_key()
    print(Fore.YELLOW + f"Güvenlik sorusu: {entry['question']}")
    answer = getpass.getpass("Cevabınız: ").strip()
    if answer == decrypt(entry['answer'], key):
        return True
    else:
        print(Fore.RED + "Yanlış cevap!")
        return False

def load_master_password():
    if not os.path.exists(MASTER_FILE):
        return None
    with open(MASTER_FILE, "r") as f:
        encrypted_pw = f.read()
    key = load_key()
    return decrypt(encrypted_pw, key)

def reset_master_password():
    print(Fore.CYAN + "\n--- Master Parola Sıfırlama ---")
    if verify_security_question():
        while True:
            pw1 = getpass.getpass("Yeni ana parola: ")
            pw2 = getpass.getpass("Tekrar: ")
            if pw1 == pw2 and len(pw1) >= 6:
                key = load_key()
                encrypted_pw = encrypt(pw1, key)
                with open(MASTER_FILE, "w") as f:
                    f.write(encrypted_pw)
                print(Fore.GREEN + "Ana parola güncellendi!\n")
                break
            else:
                print(Fore.RED + "Parolalar uyuşmuyor veya çok kısa. Tekrar deneyin.")


def show_logo():
    print(r"""
 ___                      ___                        _ 
| . | ___  ___ ._ _  ___ | . \ ___  ___ ___ _ _ _  _| |
| | || . \/ ._>| ' ||___||  _/<_> |<_-<<_-<| | | |/ . |
`___'|  _/\___.|_|_|     |_|  <___|/__//__/|__/_/ \___|
     |_|                                               
    """)
    print("     Yerel Parola Yöneticisi - v0.1\n")
    print("     Made by efekcss...\n")
    print(" Visit --> github.com/efekcss")

def main_menu():
    print(Fore.CYAN + "\n--- Ana Menü ---\n")
    print(Fore.RED + "0." + Fore.RESET + " Çıkış")
    print(Fore.YELLOW + "1." + Fore.RESET + " Yeni parola ekle")
    print(Fore.YELLOW + "2." + Fore.RESET + " Parolaları listele")
    print(Fore.YELLOW + "3." + Fore.RESET + " Şifre üret")
    print(Fore.YELLOW + "4." + Fore.RESET + " Parola sil")
    print(Fore.YELLOW + "5." + Fore.RESET + " Parola ara")
    print(Fore.YELLOW + "6." + Fore.RESET + " Parola güncelle")
    print(Fore.YELLOW + "7." + Fore.RESET + " Master parolayı sıfırla")

def create_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    return open("key.key", "rb").read()

def encrypt(text: str, key: bytes) -> str:
    f = Fernet(key)
    return f.encrypt(text.encode()).decode()

def decrypt(token: str, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(token.encode()).decode()


def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)



def login():
    print(Fore.BLUE + "Giriş yapmanız gerekiyor. (3 Giriş Hakkınız vardır.)")
    master_password = load_master_password()
    if not master_password:
        print(Fore.RED + "Ana parola dosyası eksik.")
        return False

    for _ in range(3):
        entered = getpass.getpass("Ana parolayı girin: ")
        if entered == master_password:
            print(Fore.GREEN + "Giriş başarılı!")
            return True
        else:
            print(Fore.RED + "Hatalı parola.")

    print(Fore.RED + "Çok fazla başarısız giriş.")
    print(Fore.YELLOW + "Güvenlik sorusunu doğru cevaplarsanız ana parolayı sıfırlayabilirsiniz.")
    if verify_security_question():
        reset_master_password()
        print(Fore.CYAN + "Lütfen yeni ana parolanızla tekrar giriş yapın.")
        master_password = load_master_password()
        for _ in range(3):
            entered = getpass.getpass("Ana parolayı girin: ")
            if entered == master_password:
                print(Fore.GREEN + "Giriş başarılı!")
                return True
            else:
                print(Fore.RED + "Hatalı parola.")
        print(Fore.RED + "Çok fazla başarısız giriş. Uygulamaya erişilemiyor.")
        return False
    else:
        print(Fore.RED + "Güvenlik sorusu yanlış. Uygulamaya erişilemiyor.")
        return False


def add_password():
    key = load_key()

    site = input("Site/Uygulama adı: ")
    username = input("Kullanıcı adı: ")
    password = input("Parola: ")

    entry = {
        "site": encrypt(site, key),
        "username": encrypt(username, key),
        "password": encrypt(password, key)
    }

    data = load_data()
    data.append(entry)
    save_data(data)
    print(Fore.GREEN + "\nParola şifrelenerek kaydedildi!\n")


def list_passwords():
    key = load_key()
    data = load_data()
    if not data:
        print("Hiç parola kaydı bulunamadı.")
        return
    print(Fore.BLUE + "\nKayıtlı Parolalar:\n")
    for i, entry in enumerate(data, 1):
        site = decrypt(entry['site'], key)
        username = decrypt(entry['username'], key)
        password = decrypt(entry['password'], key)
        print(f"{i}. {site} | {username} | {password}")

def search_password():
    key = load_key()
    data = load_data()

    if not data:
        print("Kayıtlı parola bulunamadı.")
        return

    query = input("Aramak istediğiniz site adını girin (Direkt Enter'a basarsanız hepsini sıralar) : ").lower()
    results = []

    for entry in data:
        site = decrypt(entry['site'], key).lower()
        if query in site:
            username = decrypt(entry['username'], key)
            password = decrypt(entry['password'], key)
            results.append((site, username, password))

    if results:
        print(Fore.BLUE + f"\n '{query}' ile eşleşen parolalar:\n")
        for i, (site, username, password) in enumerate(results, 1):
            print(f"{i}. {site} | {username} | {password}")
    else:
        print(Fore.YELLOW + "⚠️ Eşleşen kayıt bulunamadı.")


def delete_password():
    key = load_key()
    data = load_data()

    if not data:
        print("Silinecek parola bulunamadı.")
        return

    print(Fore.MAGENTA + "\nSilinebilir Parolalar:\n")
    for i, entry in enumerate(data, 1):
        site = decrypt(entry['site'], key)
        username = decrypt(entry['username'], key)
        print(f"{i}. {site} | {username}")

    try:
        index = int(input("\nSilmek istediğiniz parolanın numarasını girin: ")) - 1
        if 0 <= index < len(data):
            deleted = decrypt(data[index]['site'], key)
            data.pop(index)
            save_data(data)
            print(Fore.RED + f"'{deleted}' için kayıt silindi.")
        else:
            print(Fore.YELLOW + "Geçersiz numara.")
    except ValueError:
        print(Fore.YELLOW + "Lütfen geçerli bir sayı girin.")

def update_password():
    key = load_key()
    data = load_data()

    if not data:
        print(Fore.YELLOW + "Güncellenecek parola bulunamadı.")
        return

    print(Fore.CYAN + "\nGüncellemek istediğiniz siteyi arayın:")

    search_term = input("Site adı (tam veya kısmi): ").strip().lower()

    filtered = []
    for i, entry in enumerate(data):
        site_decrypted = decrypt(entry['site'], key).lower()
        if search_term in site_decrypted:
            filtered.append((i, entry))

    if not filtered:
        print(Fore.RED + "Eşleşen site bulunamadı.")
        return

    print(Fore.BLUE + "\nEşleşen Parolalar:\n")
    for idx, (i, entry) in enumerate(filtered, 1):
        site = decrypt(entry['site'], key)
        username = decrypt(entry['username'], key)
        print(f"{idx}. {site} | {username}")

    try:
        choice = int(input("\nGüncellemek istediğiniz parolanın numarasını girin: ")) - 1
        if choice < 0 or choice >= len(filtered):
            print(Fore.YELLOW + "Geçersiz seçim.")
            return
    except ValueError:
        print(Fore.YELLOW + "Geçerli bir sayı girin.")
        return

    index = filtered[choice][0]

    new_username = input("Yeni kullanıcı adı (boş bırakılırsa değişmez): ").strip()
    new_password = input("Yeni parola (boş bırakılırsa değişmez): ").strip()

    if new_username:
        data[index]['username'] = encrypt(new_username, key)
    if new_password:
        data[index]['password'] = encrypt(new_password, key)

    save_data(data)
    print(Fore.GREEN + "Parola güncellendi!")


def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def generate_password_menu():
    print("\nParola oluştururken kullanmak istediğiniz karakter türlerini seçin:")

    use_lower = input("Küçük harfler dahil edilsin mi? (E/H) ").strip().lower() != 'h'
    use_upper = input("Büyük harfler dahil edilsin mi? (E/H) ").strip().lower() != 'h'
    use_digits = input("Rakamlar dahil edilsin mi? (E/H) ").strip().lower() != 'h'
    use_symbols = input("Semboller dahil edilsin mi? (E/H) ").strip().lower() != 'h'

    if not any([use_lower, use_upper, use_digits, use_symbols]):
        print(Fore.YELLOW + "En az bir karakter türü seçmelisiniz!")
        return

    try:
        length = int(input("Parola uzunluğu (varsayılan 12): ") or 12)
        if length < 6:
            print(Fore.YELLOW + "Parola çok kısa! En az 6 karakter olmalı.")
            return
    except ValueError:
        print(Fore.YELLOW + "Lütfen geçerli bir sayı girin.")
        return

    characters = ""
    if use_lower:
        characters += string.ascii_lowercase
    if use_upper:
        characters += string.ascii_uppercase
    if use_digits:
        characters += string.digits
    if use_symbols:
        characters += string.punctuation

    password = ''.join(random.choice(characters) for _ in range(length))

    print(f"\nOluşturulan parola: \033[92m{password}\033[0m\n")

    save_choice = input("Bu parolayı parola listesine eklemek ister misiniz? (E/h): ").strip().lower()
    if save_choice != 'h':
        key = load_key()
        site = input("Site/Uygulama adı: ")
        username = input("Kullanıcı adı: ")

        entry = {
            "site": encrypt(site, key),
            "username": encrypt(username, key),
            "password": encrypt(password, key)
        }

        data = load_data()
        data.append(entry)
        save_data(data)
        print(Fore.GREEN + "Parola parola listesine kaydedildi!\n")

    input("Devam etmek için Enter'a basın...")


def run():
    if not os.path.exists("key.key"):
        create_key()
    
    setup_master_password()

    if not os.path.exists(SECURITY_FILE):
        setup_security_question()

    if not login():
        return  

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        show_logo()
        main_menu()
        choice = input("\nSeçiminiz: ").strip()

        if choice == "1":
            add_password()
        elif choice == "2":
            list_passwords()
            input("\nDevam etmek için Enter'a basın...")
        elif choice == "3":
            generate_password_menu()
        elif choice == "4":
            delete_password()
            input("\nDevam etmek için Enter'a basın...")
        elif choice == "5":
            search_password()
            input("\nDevam etmek için Enter'a basın...")
        elif choice == "6":
            update_password()
            input("\nDevam etmek için Enter'a basın...")
        elif choice == "7":
            reset_master_password()
            input("\nDevam etmek için Enter'a basın...")
        elif choice == "0":
            print("Görüşmek üzere...")
            break
        else:
            print(Fore.RED + "Geçersiz seçim!")
            input(Fore.GREEN + "Devam etmek için Enter'a basın...")

if __name__ == "__main__":
    run()
