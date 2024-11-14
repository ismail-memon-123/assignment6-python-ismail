from typing import Dict, Any, Collection

from pyxtension.streams import stream

from cs5278_assignment_6.live7.attribute import Attribute
from cs5278_assignment_6.live7.attributes_strategy import AttributesStrategy


class MapAttributesStrategy(AttributesStrategy[Dict[str, Any]]):
    @staticmethod
    def get_attributes(data: Dict[str, Any]) -> Collection[Attribute]:
        return stream(data.items()).map(lambda e: Attribute(e[0], type(e[1]), e[1])).to_list()
