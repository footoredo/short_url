# Requirements 

- web.py
- python-mysqldb
- pillow
- [python-qrcode](https://github.com/lincolnloop/python-qrcode)

# Usage

1. Deploy MySQL environment.

2. Create a user and a database. Grant all its privileges to the user.

3. Execute `source data.sql` in the database.

4. Create a `configure.py`, of which the format is like the following:

        secret_code = "" # A string contains only [A-Za-z0-9]
    
        db_config = {
            "host": "",
            "user": "",
            "passwd": "",
            "db": "",
            ...etc
        }               # Params of connect(). see http://mysql-python.sourceforge.net/MySQLdb.html#mysqldb
