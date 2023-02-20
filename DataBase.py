import mysql.connector
import subprocess
import threading


class DataBase:
    USERS_TABLE = "users"
    PAIRS_TABLE = "pairs"
    MATCHES_TABLE = "matches"

    def __init__(self):
        self.conn = mysql.connector.connect(user='', password='',
                                            host='',
                                            database='')
        self.curs = self.conn.cursor(buffered=True)
        self.curs.execute(
            """
                        CREATE TABLE IF NOT EXISTS users(
                        id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
                        user_tg_id VARCHAR(255) NOT NULL,
                        tg_username VARCHAR(255),
                        is_registered INTEGER NOT NULL DEFAULT 0,
                        is_enabled INTEGER NOT NULL DEFAULT 1,
                        description VARCHAR(1024),
                        is_female INTEGER NOT NULL DEFAULT 0,
                        is_finding_male INTEGER NOT NULL DEFAULT 0,
                        is_finding_female INTEGER NOT NULL DEFAULT 0,
                        UNIQUE(user_tg_id)
                        );
                        """ 
        )
        self.curs.execute(
            """
                        CREATE TABLE IF NOT EXISTS pairs(
                        id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
                        user_id INTEGER NOT NULL,
                        observable_user_id INTEGER NOT NULL,
                        is_liked INTEGER NOT NULL
                        );
                        """ 
        )
        self.curs.execute(
            """
                        CREATE TABLE IF NOT EXISTS matches(
                        id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
                        user1_id INTEGER NOT NULL,
                        user2_id INTEGER NOT NULL
                        );
                        """ 
        )
        self.conn.commit()

    def get_new_user_id(self):
        self.curs.execute("SELECT MAX(id) FROM users;")
        self.conn.commit()
        new_id = self.curs.fetchone()[0]
        if new_id is None:
            new_id = 1
        else:
            new_id += 1
        return new_id

    def __add_db_item__(self, db_item: dict, table: str):
        req = f"INSERT IGNORE INTO {table}("
        parameteres = []
        for ind, key in enumerate(db_item.keys()):
            if ind == len(db_item.keys()) - 1:
                req += f"{key}) "
            else:
                req += f"{key}, "
        req += "VALUES("
        for ind, val in enumerate(db_item.values()):
            parameteres.append(val)
            if ind == len(db_item.values()) - 1:
                req += f"%s);"
            else:
                req += f"%s, "
        self.curs.execute(req, parameteres)
        self.conn.commit()
    
    def add_user(self, user: dict):
        self.__add_db_item__(user, self.USERS_TABLE)

    def __add_pair__(self, user_tg_id, observable_tg_id, is_liked: bool):
        pair = {
            "user_id": self.get_user_db_id(user_tg_id),
            "observable_user_id": self.get_user_db_id(observable_tg_id),
            "is_liked": is_liked
        }
        self.__add_db_item__(pair, self.PAIRS_TABLE)

    def add_pair_or_update(self, user_tg_id, observable_tg_id, is_liked: bool):
        is_pair_exists = self.is_pair_exists(user_tg_id, observable_tg_id)
        if not is_pair_exists:
            self.__add_pair__(user_tg_id, observable_tg_id, is_liked)
        else:
            self.__update_pair__(user_tg_id, observable_tg_id, is_liked)

    def add_match(self, user1_tg_id, user2_tg_id):
        match = {
            "user1_id": self.get_user_db_id(user1_tg_id),
            "user2_id": self.get_user_db_id(user2_tg_id),
        }
        self.__add_db_item__(match, self.MATCHES_TABLE)
        
    def is_user_registered(self, user_tg_id) -> bool:
        req= f"SELECT * FROM users WHERE user_tg_id = %s AND is_registered = 1;"
        parameters = [user_tg_id]
        self.curs.execute(req, parameters)
        self.conn.commit()
        response = self.curs.fetchall()
        return len(response) > 0

    def is_user_enabled(self, user_tg_id) -> bool:
        req= f"SELECT * FROM users WHERE user_tg_id = %s AND is_enabled = 1;"
        parameters = [user_tg_id]
        self.curs.execute(req, parameters)
        self.conn.commit()
        response = self.curs.fetchall()
        return len(response) > 0

    def register_user(self, user_tg_id):
        req = "UPDATE users SET is_registered=1 WHERE user_tg_id = %s"
        parameters = [user_tg_id]
        self.curs.execute(req, parameters)
        self.conn.commit()

    def update_user_description(self, user_tg_id, description: str):
        req = "UPDATE users SET description=%s WHERE user_tg_id = %s"
        parameters = [description, user_tg_id]
        self.curs.execute(req, parameters)
        self.conn.commit()
    
    def update_user_sex(self, user_tg_id, is_female: bool):
        req = "UPDATE users SET is_female=%s WHERE user_tg_id = %s"
        parameters = [is_female, user_tg_id]
        self.curs.execute(req, parameters)
        self.conn.commit()

    def update_user_preferables(self, user_tg_id, is_finds_male: bool, is_finds_female: bool):
        req = "UPDATE users SET is_finding_male=%s, is_finding_female=%s WHERE user_tg_id = %s"
        parameters = [is_finds_male, is_finds_female, user_tg_id]
        self.curs.execute(req, parameters)
        self.conn.commit()

    def update_user_tg_username(self, user_tg_id, tg_username: str):
        req = "UPDATE users SET tg_username=%s WHERE user_tg_id = %s"
        parameters = [tg_username, user_tg_id]
        self.curs.execute(req, parameters)
        self.conn.commit()
    
    def __update_pair__(self, user_tg_id, observable_tg_id, is_liked: bool):
        req = "UPDATE pairs SET is_liked=%s WHERE user_id = %s AND observable_user_id = %s"
        user_db_id = self.get_user_db_id(user_tg_id)
        observable_db_id = self.get_user_db_id(observable_tg_id)
        parameters = [is_liked, user_db_id, observable_db_id]
        self.curs.execute(req, parameters)
        self.conn.commit()

    def __get_pair_suggestion_id_deprecated__(self, user_tg_id) -> int:  
        req = """SELECT user_tg_id FROM users
                 LEFT JOIN pairs ON users.id = pairs.observable_user_id AND pairs.user_id = %s
                 WHERE pairs.observable_user_id IS NULL
                 AND users.is_registered = 1
                 AND users.is_enabled = 1
                 AND users.user_tg_id != %s
                 LIMIT 1;
        """
        user_db_id = self.get_user_db_id(user_tg_id)
        parameters = [user_db_id, user_tg_id]
        self.curs.execute(req, parameters)
        self.conn.commit()
        result = self.curs.fetchone()
        if result is None: 
            return None
        pair_tg_id = result[0]
        return pair_tg_id

    def get_pair_suggestion_ids(self, user_tg_id, cnt: int) -> list[int]:
        user_db_id = self.get_user_db_id(user_tg_id)
        is_user_finding_male = self.get_user_is_finding_male(user_tg_id)
        is_user_finding_female = self.get_user_is_finding_female(user_tg_id)
        req = """SELECT user_tg_id FROM users
                 WHERE users.is_registered = 1
                 AND users.is_enabled = 1
                 AND users.user_tg_id != %s
                 AND users.id NOT IN
                 (SELECT user1_id from matches WHERE user2_id = %s)
                 AND users.id NOT IN
                 (SELECT user2_id from matches WHERE user1_id = %s)
                 ORDER BY RAND()
                 LIMIT %s;
        """
        # parameters = [user_tg_id, is_user_finding_male, is_user_finding_female, user_db_id, user_db_id, cnt]
        parameters = [user_tg_id, user_db_id, user_db_id, cnt]
        self.curs.execute(req, parameters)
        self.conn.commit()
        result = self.curs.fetchall()
        if result is None: 
            return []
        pairs_tg_ids = []
        for row in result:
            pairs_tg_ids.append(int(row[0]))
        return pairs_tg_ids

    def get_user_description(self, user_tg_id):
        req = "SELECT description FROM users WHERE user_tg_id = %s;"
        parameters = [user_tg_id]
        self.curs.execute(req, parameters)
        self.conn.commit()
        description = self.curs.fetchone()[0]
        return description

    def get_user_tg_username(self, user_tg_id) -> str:
        req = "SELECT tg_username FROM users WHERE user_tg_id = %s;"
        parameters = [user_tg_id]
        self.curs.execute(req, parameters)
        self.conn.commit()
        tg_username = self.curs.fetchone()[0]
        return tg_username

    def get_user_db_id(self, user_tg_id):
        req = "SELECT id FROM users WHERE user_tg_id = %s;"
        parameters = [user_tg_id]
        self.curs.execute(req, parameters)
        self.conn.commit()
        id = self.curs.fetchone()[0]
        return id

    def get_user_is_female(self, user_tg_id) -> int:
        req = "SELECT is_female FROM users WHERE user_tg_id = %s;"
        parameters = [user_tg_id]
        self.curs.execute(req, parameters)
        self.conn.commit()
        is_female = self.curs.fetchone()[0]
        return is_female

    def get_user_is_finding_male(self, user_tg_id) -> int:
        req = "SELECT is_finding_male FROM users WHERE user_tg_id = %s;"
        parameters = [user_tg_id]
        self.curs.execute(req, parameters)
        self.conn.commit()
        is_finding_male = self.curs.fetchone()[0]
        return is_finding_male

    def get_user_is_finding_female(self, user_tg_id) -> int:
        req = "SELECT is_finding_female FROM users WHERE user_tg_id = %s;"
        parameters = [user_tg_id]
        self.curs.execute(req, parameters)
        self.conn.commit()
        is_finding_female = self.curs.fetchone()[0]
        return is_finding_female

    def get_user_matches_tg_user_names(self, user_tg_id) -> list[str]:
        user_db_id = self.get_user_db_id(user_tg_id)
        req = """SELECT tg_username FROM users
                 WHERE id IN
                 (SELECT user1_id from matches WHERE user2_id = %s)
                 OR id IN
                 (SELECT user2_id from matches WHERE user1_id = %s)
        """
        parameters = [user_db_id, user_db_id]
        self.curs.execute(req, parameters)
        self.conn.commit()
        matches_rows = self.curs.fetchall()
        matches = [match_row[0] for match_row in matches_rows]
        return matches

    def is_user_likes_observable(self, user_tg_id, observable_tg_id) -> bool:
        user_db_id = self.get_user_db_id(user_tg_id)
        observable_db_id = self.get_user_db_id(observable_tg_id)
        req = "SELECT * FROM pairs WHERE user_id = %s AND observable_user_id = %s AND is_liked = 1;"
        parameters = [user_db_id, observable_db_id]
        self.curs.execute(req, parameters)
        self.conn.commit()
        result = self.curs.fetchall()
        return len(result) > 0

    def is_pair_exists(self, user_tg_id, observable_tg_id) -> bool:
        user_db_id = self.get_user_db_id(user_tg_id)
        observable_db_id = self.get_user_db_id(observable_tg_id)
        req = "SELECT * FROM pairs WHERE user_id = %s AND observable_user_id = %s"
        parameters = [user_db_id, observable_db_id]
        self.curs.execute(req, parameters)
        self.conn.commit()
        result = self.curs.fetchall()
        return len(result) > 0

    def is_match_exists(self, user_tg_id, observable_tg_id) -> bool:
        user_db_id = self.get_user_db_id(user_tg_id)
        observable_db_id = self.get_user_db_id(observable_tg_id)
        req = "SELECT * FROM matches WHERE user1_id = %s AND user2_id = %s"
        parameters = [user_db_id, observable_db_id]
        self.curs.execute(req, parameters)
        self.conn.commit()
        result = self.curs.fetchall()
        return len(result) > 0

    def drop_pairs_and_matches(self):
        req = "DELETE FROM pairs;"
        self.curs.execute(req)
        req = "DELETE FROM matches;"
        self.curs.execute(req)
        self.conn.commit()

    def get_users_ids(self):
        req = "SELECT * FROM users;"
        self.curs.execute(req)
        self.conn.commit()
        users = self.curs.fetchall()
        ids = []
        for row in users:
            ids.append(row[1])
        return ids
