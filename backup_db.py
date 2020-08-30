#!/usr/bin/env python3
import sys
import os.path
import argparse
import sqlite3

APP_DB = "~/.local/lib/calibre-web/app.db"

parser = argparse.ArgumentParser(
    description="Backup a sqlite3 database",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument("source", default=APP_DB, help="The SQLite3 database to backup")
parser.add_argument("destination", nargs="?", help="The destination to backup to")
parser.add_argument(
    "--pages", type=int, default=1, help="The number of pages to handle in each loop"
)

args = parser.parse_args()

source = os.path.abspath(os.path.expanduser(args.source))
if args.destination:
    dest = os.path.abspath(os.path.expanduser(args.destination))
else:
    dest = "%s-backup%s" % os.path.splitext(source)

# https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
def progress(status, remaining, total):
    # define SQLITE_OK           0   /* Successful result */
    # define SQLITE_DONE        101  /* sqlite3_step() has finished executing */
    rc = ""
    if status and status != 101:
        rc = f" [Error {status}]"
    count = total - remaining
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    pct = round(100.0 * count / float(total), 1)
    bar = "=" * filled_len + "-" * (bar_len - filled_len)
    print(f"[{bar}] {pct}%{rc}\r", end="", flush=True)


try:
    con = sqlite3.connect(source)
    con.execute("VACUUM")
    print(f"Repacked source {source}")

    bkp = sqlite3.connect(dest)
    with bkp:
        con.backup(bkp, pages=args.pages, progress=progress)
    print(f"\nBacked up to {dest}")

finally:
    if con:
        con.close()
    if bkp:
        bkp.close()
