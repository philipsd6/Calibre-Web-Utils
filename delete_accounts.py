# [[file:~/jrnl/journal.org::*Loading%20up%20Student%20IDs%20in%20Julie's%20Calibre-Web%20instance][Loading up Student IDs in Julie's Calibre-Web instance:1]]
#!/usr/bin/env python3
import os.path
import argparse
import sqlite3
import itertools

## Defaults
APP_DB = "~/.local/lib/calibre-web/app.db"
# These are the columns we expect to filter on
COLUMNS = ["nickname", "email"]


def predicates(args, columns):
    """
    Generates predicates with placeholders for columns:
      join with ' AND ', or 'OR' as desired
    """
    for col in columns:
        if vars(args).get(col):
            yield f"{col} LIKE ?"


def predicate_values(args, columns):
    """
    Generates values matching the generated predicate placeholders
    """
    for values in itertools.product(
        *[vars(args).get(col) or [None] for col in columns]
    ):
        yield tuple([v for v in values if v])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Delete Calibre-Web accounts, based on every combination of the provided "
            "filters.\nNote that SQL patterns use '%' and '_' for matching any, or one "
            "character respectively."
        ),
        epilog=(
            "For example, to delete all accounts for alice and bob in the example.com "
            "and aol.com domains, use:\n\n"
            "%(prog)s --nickname alice bob --email %%@example.com %%@aol.com"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
        help="Show accounts that would be deleted",
    )
    for col in COLUMNS:
        parser.add_argument(
            f"--{col}", nargs="+", help=f"Patterns to match in the {col} of the account"
        )

    args = parser.parse_args()

    if not any([vars(args).get(col) for col in COLUMNS]):
        parser.error("At least one filter parameter is required.")

    # Process args:
    db = os.path.abspath(os.path.expanduser(args.db))
    predicate = " AND ".join(predicates(args, columns=COLUMNS))

    try:
        con = sqlite3.connect(db)
        with con as cur:
            if args.dry_run:
                for values in predicate_values(args, columns=COLUMNS):
                    res = cur.execute(
                        f"SELECT {', '.join(COLUMNS)} FROM user WHERE {predicate}",
                        values,
                    )
                    rows = res.fetchall()
                    widths = [max(map(len, col)) for col in zip(*rows)]
                    for row in rows:
                        print(
                            " ".join([f"{{:{width}}}" for width in widths]).format(*row)
                        )
            else:
                res = cur.executemany(
                    f"DELETE FROM user WHERE {predicate}",
                    predicate_values(args, columns=COLUMNS),
                )
                print(f"Deleted {res.rowcount} accounts")

                if res.rowcount > 0:
                    # Determine the now maximum ID for the user table
                    max_id = cur.execute("SELECT MAX(id) FROM user").fetchone()

                    # Update the current sequence to the new maximum ID
                    cur.execute(
                        "UPDATE sqlite_sequence SET seq=? WHERE name='user'", max_id
                    )
                    print(f"Reset ID sequence to {max_id[0]}")

        if not args.dry_run and res.rowcount > 0:
            con.execute("VACUUM")
            print(f"Repacked {args.db}")

    finally:
        try:
            con.close()
        except:
            pass
# Loading up Student IDs in Julie's Calibre-Web instance:1 ends here
