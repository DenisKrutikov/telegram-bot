from typing import Dict, List, Optional


class Users:
    all_users: Dict[int, 'Users'] = dict()
    """
    Класс описывающий пользователя телеграмм-бота

    Args:
        command (str): команда которую вводит пользователь
        city (str): город в котором ищут отель
        city_id (str): id города
        check_in (datetime): дата заезда в отель
        check_out (datetime): дата выезда из отеля
        min_price (int): минимальная цена за сутка
        max_price (int): максимальная цена за сутки
        hotels_count (int): количество искомых отелей
        photo_hotels (int): количество выводимых фото
        hotel_list (List[Dict]): список отелей
        action (str): действие выезд или заезд в отель
        all_users (Dict[int, Users]): список пользователей
    """

    def __init__(self, user_id: int) -> None:
        self.command: str = ''
        self.city: str = ''
        self.city_id: str = ''
        self.check_in = None
        self.check_out = None
        self.min_price: int = 0
        self.max_price: int = 0
        self.hotels_count: int = 0
        self.photo_hotels: int = 0
        self.hotel_list: List[dict] = []
        self.action: str = ''
        Users.add_user(user_id, self)

    @staticmethod
    def get_user(user_id: int) -> Optional['Users']:
        """
        Метод, который определяет, существует ли пользователь
        с user_id в списке пользователей.

        :return: возвращает пользователя
        :rtype: Users
        """
        if Users.all_users.get(user_id) is None:
            new_user = Users(user_id)
            return new_user
        return Users.all_users.get(user_id)

    @classmethod
    def add_user(cls, user_id: int, user: 'Users') -> None:
        """
        Метод, который добавляет нового пользователя в список пользователей
        """
        cls.all_users[user_id] = user

    def cleaning(self) -> None:
        """
        Метод обнуляющий данные пользователя
        """
        self.city = ''
        self.city_id = ''
        self.check_in = None
        self.check_out = None
        self.min_price = 0
        self.max_price = 0
        self.hotels_count = 0
        self.photo_hotels = 0
        self.hotel_list = []
        self.action = ''
