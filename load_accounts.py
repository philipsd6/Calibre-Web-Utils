#!/usr/bin/env python3
import csv
import os.path
import argparse
import sys
import sqlite3
from werkzeug.security import generate_password_hash

TEMPLATE_NICKNAME = "template_account"
APP_DB = "~/.local/lib/calibre-web/app.db"


def merge_values(template_account, infile, default_domain=None, default_password=None):
    """
    Merge the contents of the infile with the template_account dict to generate the row
    values to insert. Uses the default domain and password to fill in when applicable.
    """
    if default_password:
        default_password = generate_password_hash(default_password)

    with infile as f:
        head = next(f)
        f.seek(0)
        if "\t" in head:
            reader = csv.DictReader(f, dialect="excel-tab")
        else:
            reader = csv.DictReader(f)

        for rec in reader:
            row = template_account.copy()
            for k, v in rec.items():
                if k.lower() == "password":
                    # This makes the insert a LOT slower...
                    row["password"] = generate_password_hash(v)
                elif k.lower() in row:
                    row[k.lower()] = v
            if "password" not in rec and default_password:
                row["password"] = default_password
            if "nickname" not in rec and "email" in rec:
                row["nickname"] = rec["email"]
            elif "nickname" in rec and "email" not in rec and default_domain:
                row["email"] = f"{rec['nickname']}@{default_domain}"

            yield tuple(row.values())


def trace_callback(statement):
    print(statement)


def progress_handler():
    print(".", end="", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Load Calibre-Web accounts from TSV/CSV file",
    )
    parser.add_argument(
        "--db",
        default=APP_DB,
        help="The SQLite3 database for the Calibre-Web application (Default: %(default)s)",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Show the accounts that would be created",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Display the SQL statements executed"
    )
    parser.add_argument(
        "--template-nickname",
        default=TEMPLATE_NICKNAME,
        help="The nickname of the account to base the new accounts on",
    )
    parser.add_argument(
        "--domain",
        help="The domain for these nicknames, if not email is specified in the input file",
    )
    parser.add_argument(
        "--password",
        help="The password for the new accounts if not specified in the input file",
    )
    parser.add_argument(
        "infile",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="An input CSV file with nickname, and optionally email and password",
    )

    args = parser.parse_args()
    db = os.path.abspath(os.path.expanduser(args.db))

    try:
        con = sqlite3.connect(db)
        con.row_factory = sqlite3.Row
        with con as cur:
            template_account = cur.execute(
                "SELECT * FROM user WHERE nickname = ?", (args.template_nickname,)
            ).fetchone()

        if not template_account:
            parser.error(f"Template account '{args.template_nickname}' doesn't exist!")

        # Now we process that into what we want to insert, knowing that ID is an
        # autoincrement column so we'll just drop that one:
        template_account = dict(zip(template_account.keys(), template_account))
        del template_account["id"]
        statement = (
            "INSERT OR IGNORE INTO user("
            + ", ".join(template_account.keys())
            + ") VALUES ("
            + ", ".join("?" * len(template_account))
            + ")"
        )

        row_generator = merge_values(
            template_account, args.infile, args.domain, args.password
        )

        if args.debug:
            con.set_trace_callback(trace_callback)
        else:
            con.set_progress_handler(progress_handler, 300)
            print("Loading", end="")

        with con as cur:
            res = cur.executemany(statement, row_generator)
            if args.dry_run:
                con.set_trace_callback(trace_callback)
                cur.execute("rollback")

        if args.dry_run:
            print(f"Would have loaded {res.rowcount} accounts")
        else:
            if not args.debug:
                print()
            print(f"Loaded {res.rowcount} accounts")

    finally:
        try:
            con.close()
        except:
            pass
