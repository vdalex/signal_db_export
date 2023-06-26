"""Main script for sigexport."""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from typer import Exit, Option, run

from pysqlcipher3 import dbapi2 as sqlcipher  # type: ignore[import]


Convos = List[Any]
Contact = Dict[str, str]
Contacts = List[Contact]


def source_location() -> Path:
    """Get OS-dependent source location."""
    home = Path.home()
    paths = {
        "linux": home / ".config/Signal",
        "linux2": home / ".config/Signal",
        "win32": home / "AppData/Roaming/Signal",
    }
    try:
        source_path = paths[sys.platform]
    except KeyError:
        print("Please manually enter Signal location using --source.")
        raise Exit(code=1)

    return source_path


def default_timestamp() -> int:
    dt_now = datetime.now()
    # Build local datetime at 00:00 current date ant return UTC timestamp in ms
    dt = datetime(dt_now.year, dt_now.month, dt_now.day)
    return int((dt.astimezone(timezone.utc)).timestamp()*1000)


def fetch_data(
    db_file: Path,
    key: str,
    ts: int,
    groups: Optional[str] = None,
    list_chats: Optional[bool] = False,
) -> Tuple[Convos, Contacts]:
    """Load SQLite data into dicts."""
    contacts: Contacts = []
    convos: Convos = []

    db = sqlcipher.connect(str(db_file))
    c = db.cursor()
    # param binding doesn't work for pragmas, so use a direct string concat
    c.execute(f"PRAGMA KEY = \"x'{key}'\"")
    c.execute("PRAGMA cipher_page_size = 4096")
    c.execute("PRAGMA kdf_iter = 64000")
    c.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA512")
    c.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA512")

    query = "SELECT type, id, name FROM conversations"
    c.execute(query)
    for result in c:
        if result[0] == "group":
            contacts.append({
                "id": result[1],
                "name": result[2]
            })

    if not list_chats:
        if groups:
            query = (f"SELECT m.json "
                     f"FROM messages m, conversations c, conversations c2 "
                     f"WHERE m.type = 'incoming' and m.conversationId = c.id and m.sourceuuid = c2.uuid and c.Name in ({groups}) and m.sent_at > {ts} "
                     f"ORDER BY sent_at")
        else:
            query = (f"SELECT m.json "
                     f"FROM messages m, conversations c, conversations c2 "
                     f"WHERE m.type = 'incoming' and m.conversationId = c.id and m.sourceuuid = c2.uuid and m.sent_at > {ts} "
                     f"ORDER BY sent_at")

        c.execute(query)
        for message in c:
            convos.append(json.loads(message[0]))

    return convos, contacts


def main(
    source: Optional[Path] = Option(
        None, help="Path to Signal source database"),
    chats: str = Option(
        None, help="Comma-separated chat names to include"
    ),
    ts: int = Option(
        None, help="UNIX timestamp ms"),
    list_chats: bool = Option(
        False, "--list-chats", "-l", help="List available chats and exit"
    ),
) -> None:
    """Read the Signal directory and output chats as json."""

    if source:
        src = Path(source).expanduser().absolute()
    else:
        src = source_location()
    source = src / "config.json"
    db_file = src / "sql" / "db.sqlite"

    # Read sqlcipher key from Signal config file
    if source.is_file():
        with open(source, encoding="utf-8") as conf:
            key = json.loads(conf.read())["key"]
    else:
        print(f"Error: {source} not found in directory {src}")
        raise Exit(code=1)

    # Read chats from export_config file
    if chats is None:
        if os.path.isfile("export_config.json"):
            with open("export_config.json", encoding='utf-8') as conf:
                chats = json.loads(conf.read())["groups"]

    if ts is None:
        ts = default_timestamp()

    convos, contacts = fetch_data(
        db_file,
        key,
        groups=chats,
        ts=ts,
        list_chats=list_chats
    )

    if list_chats:
        for contact in contacts:
            print("'{}'".format(contact["name"]))
        raise Exit()

    filename = f"output/json_data_{ts}.json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as outfile:
        json.dump({"groups_name_id": contacts, "messsages": convos},
                  outfile, indent=4, ensure_ascii=False)
    print("Signal database exported as {}".format(filename))


def cli() -> None:
    """cli."""
    run(main)


if __name__ == "__main__":
    cli()
