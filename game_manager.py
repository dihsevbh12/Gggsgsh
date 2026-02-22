# Game Manager

class GameManager:
    def __init__(self):
        self.sessions = {}

    def start_session(self, session_id):
        if session_id not in self.sessions:
            self.sessions[session_id] = {'status': 'active'}
            print(f'Session {session_id} started.')
        else:
            print(f'Session {session_id} already exists.')

    def end_session(self, session_id):
        if session_id in self.sessions:
            self.sessions[session_id]['status'] = 'ended'
            print(f'Session {session_id} ended.')
        else:
            print(f'Session {session_id} does not exist.')

    def get_session_status(self, session_id):
        return self.sessions.get(session_id, 'Session not found.')

# Example usage:
if __name__ == '__main__':
    manager = GameManager()
    manager.start_session('session1')
    print(manager.get_session_status('session1'))
    manager.end_session('session1')
    print(manager.get_session_status('session1'))
