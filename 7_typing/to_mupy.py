import json
from typing import Dict, List, Any
from typing import TypeVar, Generic

T = TypeVar('T')
Json = Dict[str, Any]


class Stack(Generic[T]):
    def __init__(self) -> None:
        self.items: List[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> T:
        return self.items.pop()

    def empty(self) -> bool:
        return not self.items

    def __repr__(self):
        return f'Stack[{", ".join([str(i) for i in self.items])}]'


class Metro:
    def __init__(self, metro_id: int, distance: int):
        self.id = metro_id
        self.distance = distance

    def __repr__(self):
        return f'Metro(metro_id={self.id}, distance={self.distance})'


def parse_string(raw_string: str) -> Json:
    return json.loads(raw_string)


def get_metro_stations(raw_string: str) -> Stack[Metro]:
    raw_metro_stations = parse_string(raw_string)['metro_stations']
    result: Stack[Metro] = Stack[Metro]
    result.push('')
    result.push(1)
    for i in raw_metro_stations:
        m = Metro(**i)
        result.push(m)
    return result


def main():
    string = '''{
        "city" : "Москва",
        "street" : "площадь Революции",
        "building" : "3",
        "description" : null,
        "raw" : "Москва, площадь Революции, 3",
        "metro_stations" : [{"metro_id": 2, "distance": 150}, {"metro_id": 5, "distance": 270}],
        "id" : "3"
    }'''

    print(get_metro_stations(string))


main()
