import pyodbc

server = '24.4.203.133'
database = 'tempdb'
username = 'sa'
password = 'Password1!'
driver = '{ODBC Driver 18 for SQL Server}'
import ssl


class Database(object):
    connection = None
    cursor = None

    def __init__(self):
        if Database.connection is None:
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                # Legacy Python that doesn't verify HTTPS certificates by default
                pass
            else:
                # Handle target environment that doesn't support HTTPS verification
                ssl._create_default_https_context = _create_unverified_https_context

            try:
                with pyodbc.connect(
                        'DRIVER=' + driver
                        + ';SERVER=tcp:' + server
                        + ';PORT=1433;DATABASE=' + database
                        + ';UID=' + username
                        + ';PWD=' + password
                        + ";TrustServerCertificate=YES") as conn:
                    with conn.cursor() as cursor:
                        Database.connection = conn
                        Database.cursor = cursor
            except Exception as error:
                print("Error: Connection not established {}".format(error))
        else:
            print("Connection established")

    def execute(self, string_to_execute):
        return self.cursor.execute(string_to_execute)

    def get_rows(self, string_to_execute):
        self.cursor.execute(string_to_execute)
        columns = [column[0] for column in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def count_rows(self, table, column, value):
        string = f"SELECT COUNT(*) as count FROM {table} WHERE {column}={value};"
        print(string)
        return self.get_rows(string)[0]['count']

    def does_value_exist(self, table, column, value):
        string = f"SELECT COUNT(1) as count FROM {table} WHERE {column}={value};"
        print(string)
        rows = self.get_rows(string)
        print("rows",rows)
        if len(rows) == 0:
            return False
        rows = self.get_rows(string)[0]
        return 1 == rows['count']

    def create_user(self, user_info):
        print(user_info, user_info.get('id'))
        string = f"INSERT INTO users VALUES ('{user_info.get('id')}','{user_info.get('given_name')}','{user_info.get('family_name')}','{user_info.get('email')}'); "
        print(string)
        exists = self.does_value_exist("users", "id", user_info.get('id'))
        if not exists:
            self.cursor.execute(string)
            if not exists and self.does_value_exist("users", "id", user_info.get('id')):
                self.connection.commit()
                return True
        return False

    def check_user(self, user_info):
        id = user_info.get("id")
        if self.does_value_exist("users", "id", id):
            print("Exists")
            return True
        else:
            print("Creating Account")
            return self.create_user(user_info)

    def create_db(db):
        string = "CREATE TABLE users (" + \
                 " id    DECIMAL(24,0) NOT NULL," + \
                 " first_name  VARCHAR (50) NOT NULL," + \
                 " last_name  VARCHAR (50) NOT NULL," + \
                 " email VARCHAR (50) NOT NULL," + \
                 " CONSTRAINT PK_users PRIMARY KEY CLUSTERED (id ASC)" + \
                 ");" + \
                 " CREATE NONCLUSTERED INDEX Index_users_1 ON users(id ASC);"
        return db.execute(string)

    def get_portfolio(self, user_info):
        print(user_info, user_info.get('id'))
        string = f"SELECT ticker, shares, datetime FROM portfolios WHERE user_id={user_info.get('id')};"
        print(string)
        self.cursor.execute(string)
        columns = [column[0] for column in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def make_trade(self, user_info, trade):
        # TODO Make table and insert trade information
        # TODO VERIFY ACCT BALANCE CAN AFFORD
        string = f"INSERT INTO portfolios(user_id,ticker,shares) VALUES ({user_info.get('id')},'{trade['ticker']}',{trade['shares']}) "
        print(string)
        total_trades = self.count_rows("portfolios", "ticker", f"'{trade['ticker']}'")
        self.cursor.execute(string)
        if total_trades < self.count_rows("portfolios", "ticker", f"'{trade['ticker']}'"):
            self.connection.commit()
            return True
        return False


if __name__ == "__main__":
    db = Database()
    test_user = {"id": 1, "given_name": "Test", "family_name": "Test", "email": "test@aa.com"}
    print(db.check_user(test_user))
    print(db.make_trade(test_user, {"ticker": "TSLA", "shares": 1}))
    # print(db.get_portfolio(test_user))
