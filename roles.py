class Role:
    def __init__(self, name):
        self.name = name

class Mafia(Role):
    def __init__(self):
        super().__init__('Mafia')
        self.power = 'Kill'

class Detective(Role):
    def __init__(self):
        super().__init__('Detective')
        self.power = 'Investigate'

class Civilian(Role):
    def __init__(self):
        super().__init__('Civilian')
        self.power = 'None'

class Doctor(Role):
    def __init__(self):
        super().__init__('Doctor')
        self.power = 'Save one player per night'