from typing import TypeVar, List, Dict, cast

K = TypeVar("K")
V = TypeVar("V")


class MapUtils:
    @staticmethod
    def of(items: List[object]) -> Dict[K, V]:
        data: Dict[K, V] = {}

        for i in range(0, len(items), 2):
            data[cast(K, items[i])] = cast(V, items[i + 1])

        return data
