
class Users:
    all_users = dict()

    def __init__(self, user_id):
        self.command = None
        self.city = None
        self.city_id = None
        self.check_in = None
        self.check_out = None
        self.min_price = None
        self.max_price = None
        self.min_distance = None
        self.max_distance = None
        self.hotels_count = None
        self.photo_hotels = None
        self.hotel_list = []
        self.action = None
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
