import sys
import os

# ──────────────────────────────────────────────
# The in-memory index was custom (no built-in)
# A list of key-value pairs was implemented
# The entries that were put in last always overrided the ones the ones previously.
# ──────────────────────────────────────────────

DB_FILE = "data.db"

def index_set(index, key, value):
    """Update the key in the index."""
    for entry in index:
        if entry[0] == key:
            entry[1] = value
            return
    index.append([key, value])

def index_get(index, key):
    """The value of the key will be returned or nothing will be returned if it is not found."""
   
    for entry in reversed(index):
        if entry[0] == key:
            return entry[1]
    return None

# ──────────────────────────────────────────────
# This portion is for the append-only
# ──────────────────────────────────────────────

def persist_set(key, value):
    """SET command is appended to the log file instantly."""
    with open(DB_FILE, "a") as f:
        
        f.write(f"SET|{key}|{value}\n")

def load_from_disk(index):
    """The log file is played again in order for the in-memory index on startup to be rebuilt."""
    if not os.path.exists(DB_FILE):
        return  # No existing data, start fresh
    with open(DB_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|", 2)
            if len(parts) == 3 and parts[0] == "SET":
                _, key, value = parts
                index_set(index, key, value)

# ──────────────────────────────────────────────
# This portion deals with the handling of the commands
# ──────────────────────────────────────────────

def handle_command(index, line):
    """Once parsed a single command line is executed and False is returned on exit"""
    parts = line.strip().split(" ", 2)
    if not parts or parts[0] == "":
        return True

    cmd = parts[0].upper()

    if cmd == "SET":
        if len(parts) < 3:
            print("ERROR: Usage: SET <key> <value>")
        else:
            key, value = parts[1], parts[2]
            index_set(index, key, value)
            persist_set(key, value)
            print("OK")

    elif cmd == "GET":
        if len(parts) < 2:
            print("ERROR: Usage: GET <key>")
        else:
            key = parts[1]
            val = index_get(index, key)
            if val is None:
                print("NULL")
            else:
                print(val)

    elif cmd == "EXIT":
        return False  # Signal to stop the loop

    else:
        print(f"ERROR: Unknown command '{cmd}'")

    return True

# ──────────────────────────────────────────────
# This portion is for the main entry point
# ──────────────────────────────────────────────

def main():
    index = []           
    load_from_disk(index)  

    for line in sys.stdin:
        if not handle_command(index, line):
            break

if __name__ == "__main__":
    main()