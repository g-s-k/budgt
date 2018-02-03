# get account data from db
def get_db_data(cursor, table="accounts"):
    cursor.execute("SELECT * FROM " + table)
    return cursor.fetchall()

def add_to_table(c, tbl, data):
    data_str = []
    for col in formats[tbl]:
        el_str = "'{0}'" if col[1] == "text" else "{0}"
        data_str.append(el_str.format(data[col[0]]))
    c.execute("INSERT INTO {0} VALUES ({1})".format(tbl, ", ".join(data_str)))
    return
