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
    where_lst = ["{0}={1}".format(k, "'{0}'".format(v) if isinstance(v, str) else v) for k, v in where.items()]
    cursor.execute("DELETE FROM {0} WHERE {1}".format(tbl, " AND ".join(where_lst)))
