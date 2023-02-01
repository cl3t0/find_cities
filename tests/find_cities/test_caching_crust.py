from find_cities.api_int import AbstractApi
from find_cities.cacher_int import AbstractCacher
from find_cities.caching_crust import CachingCrust
from find_cities.utils import date_range
from datetime import date, timedelta
from typing import Dict, Optional, Tuple


class MockedApi(AbstractApi):
    def get_price_between_at_next_7_days(
        self, airport1: str, airport2: str, choosen_date: date
    ) -> Dict[date, float]:
        data = {
            ("A", "B", date(year=2023, month=1, day=1)): 7,
            ("A", "B", date(year=2023, month=1, day=2)): 5,
            ("A", "B", date(year=2023, month=1, day=3)): 3,
            ("A", "B", date(year=2023, month=1, day=4)): 2,
            ("A", "B", date(year=2023, month=1, day=5)): 3,
            ("A", "B", date(year=2023, month=1, day=6)): 6,
            ("A", "B", date(year=2023, month=1, day=7)): 6,
            #
            ("A", "B", date(year=2023, month=1, day=7 + 1)): 7,
            ("A", "B", date(year=2023, month=1, day=7 + 2)): 5,
            ("A", "B", date(year=2023, month=1, day=7 + 3)): 3,
            ("A", "B", date(year=2023, month=1, day=7 + 4)): 2,
            ("A", "B", date(year=2023, month=1, day=7 + 5)): 3,
            ("A", "B", date(year=2023, month=1, day=7 + 6)): 6,
            ("A", "B", date(year=2023, month=1, day=7 + 7)): 6,
        }
        return {
            day: data[(airport1, airport2, day)]
            for day in date_range(choosen_date, choosen_date + timedelta(days=7))
        }


class InMemoryCacher(AbstractCacher):
    def __init__(self) -> None:
        self.data: Dict[Tuple[str, str, date], float] = {}

    def store(
        self, airport1: str, airport2: str, chosen_date: date, price: float
    ) -> None:
        self.data[(airport1, airport2, chosen_date)] = price

    def get(self, airport1: str, airport2: str, chosen_date: date) -> Optional[float]:
        return self.data.get((airport1, airport2, chosen_date))


def test_storage_1():
    cacher = InMemoryCacher()
    client = MockedApi()
    caching_client = CachingCrust(client, cacher)
    result = caching_client.get_price_between_at_next_7_days(
        "A", "B", date(year=2023, month=1, day=1)
    )
    expected_data_cached = {
        ("A", "B", date(year=2023, month=1, day=1)): 7,
        ("A", "B", date(year=2023, month=1, day=2)): 5,
        ("A", "B", date(year=2023, month=1, day=3)): 3,
        ("A", "B", date(year=2023, month=1, day=4)): 2,
        ("A", "B", date(year=2023, month=1, day=5)): 3,
        ("A", "B", date(year=2023, month=1, day=6)): 6,
        ("A", "B", date(year=2023, month=1, day=7)): 6,
    }
    expected_result = {
        date(year=2023, month=1, day=1): 7,
        date(year=2023, month=1, day=2): 5,
        date(year=2023, month=1, day=3): 3,
        date(year=2023, month=1, day=4): 2,
        date(year=2023, month=1, day=5): 3,
        date(year=2023, month=1, day=6): 6,
        date(year=2023, month=1, day=7): 6,
    }
    assert result == expected_result
    assert cacher.data == expected_data_cached


def test_storage_2():
    cacher = InMemoryCacher()
    client = MockedApi()
    caching_client = CachingCrust(client, cacher)
    _ = caching_client.get_price_between_at_next_7_days(
        "A", "B", date(year=2023, month=1, day=1)
    )
    result = caching_client.get_price_between_at_next_7_days(
        "A", "B", date(year=2023, month=1, day=3)
    )
    expected_data_cached = {
        ("A", "B", date(year=2023, month=1, day=1)): 7,
        ("A", "B", date(year=2023, month=1, day=2)): 5,
        ("A", "B", date(year=2023, month=1, day=3)): 3,
        ("A", "B", date(year=2023, month=1, day=4)): 2,
        ("A", "B", date(year=2023, month=1, day=5)): 3,
        ("A", "B", date(year=2023, month=1, day=6)): 6,
        ("A", "B", date(year=2023, month=1, day=7)): 6,
        ("A", "B", date(year=2023, month=1, day=7 + 1)): 7,
        ("A", "B", date(year=2023, month=1, day=7 + 2)): 5,
        ("A", "B", date(year=2023, month=1, day=7 + 3)): 3,
        ("A", "B", date(year=2023, month=1, day=7 + 4)): 2,
        ("A", "B", date(year=2023, month=1, day=7 + 5)): 3,
        ("A", "B", date(year=2023, month=1, day=7 + 6)): 6,
        ("A", "B", date(year=2023, month=1, day=7 + 7)): 6,
    }
    expected_result = {
        date(year=2023, month=1, day=3): 3,
        date(year=2023, month=1, day=4): 2,
        date(year=2023, month=1, day=5): 3,
        date(year=2023, month=1, day=6): 6,
        date(year=2023, month=1, day=7): 6,
        date(year=2023, month=1, day=7 + 1): 7,
        date(year=2023, month=1, day=7 + 2): 5,
    }
    assert result == expected_result
    assert cacher.data == expected_data_cached