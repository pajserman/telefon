# app.py

from phone import IntercomMaster

# Define your known devices here
contacts = {
    "localhost": "localhost",
}

def print_contacts():
    print("\nAvailable Devices:")
    for i, (name, ip) in enumerate(contacts.items(), start=1):
        print(f"  {i}. {name} ({ip})")
    print("  q. Quit")

def main():
    master = IntercomMaster()

    try:
        print("=== Intercom Master ===")
        while True:
            print_contacts()
            choice = input("\nSelect a device to call: ").strip()

            if choice.lower() == 'q':
                break

            try:
                index = int(choice) - 1
                if 0 <= index < len(contacts):
                    name = list(contacts.keys())[index]
                    ip = contacts[name]
                    print(f"[+] Calling {name} ({ip})...")
                    master.start_call(target_ip=ip)
                    print(f"[-] Call with {name} ended.")
                else:
                    print("[!] Invalid selection.")
            except ValueError:
                print("[!] Please enter a valid number.")

    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")

    finally:
        print("[*] Shutting down intercom...")
        master.close()

if __name__ == "__main__":
    main()
