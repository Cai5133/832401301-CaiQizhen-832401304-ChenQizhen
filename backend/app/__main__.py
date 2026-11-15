"""Explicit database initialization and optional fictional demo data."""
import argparse

from .database import Database, default_database_path
from .schemas import ContactInput
from .services.contacts import insert_contact
from .services.excel import sample_contacts


def main():
    parser = argparse.ArgumentParser(description="通讯录数据库工具")
    parser.add_argument("command", choices=["init", "seed"])
    parser.add_argument("--database", default=None, help="数据库路径，默认 ADDRESS_BOOK_DB")
    args = parser.parse_args()
    database = Database(args.database or default_database_path())
    database.initialize()
    if args.command == "seed":
        with database.connect() as connection, connection:
            if connection.execute("SELECT count(*) FROM contacts").fetchone()[0]:
                parser.exit(1, "数据库非空，未插入演示数据。请使用单独的空数据库。\n")
            for contact in sample_contacts():
                insert_contact(connection, ContactInput(**contact))
        print("已写入 1 位虚构演示联系人")
    else:
        print("数据库已初始化")


if __name__ == "__main__":
    main()
