# Database Management and Game Statistics

class Database:
    def __init__(self):
        self.data = {}

    def add_record(self, game_id, stats):
        self.data[game_id] = stats

    def get_record(self, game_id):
        return self.data.get(game_id, "No record found.")

    def update_record(self, game_id, stats):
        if game_id in self.data:
            self.data[game_id] = stats
            return True
        return False

    def delete_record(self, game_id):
        if game_id in self.data:
            del self.data[game_id]
            return True
        return False

# Example Usage
if __name__ == '__main__':
    db = Database()
    db.add_record(1, {'score': 100, 'level': 5})
    print(db.get_record(1))
    db.update_record(1, {'score': 150, 'level': 6})
    print(db.get_record(1))
    db.delete_record(1)
    print(db.get_record(1))