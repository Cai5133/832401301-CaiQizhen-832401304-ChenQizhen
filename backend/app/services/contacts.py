"""Contact operations use parameterized SQL and one transaction per write."""
import sqlite3

from fastapi import HTTPException

from ..database import Database
from ..schemas import ContactInput


def _require_contact(connection, contact_id):
    row = connection.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="联系人不存在")
    return row


def _serialize(connection, rows):
    # A single methods query avoids one query per contact and SQLite parameter limits.
    result = {row["id"]: {"id": row["id"], "name": row["name"],
                         "isFavorite": bool(row["is_favorite"]), "methods": []} for row in rows}
    if result:
        for method in connection.execute("SELECT * FROM contact_methods ORDER BY id"):
            if method["contact_id"] in result:
                result[method["contact_id"]]["methods"].append(
                    {key: method[key] for key in ("type", "label", "value")})
    return list(result.values())


def list_contacts(database: Database, q: str = "", favorite: bool | None = None):
    conditions, params = [], []
    if q.strip():
        conditions.append("""(instr(casefold(name), ?) > 0 OR EXISTS (
            SELECT 1 FROM contact_methods m WHERE m.contact_id = contacts.id
            AND instr(casefold(m.value), ?) > 0))""")
        params.extend([q.strip().casefold()] * 2)
    if favorite is not None:
        conditions.append("is_favorite = ?")
        params.append(int(favorite))
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    with database.connect() as connection:
        rows = connection.execute("SELECT * FROM contacts" + where + " ORDER BY id", params).fetchall()
        items = _serialize(connection, rows)
    return {"items": items, "total": len(items)}


def get_contact(database: Database, contact_id: int):
    with database.connect() as connection:
        return _serialize(connection, [_require_contact(connection, contact_id)])[0]


def _insert_methods(connection, contact_id, methods):
    connection.executemany(
        "INSERT INTO contact_methods(contact_id, type, label, value) VALUES (?, ?, ?, ?)",
        [(contact_id, method.type, method.label, method.value) for method in methods])


def insert_contact(connection: sqlite3.Connection, contact: ContactInput):
    # Caller owns the transaction so a whole spreadsheet can be committed atomically.
    cursor = connection.execute("INSERT INTO contacts(name, is_favorite) VALUES (?, ?)",
                                (contact.name, int(contact.isFavorite)))
    _insert_methods(connection, cursor.lastrowid, contact.methods)
    return cursor.lastrowid


def create_contact(database: Database, contact: ContactInput):
    with database.connect() as connection, connection:
        contact_id = insert_contact(connection, contact)
        return _serialize(connection, [_require_contact(connection, contact_id)])[0]


def update_contact(database: Database, contact_id: int, contact: ContactInput):
    with database.connect() as connection, connection:
        _require_contact(connection, contact_id)
        connection.execute("UPDATE contacts SET name = ?, is_favorite = ? WHERE id = ?",
                           (contact.name, int(contact.isFavorite), contact_id))
        connection.execute("DELETE FROM contact_methods WHERE contact_id = ?", (contact_id,))
        _insert_methods(connection, contact_id, contact.methods)
        return _serialize(connection, [_require_contact(connection, contact_id)])[0]


def set_favorite(database: Database, contact_id: int, is_favorite: bool):
    with database.connect() as connection, connection:
        _require_contact(connection, contact_id)
        connection.execute("UPDATE contacts SET is_favorite = ? WHERE id = ?",
                           (int(is_favorite), contact_id))
        return _serialize(connection, [_require_contact(connection, contact_id)])[0]


def delete_contact(database: Database, contact_id: int):
    with database.connect() as connection, connection:
        _require_contact(connection, contact_id)
        connection.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
