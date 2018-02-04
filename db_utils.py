# get account data from db
def get_db_data(cursor, table="accounts"):
    cursor.execute("SELECT * FROM " + table)
    return cursor.fetchall()

# append data to table
def insert_record(c, tbl, data, formats):
    data_str = []
    for col in formats[tbl]:
        el_str = "'{0}'" if col[1] == "text" else "{0}"
        data_str.append(el_str.format(data[col[0]]))
    c.execute("INSERT INTO {0} VALUES ({1})".format(tbl, ", ".join(data_str)))
    return

# clear the database without destroying unrelated data
def clear_db(cursor, tables):
    for tbl in tables:
        cursor.execute("DROP TABLE IF EXISTS {0}".format(tbl))

# initialize tables if not present
def init_db(cursor, structure):
    for tbl, fields in structure.items():
        fmt_str = ", ".join([" ".join(a) for a in fields])
        cursor.execute('CREATE TABLE IF NOT EXISTS {0} ({1})'.format(tbl, fmt_str))

# remove record from table
def delete_record(cursor, tbl, where):
    cursor.execute("DELETE FROM {0} {1}".format(tbl, dict2where(where)))

# update existing record
def update_record(cursor, tbl, new_data, where):
    cursor.execute("UPDATE {0} SET {1} {2}".format(tbl, dict2csl(new_data), dict2where(where)))

# convert dictionary to list of equals strings
def dict2list(d):
    return ["{0}={1}".format(k, "'{0}'".format(v) if isinstance(v, str) else v)
            for k, v in d.items() if v is not None]

# convert dictionary to comma sep list
def dict2csl(d):
    return ", ".join(dict2list(d))

# convert dictionary to where clause
def dict2where(d):
    return "WHERE " + " AND ".join(dict2list(d)) if len(d) else ""
