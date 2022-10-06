
class Users:
    all_users = dict()

    def __init__(self, user_id):

        self.command = None
        self.city = None
        self.check_in = None
        self.check_out = None
        self.hotels_count = None
        Users.add_user(user_id, self)

    @staticmethod
    def get_user(user_id):
        if Users.all_users.get(user_id) is None:
            new_user = Users(user_id)
            return new_user
        return Users.all_users.get(user_id)

    @classmethod
    def add_user(cls, user_id, user):
        cls.all_users[user_id] = user
