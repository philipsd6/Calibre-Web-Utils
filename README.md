# Calibre-Web Utils
Utility scripts for managing the [Calibre-Web][calibre-web] application
database, due to a lack of API access for managing user accounts.

## [`backup_db.py`](./backup_db.py)
Back up any SQLite3 database.

    usage: backup_db.py [-h] [--pages PAGES] source [destination]

    Backup a sqlite3 database

    positional arguments:
      source         The SQLite3 database to backup
      destination    The destination to backup to (default: None)

    optional arguments:
      -h, --help     show this help message and exit
      --pages PAGES  The number of pages to handle in each loop (default: 1)

## [`delete_accounts.py`](./delete_accounts.py)
Delete Calibre-Web user accounts based on column filters like
`--nickname` and `--email`.

    usage: delete_accounts.py [-h] [--db DB] [-n] [--nickname NICKNAME [NICKNAME ...]]
                              [--email EMAIL [EMAIL ...]]

    Delete Calibre-Web accounts, based on every combination of the provided filters.
    Note that SQL patterns use '%' and '_' for matching any, or one character respectively.

    optional arguments:
      -h, --help            show this help message and exit
      --db DB               The SQLite3 database for the Calibre-Web application (Default:
                            ~/.local/lib/calibre-web/app.db)
      -n, --dry-run         Show accounts that would be deleted
      --nickname NICKNAME [NICKNAME ...]
                            Patterns to match in the nickname of the account
      --email EMAIL [EMAIL ...]
                            Patterns to match in the email of the account

    For example, to delete all accounts for alice and bob in the example.com and aol.com domains, use:

    delete_accounts.py --nickname alice bob --email %@example.com %@aol.com

## [`load_accounts.py`](./load_accounts.py)
Create Calibre-Web accounts by merging data from a CSV or TSV file with
an existing template user account.

The CSV/TSV file can contain all the columns available in the `user`
table, but typically, only the `email` column and/or `nickname` columns
are needed. If a `password` column is in the CSV/TSV file, it is hashed
before loading.

    usage: load_accounts.py [-h] [--db DB] [-n] [--debug]
                            [--template-nickname TEMPLATE_NICKNAME] [--domain DOMAIN]
                            [--password PASSWORD]
                            [infile]

    Load Calibre-Web accounts from TSV/CSV file

    positional arguments:
      infile                An input CSV file with nickname, and optionally email and
                            password

    optional arguments:
      -h, --help            show this help message and exit
      --db DB               The SQLite3 database for the Calibre-Web application (Default:
                            ~/.local/lib/calibre-web/app.db)
      -n, --dry-run         Show the accounts that would be created
      --debug               Display the SQL statements executed
      --template-nickname TEMPLATE_NICKNAME
                            The nickname of the account to base the new accounts on
      --domain DOMAIN       The domain for these nicknames, if not email is specified in
                            the input file
      --password PASSWORD   The password for the new accounts if not specified in the
                            input file

This script requires [Werkzeug][Werkzeug] for password hashing. You can
install it with:

    pip install --user -r requirements.txt

[calibre-web]: https://github.com/janeczku/calibre-web "Calibre-Web"
[Werkzeug]: https://werkzeug.palletsprojects.com "Werkzeug"
