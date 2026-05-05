import subprocess
import telnetlib
import os
import time
import signal
import sys

HOST = "192.168.11.1"

#CHANGE THESE VALUES#############################
DEVICE_IP = "192.168.11.135" # The device you're going to run this script on (ex. laptop, desktop)
PASSWORD = "root" # Set the root password of the router
#DON'T MESS WITH ANYTHING BELOW THIS#############

HTTP_PORT = 8000
http_proc = None


# ---------------- HTTP SERVER ----------------

def start_http_server():
    global http_proc

    print("[*] Starting HTTP server...")

    http_proc = subprocess.Popen(
        ["python3", "-m", "http.server", str(HTTP_PORT), "--bind", "0.0.0.0"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def stop_http_server():
    global http_proc

    if http_proc:
        print("[*] Stopping HTTP server...")
        http_proc.terminate()

        try:
            http_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            http_proc.kill()


# ---------------- TELNET CORE ----------------

def telnet_session():
    tn = telnetlib.Telnet(HOST)

    tn.read_until(b"login: ")
    tn.write(b"root\n")

    tn.read_until(b"Password: ")
    tn.write(PASSWORD.encode() + b"\n")

    tn.read_until(b"# ")

    return tn


def send_wait(tn, cmd, wait=b"# ", timeout=10):
    print(f"[>] {cmd}")
    tn.write(cmd.encode() + b"\n")
    out = tn.read_until(wait, timeout)
    text = out.decode(errors="ignore")
    print(text)
    return text


# ---------------- DEVICE PREP ----------------

def prepare_device():
    print("[*] Preparing device...")

    cmd = (
        f'wget -O- "http://{HOST}/protocol.csp'
        f'?fname=net&opt=time_conf&math=0.1&function=set"'
    )

    subprocess.run(cmd, shell=True)


# ---------------- FILE UPLOAD ----------------

def upload_file(local_file, remote_path):
    print(f"[*] Uploading {local_file} -> {remote_path}")

    if not os.path.exists(local_file):
        print(f"[!] Missing file: {local_file}")
        return

    url = f"http://{DEVICE_IP}:{HTTP_PORT}/{local_file}"

    tn = telnet_session()

    send_wait(tn, f"wget {url} -O {remote_path}")
    send_wait(tn, f"ls -l {remote_path}")

    tn.write(b"exit\n")
    tn.close()


# ---------------- START REMOTE SERVER ----------------

def start_server():
    print("[*] Starting remote server...")

    upload_file("bareiron", "/tmp/bareiron")

    if os.path.exists("world.bin"):
        upload_file("world.bin", "/tmp/world.bin")

    tn = telnet_session()

    send_wait(tn, "cd /tmp")
    send_wait(tn, "chmod +x bareiron")
    send_wait(tn, "./bareiron &")

    tn.write(b"exit\n")
    tn.close()


# ---------------- BACKUP + CLEANUP ----------------

def backup_server():
    print("[*] Backing up via netcat...")

    # Local listeners
    bareiron_nc = subprocess.Popen("nc -l -p 9000 > bareiron", shell=True)
    world_nc = subprocess.Popen("nc -l -p 9001 > world.bin", shell=True)

    time.sleep(1)

    tn = telnet_session()

    # Transfer files from device -> host
    send_wait(tn, f"nc {DEVICE_IP} 9000 < /tmp/bareiron")
    send_wait(tn, f"[ -f /tmp/world.bin ] && nc {DEVICE_IP} 9001 < /tmp/world.bin")

    bareiron_nc.wait()
    world_nc.wait()

    print("[*] Backup complete")

    # ---------------- KILL REMOTE PROCESS ----------------

    print("[*] Stopping remote bareiron process...")

    out = send_wait(tn, "killall bareiron")

    if "not found" in out.lower() or "no process" in out.lower():
        send_wait(tn, "ps | grep bareiron | grep -v grep")
        send_wait(tn, "ps | grep bareiron | grep -v grep | awk '{print $1}' | xargs kill -9")

    tn.write(b"exit\n")
    tn.close()

    print("[*] Remote process stopped")


# ---------------- CLEAN EXIT ----------------

def signal_handler(sig, frame):
    stop_http_server()
    sys.exit(0)


# ---------------- MAIN LOOP ----------------

def main():
    signal.signal(signal.SIGINT, signal_handler)

    start_http_server()
    time.sleep(3)

    try:
        while True:
            print("\n1. Prepare device")
            print("2. Start server")
            print("3. Backup server")
            print("4. Exit")

            choice = input("> ").strip()

            if choice == "4":
                break
            elif choice == "1":
                prepare_device()
            elif choice == "2":
                start_server()
            elif choice == "3":
                backup_server()
            else:
                print("Invalid option")

    finally:
        stop_http_server()


if __name__ == "__main__":
    main()