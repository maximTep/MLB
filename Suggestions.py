from DataBase import DataBase


class Suggestions:
    def __init__(self, user_tg_id: int, database: DataBase):
        self.user_tg_id: int = user_tg_id
        self.database: DataBase = database
        self.suggestions_lst: list[int] = []
        self.cnt: int = 50
        
    def get_pair_suggestion_id(self) -> int:
        if len(self.suggestions_lst) == 0:
            self.suggestions_lst = self.database.get_pair_suggestion_ids(self.user_tg_id, self.cnt)
        if len(self.suggestions_lst) == 0:
            return None
        suggestion_id = self.suggestions_lst.pop()
        return suggestion_id

    def clear_suggestions(self):
        self.suggestions_lst.clear()
            