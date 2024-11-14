import math
import random
import sys
import uuid
from typing import List, Iterator, Dict, TypeVar, Any, Set

from cs5278_assignment_6.live6.data_and_position import DataAndPosition
from cs5278_assignment_6.live6.iterable_geo_hash import IterableGeoHash
from cs5278_assignment_6.live6.iterable_geo_hash_factory import IterableGeoHashFactory
from cs5278_assignment_6.live6.position import Position
from cs5278_assignment_6.live7.attributes_strategy import AttributesStrategy
from cs5278_assignment_6.live7.example.building import Building
from cs5278_assignment_6.live7.example.building_attributes_strategy import BuildingAttributesStrategy
from cs5278_assignment_6.live7.proximity_stream_db import ProximityStreamDB
from cs5278_assignment_6.live7.proximity_stream_db_factory import ProximityStreamDBFactory
from cs5278_assignment_6.live9.map_attributes_strategy import MapAttributesStrategy
from cs5278_assignment_6.live9.map_utils import MapUtils

from pyxtension.streams import stream

from cs5278_assignment_6.live9.query_engine import QueryEngine

T = TypeVar("T")


class TestQueryEngine:
    class FakeIterableGeoHash(IterableGeoHash):
        def __init__(self, bits: List[bool]):
            self.bits: List[bool] = bits if bits else []

        def bits_of_precision(self) -> int:
            return len(self.bits)

        def prefix(self, n) -> IterableGeoHash:
            return TestQueryEngine.FakeIterableGeoHash(self.bits[:n])

        def north_neighbor(self) -> IterableGeoHash:
            raise NotImplementedError

        def south_neighbor(self) -> IterableGeoHash:
            raise NotImplementedError

        def west_neighbor(self) -> IterableGeoHash:
            raise NotImplementedError

        def east_neighbor(self) -> IterableGeoHash:
            raise NotImplementedError

        def __iter__(self) -> Iterator[bool]:
            return iter(self.bits)

    @staticmethod
    def new_db(strat: AttributesStrategy[T], hash_dict: Dict[Position,
               List[bool]], bits: int) -> ProximityStreamDB[type(T)]:
        def hash_dict_filter(lat, lon):
            matching_entries = [hash_dict[pos] for pos in hash_dict if
                                pos.get_latitude() == lat and pos.get_longitude() == lon]

            if not len(matching_entries):
                raise KeyError

            assert len(matching_entries) == 1, "Found more than one matching entry in " \
                                               "dictionary! This should not be possible."

            return matching_entries[0]

        return ProximityStreamDBFactory.create(
            strat,
            bits,
            type("IterableGeoHashFactoryImplementation", (IterableGeoHashFactory, object),
                 {"with_coordinates": staticmethod(
                     lambda lat, lon, bs: TestQueryEngine.FakeIterableGeoHash(
                         hash_dict_filter(lat, lon)).prefix(bs)
                 )})()
        )

    @staticmethod
    def random_geo_hash(bits: int) -> List[bool]:
        return random.choices([True, False], k=bits)

    @staticmethod
    def random_position() -> Position:
        lat: float = random.uniform(-90, 90)  # generate a random lat between -90 / 90
        lon: float = random.uniform(-180, 180)  # generate a random lon between -180 / 180

        return Position.with_coordinates(lat, lon)

    # This method randomly generates a set of unique Positions and maps them to a specified
    # number of geohashes. The geohashes are completely random and the mapping is random.

    # For example, randomCoordinateHashMappings(16, 100, 12) would generate 100
    # unique Positions and map them to 12 random geohashes of 16 bits each.
    @staticmethod
    def random_coordinate_hash_mappings(bits: int, total: int, groups: int,
                                        shared_prefix_length: int) -> Dict[Position, List[bool]]:
        avg: int = total // groups  # If it doesn't divide evenly, there is a remainder discarded

        mappings: Dict[Position, List[bool]] = {}
        positions: Set[Position] = set()
        prefixes: Set[str] = set()

        # We generate random unique geohash prefixes of length `sharedPrefixLength`
        # so that we can synthesize groups of positions that will match up to a
        # certain number of bits.
        for i in range(groups):
            prefix: List[bool] = TestQueryEngine.random_geo_hash(shared_prefix_length)
            while TestQueryEngine.to_string(prefix) in prefixes:
                prefix = TestQueryEngine.random_geo_hash(shared_prefix_length)

            prefixes.add(TestQueryEngine.to_string(prefix))

            # Create `avg` Position objects that are
            # unique and map each one to the random hash.
            prefix_suffixes = set()
            for j in range(avg):
                full_hash: List[bool] = prefix.copy()

                suffix = TestQueryEngine.random_geo_hash(bits - shared_prefix_length)
                while TestQueryEngine.to_string(suffix) in prefix_suffixes:
                    suffix = TestQueryEngine.random_geo_hash(bits - shared_prefix_length)

                pos: Position = TestQueryEngine.random_position()
                while pos in positions:
                    pos = TestQueryEngine.random_position()

                positions.add(pos)

                mappings[pos] = full_hash

        return mappings

    @staticmethod
    def to_string(data: List[bool]) -> str:
        hash_string: str = ""

        for b in data:
            hash_string += "1" if b else "0"

        return hash_string

    @staticmethod
    def data(m: Dict[str, Any]) -> DataAndPosition[Dict[str, Any]]:
        class DataAndPositionExtended(DataAndPosition[Dict[str, Any]]):
            @staticmethod
            def get_data() -> Dict[str, Any]:
                return m

            @staticmethod
            def get_latitude() -> float:
                return float(m.get("lat"))

            @staticmethod
            def get_longitude() -> float:
                return float(m.get("lon"))

        return DataAndPositionExtended()

    @staticmethod
    def test_simple_query():
        data: DataAndPosition = TestQueryEngine.data(MapUtils.of(
            ["height", 10.0,
             "age", 32.0,
             "lat", -90.0,
             "lon", -180.0]
        ))

        data2: DataAndPosition = TestQueryEngine.data(MapUtils.of(
            ["age", 56.0,
             "height", 8.0,
             "lat", -90.0,
             "lon", -180.0]
        ))

        db: ProximityStreamDB = ProximityStreamDBFactory().create(MapAttributesStrategy(), 32)
        db.insert(data)
        db.insert(data2)

        # This should produce the same result as the manually created query above
        result2: stream[DataAndPosition[Dict[str, Any]]] = \
            QueryEngine.execute(
                db,
                MapAttributesStrategy(),
                "(find " +
                "     (near -45.0 -145.0 2) " +
                "     (where " +
                "          (> :height 8)" +
                "     )" +
                ")"
            )

        assert result2.size() == 1
        assert {'height': 10.0, 'age': 32.0, 'lat': -90.0, 'lon': -180.0} == result2.toList()[0].get_data()

    @staticmethod
    def random_int(min_bound: int, max_bound: int) -> int:
        return random.randint(min_bound, max_bound)

    @staticmethod
    def greater_than_query(lat: float, lon: float, bits: int, attr_name: str, v: object) -> str:
        return \
            f"(find " \
            f"     (near {lat} {lon} {bits}) " \
            f"     (where " \
            f"          (> :{attr_name} {v})" \
            f"     )" \
            f")"

    @staticmethod
    def test_random_queries_with_fixed_geo() -> None:
        """
        This test randomly generates a series of maps with a fixed
        set of keys and random values for the keys. The test then
        issues a series of queries near 0,0 to check if the query
        accurately filters results based on randomly chosen keys and
        values.
        """

        max_items: int = 1000
        min_items: int = 10
        max_attrs: int = 10
        min_attrs: int = 1
        total_items: int = TestQueryEngine.random_int(min_items, max_items)
        total_attrs: int = TestQueryEngine.random_int(min_attrs, max_attrs)

        attr_names: List[str] = []
        for _ in range(total_attrs):
            attr_names.append(str(uuid.uuid4()))

        items: List[Dict[str, object]] = []
        for _ in range(total_items):
            attr_values: Dict[str, object] = {"id": str(uuid.uuid4()), "lat": 0.0, "lon": 0.0}

            for n in attr_names:
                attr_values[n] = TestQueryEngine.random_int(-sys.maxsize - 1, sys.maxsize)

            items.append(attr_values)

        db: ProximityStreamDB = ProximityStreamDBFactory().create(MapAttributesStrategy(), 32)

        for item in items:
            db.insert(TestQueryEngine.data(item))

        random_queries: int = TestQueryEngine.random_int(0, 100)
        for i in range(random_queries):
            attr_name: str = attr_names[TestQueryEngine.random_int(0, len(attr_names) - 1)]
            value: int = int(stream(items).map(lambda lambda_item: lambda_item.get(attr_name)).to_list()[
                             TestQueryEngine.random_int(0, max(0, len(items) - 2)):][0])

            query: str = TestQueryEngine.greater_than_query(0, 0, 1, attr_name, value)

            result: stream[str] = stream([res.get_data()[attr_name] for res in
                                          QueryEngine.execute(db, MapAttributesStrategy(), query)])

            expected = stream(items).map(lambda lambda_item: lambda_item.get(
                    attr_name)).filter(lambda v: int(v) > value)

            assert result.size() == expected.size()
            assert result.toSet() == expected.toSet()

    @staticmethod
    def test_random_queries():
        # This test randomly generates a set of positions that are
        # artificially assigned to geohashes. The geohashes are constructed
        # such that the positions are guaranteed to fall into N groups that
        # match K bits of their geohashes. The test generates random queries
        # and uses the advance knowledge of what other items are nearby to
        # calculate what the query results should be.

        # A synthetic example:

        # groups = 3
        # sharedPrefixLength = 2
        # bits = 4
        # buildings = 6

        # randomMappings = {
        #      [(-88.01, 0) 1111]
        #      [(-48.01, 90) 1101]
        #      [(-88.01, 20) 1000]
        #      [(20.01, 0) 1001]
        #      [(118.01, -10) 0110]
        #      [(88.01, 10) 0101]
        # }

        # There are three unique prefixes of length 2.
        # [11, 10, 01]

        # Every position has been mapped to a random geohash that
        # starts with one of these prefixes.

        # For any given prefix, we know in advance what positions will
        # map to it.

        # For each position, we can check that all other locations with
        # a matching prefix are returned when we do a nearby search on
        # that position.

        # Note: the hashes are completely random and unrelated to the
        # actual positions on the earth -- it shouldn't matter to your
        # implementation how the position to geohash translation is done,
        # as long as it is consistent

        max_groups: int = 128
        max_bits: int = 256

        groups: int = random.randint(1, max_groups)
        buildings: int = random.randint(groups, 28 * groups)

        # We have to ensure that we have
        # enough bits in the shared prefix
        # to differentiate all the groups and
        # not take forever to randomly generate
        # the unique shared prefixes
        shared_prefix_length: int = \
            random.randint(math.ceil(math.log2(groups)), max_bits - math.ceil(math.log2(buildings // groups)))
        bits: int = \
            shared_prefix_length + \
            random.randint(math.ceil(math.log2(buildings // groups)), max_bits - shared_prefix_length)

        # For debugging.
        # print(f"Testing {buildings} items with {bits} bit hashes and "
        #       f"{shared_prefix_length} shared bits in {groups} groups")

        random_mappings: Dict[Position, List[bool]] = \
            TestQueryEngine.random_coordinate_hash_mappings(bits, buildings, groups, shared_prefix_length)
        db: ProximityStreamDB[Building] = \
            TestQueryEngine.new_db(BuildingAttributesStrategy(), random_mappings, bits)

        hash_to_building_dict: Dict[str, Set[Building]] = {}
        hash_to_sqft: Dict[str, List[float]] = {}
        hash_to_classrooms: Dict[str, List[float]] = {}

        for entry in random_mappings.items():
            pos: Position = entry[0]
            hash_str: str = TestQueryEngine.to_string(entry[1])[:shared_prefix_length]
            b: Building = Building(str(uuid.uuid4()), random.random() * 100000, round(random.random() * 25))
            db.insert(DataAndPosition.with_coordinates(pos.get_latitude(), pos.get_longitude(), b))

            existing: Set[Building] = hash_to_building_dict.get(hash_str, set())
            existing.add(b)
            hash_to_building_dict[hash_str] = existing

            curr: List[float] = hash_to_sqft.get(hash_str, [])
            curr.append(b.get_size_in_square_feet())
            hash_to_sqft[hash_str] = curr

            rooms: List[float] = hash_to_classrooms.get(hash_str, [])
            rooms.append(b.get_classrooms())
            hash_to_classrooms[hash_str] = rooms

        for entry in random_mappings.items():
            pos: Position = entry[0]
            hash_str: str = TestQueryEngine.to_string(entry[1])[:shared_prefix_length]
            at_geo: Set[Building] = hash_to_building_dict.get(hash_str, set())

            value: float = float(stream(at_geo).map(lambda building: building.get_size_in_square_feet()).to_list()[
                                 TestQueryEngine.random_int(0, max(0, len(at_geo) - 2)):][0])

            query: str = TestQueryEngine.greater_than_query(
                pos.get_latitude(), pos.get_longitude(), shared_prefix_length,
                BuildingAttributesStrategy.SIZE_IN_SQUARE_FEET, value
            )

            expected: Set[Building] = \
                stream(at_geo).filter(lambda building: building.get_size_in_square_feet() > value).toSet()

            result: Set[Building] = \
                QueryEngine.execute(db, BuildingAttributesStrategy(), query).map(lambda d: d.get_data()).toSet()

            assert result == expected

        for entry in random_mappings.items():
            pos: Position = entry[0]
            hash_str: str = TestQueryEngine.to_string(entry[1])[:shared_prefix_length]
            at_geo: Set[Building] = hash_to_building_dict.get(hash_str, set())

            value: float = float(stream(at_geo).map(lambda building: building.get_classrooms()).to_list()[
                                 TestQueryEngine.random_int(0, max(0, len(at_geo) - 2)):][0])

            query: str = TestQueryEngine.greater_than_query(
                pos.get_latitude(), pos.get_longitude(), shared_prefix_length,
                BuildingAttributesStrategy.CLASSROOMS, value
            )

            expected: Set[Building] = stream(at_geo).filter(lambda building: building.get_classrooms() > value).toSet()

            result: Set[Building] = \
                QueryEngine.execute(db, BuildingAttributesStrategy(), query).map(lambda d: d.get_data()).toSet()

            assert result == expected
