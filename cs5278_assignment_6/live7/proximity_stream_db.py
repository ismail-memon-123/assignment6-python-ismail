from abc import abstractmethod
from typing import TypeVar, Generic, Self, Dict
from collections.abc import Collection
from statistics import mean
from collections import Counter
from multimethod import multimethod
import itertools

from pyxtension.streams import stream

from cs5278_assignment_6.live7.attribute_matcher import AttributeMatcher
from cs5278_assignment_6.live6.position import Position

from cs5278_assignment_6.live6.iterable_geo_hash_factory import IterableGeoHashFactory, IterableGeoHashConcreteFactory
from cs5278_assignment_6.live6.data_and_position import DataAndPosition
from cs5278_assignment_6.live7.attributes_strategy import AttributesStrategy
from cs5278_assignment_6.live6.geo_db_factory import GeoDBFactory
from cs5278_assignment_6.live6.geo_hash import GeoHash
from cs5278_assignment_6.live6.proximity_db import ProximityDB

T = TypeVar("T")
V = TypeVar("V", int, float)


class ProximityStreamDB(ProximityDB[Generic[T]]):
    """
    We are going to begin modifying our database to support basic querying and filtering
    capabilities. To do this, we are going to add support for Python Streams.

    Each data item stored in the database now can have one or more attributes associated
    with it. You can think of the data items as rows and the attributes as the columns/values
    for that row. Each item can have an arbitrary number of attributes -- it does not
    have to be consistent like in a DB.

    Because we want the database to be extensible and support arbitrary data item types,
    we are going to use the strategy pattern to extract the attributes from data items.
    Your modified database should be able to have an AttributesStrategy passed to it
    that can introspect the individual data items in the database. The strategy is
    free to decide what constitutes an attributes on a data item. Each attribute has a
    name, type, and value (basically typed key/value pairs).

    In addition, we are adding support for rolling the database backward to past states.
    The database should track all the changes applied to it and support creating a
    copy that represents the state up to the nth operation being performed (exclusive).
    The nth operation is not included. So, database_state_at_time(1) only includes the
    first operation (e.g., operation at index 0).
    """

    @abstractmethod
    def database_state_at_time(self, n: int) -> Self:
        """
        Provide a method to create a version of the database after the nth operation
        was performed on it.

        For example, if you insert X, insert Y, insert Z on the database, then calling
        database_state_at_time(2) would return the database state after insert Y was called.

        It is OK if your implementation isn't efficient.
        Think about how to use the command pattern for a simple solution.

        @Bonus

        See persistent data structures for a more fun solution (bonus points -- only attempt
        if you complete the version above with the command pattern first)

        See: https://en.wikipedia.org/wiki/Persistent_data_structure

        If you go this route, I recommend that you use a tree and take the path copying
        approach. Look at the "trees" subsection for a helpful diagram of what has to
        happen before you modify the tree.
        """
        raise NotImplementedError
        

    @abstractmethod
    def stream_nearby(self, matcher: AttributeMatcher[V], pos: Position, bits_of_precision: int) -> stream[V]:
        """
        Returns a stream of the values for the specified attribute that are near the specified
        location.

        For example, you could stream the "salePrice" of all houses that are in a specific area,
        and it would return the stream of double values representing the price.

        Your implementation should use an AttributesStrategy to extract the attributes from each
        nearby data item. You then need to return the values for only attributes that the matcher
        returns true for.

        The AttributesStrategy should be used to extract attributes from the *data* stored inside
        the database like this:

        strategy: AttributeStrategy = ...
        dpos: DataAndPosition<...> = ...
        attrs_for_data: Collection[Attribute] = strategy.get_attributes(dpos.get_data())

        If you wanted to get ALL the attributes in the database, you could do something
        approximately like this:

        db: ProximityDB = ...
        data_and_pos: Collection[DataAndPosition[...]] = db.nearby(Position.with_coordinates(0,0), 0)
        data_and_pos.stream().map(lambda dpos: strategy.get_attributes(dpos.get_data())

        And if you wanted to get just the values:

        stream(stream(dataAndPos).map(
            lambda dpos: strategy.get_attributes(dpos.get_data())).map(lambda a: a.getValue())
        )

        This would give you a Stream of Streams...which could be flattened.

        It is important to note that latitude and longitude will not be attributes by
        default, since the attributes are for the *data* and NOT the DataAndPosition.
        """

        raise NotImplementedError


    @abstractmethod
    def average_nearby(self, matcher: AttributeMatcher[V], pos: Position, bits_of_precision: int) -> [V]:
        """
        You will want to rely on your method above.

        Obtain the stream of attribute values and calculate the average value for the attribute.
        """

        raise NotImplementedError

    @abstractmethod
    def min_nearby(self, matcher: AttributeMatcher[V], pos: Position, bits_of_precision: int) -> [V]:
        """
        Obtain the stream of attribute values and calculate the min value for the attribute.
        """

        raise NotImplementedError

    @abstractmethod
    def max_nearby(self, matcher: AttributeMatcher[V], pos: Position, bits_of_precision: int) -> [V]:
        """
        Obtain the stream of attribute values and calculate the max value for the attribute.
        """

        raise NotImplementedError

    @abstractmethod
    def histogram_nearby(self, matcher: AttributeMatcher[V], pos: Position,
                         bits_of_precision: int) -> Dict[type(V), int]:
        """
        Obtain the stream of attribute values and produce a histogram of the values.
        """

        raise NotImplementedError
    
class ProximityStreamDBImplementation(ProximityStreamDB):

    positionedMap: list[DataAndPosition[T]]
    # state should have a list of ProximityDB's stored in it. And then we just return the consturcted version of it.
    # the stuff this class does is static. Each operation calls makes a new db.

    def __init__(self, strat: AttributesStrategy[T], bits: int, hash_factory: IterableGeoHashFactory = None):
        self.bits = bits
        if hash_factory is not None:
            self.hash_factory = hash_factory
        else:
            self.hash_factory = IterableGeoHashConcreteFactory()
        self.strat = strat
        self.dap = []
        self.db = []
        self.state = []
        # db should hold array of the iterable geo hashes 
    
    def save_state(self):
        self.state.append(self.clone())
    def clone(self):
        cloned_db = self.__class__(self.strat, self.bits, self.hash_factory)
        cloned_db.dap = self.dap.copy()
        cloned_db.db = self.db.copy()
        cloned_db.state = self.state.copy()
        # add code here to clone other relevant data
        return cloned_db
    
    def database_state_at_time(self, n: int) -> Self:
        """
        Provide a method to create a version of the database after the nth operation
        was performed on it.

        For example, if you insert X, insert Y, insert Z on the database, then calling
        database_state_at_time(2) would return the database state after insert Y was called.

        It is OK if your implementation isn't efficient.
        Think about how to use the command pattern for a simple solution.

        @Bonus

        See persistent data structures for a more fun solution (bonus points -- only attempt
        if you complete the version above with the command pattern first)

        See: https://en.wikipedia.org/wiki/Persistent_data_structure

        If you go this route, I recommend that you use a tree and take the path copying
        approach. Look at the "trees" subsection for a helpful diagram of what has to
        happen before you modify the tree.
        """

        return self.state[n-1]

    def stream_nearby(self, matcher: AttributeMatcher[V], pos: Position, bits_of_precision: int) -> stream[V]:
        """
        Returns a stream of the values for the specified attribute that are near the specified
        location.

        For example, you could stream the "salePrice" of all houses that are in a specific area,
        and it would return the stream of double values representing the price.

        Your implementation should use an AttributesStrategy to extract the attributes from each
        nearby data item. You then need to return the values for only attributes that the matcher
        returns true for.

        The AttributesStrategy should be used to extract attributes from the *data* stored inside
        the database like this:

        strategy: AttributeStrategy = ...
        dpos: DataAndPosition<...> = ...
        attrs_for_data: Collection[Attribute] = strategy.get_attributes(dpos.get_data())

        If you wanted to get ALL the attributes in the database, you could do something
        approximately like this:

        db: ProximityDB = ...
        data_and_pos: Collection[DataAndPosition[...]] = db.nearby(Position.with_coordinates(0,0), 0)
        data_and_pos.stream().map(lambda dpos: strategy.get_attributes(dpos.get_data())

        And if you wanted to get just the values:

        stream(stream(dataAndPos).map(
            lambda dpos: strategy.get_attributes(dpos.get_data())).map(lambda a: a.getValue())
        )

        This would give you a Stream of Streams...which could be flattened.

        It is important to note that latitude and longitude will not be attributes by
        default, since the attributes are for the *data* and NOT the DataAndPosition.
        """

        data_and_pos: Collection[DataAndPosition] = self.nearby(pos, bits_of_precision)

        # Get all attributes and their values, then flatten the structure
#        attribute_stream = stream(stream(data_and_pos).map(
#            lambda dpos: self.strat.get_attributes(dpos.get_data())).map(lambda a: a.get_value())
#        )

        # If you need to return an iterable of floats
#        return itertools.chain.from_iterable(attribute_stream)

#        listStream = []
#        for dpos in data_and_pos:
#            listStream.append(self.strat.get_attributes(dpos.get_data()))
#        filtered = filter(matcher , listStream)
#        # Return the flattened stream
#       return stream(filtered)

# i think what i really need to do is return the stream of dataandpos corresponding to matching with matcher.
        listStream = []
        for dpos in data_and_pos:
            listStream.append(self.strat.get_attributes(dpos.get_data()))
        # listStream is of len data_and_pos
        matches = []
        for i in range(len(listStream)):
            for j in range(len(listStream[i])):
                if matcher.matches(listStream[i][j]) == True:
                    matches.append(listStream[i][j].get_value())

        # Return the flattened stream
        st = stream(matches)
        return st


    def average_nearby(self, matcher: AttributeMatcher[V], pos: Position, bits_of_precision: int) -> [V]:
        """
        You will want to rely on your method above.

        Obtain the stream of attribute values and calculate the average value for the attribute.
        """

        streamAtt: stream[V] = self.stream_nearby(matcher, pos, bits_of_precision)
        m = list(streamAtt)
        count = 0.0
        sum = 0.0
        for val in m:
            count = count + 1
            sum = sum + val
        return (sum/count)

    def min_nearby(self, matcher: AttributeMatcher[V], pos: Position, bits_of_precision: int) -> [V]:
        """
        Obtain the stream of attribute values and calculate the min value for the attribute.
        """

        streamAtt: stream[V] = self.stream_nearby(matcher, pos, bits_of_precision)
        return min(list(streamAtt))

    def max_nearby(self, matcher: AttributeMatcher[V], pos: Position, bits_of_precision: int) -> [V]:
        """
        Obtain the stream of attribute values and calculate the max value for the attribute.
        """

        streamAtt: stream[V] = self.stream_nearby(matcher, pos, bits_of_precision)
        return max(list(streamAtt))

    def histogram_nearby(self, matcher: AttributeMatcher[V], pos: Position,
                         bits_of_precision: int) -> Dict[type(V), int]:
        """
        Obtain the stream of attribute values and produce a histogram of the values.
        """

        streamAtt: stream[V] = self.stream_nearby(matcher, pos, bits_of_precision)
        return Counter(list(streamAtt))

    def insert(self, data: DataAndPosition[T]) -> None:
        self.save_state()
        #self.state.append(ProximityStreamDB(self.strat, self.bits, self.hash_factory, self.db))
        self.db.append(self.hash_factory.with_coordinates(data.get_latitude(), data.get_longitude(), self.bits))
        self.dap.append(data)

    @multimethod
    def delete(self, pos: Position) -> Collection[DataAndPosition[T]]:
        self.save_state()
        #change state
        answer = []
        geoHash = GeoHash.geo_hash(pos.get_latitude(), pos.get_longitude(), self.bits)
        #self.state.append(ProximityStreamDB(self.strat, self.bits, self.hash_factory, self.db))
        for i in range(len(self.db)):
            if (self.db[i].bits == geoHash):
                self.db.pop(i)
                a = self.dap.pop(i)
                answer.append(a)
        return answer


    @multimethod
    def delete(self, pos: Position, bits_of_precision: int) -> Collection[DataAndPosition[T]]:
        # change state
        self.save_state()
        #self.state.append(ProximityStreamDB(self.strat, self.bits, self.hash_factory, self.db))
        answer = []
        geoHash = GeoHash.geo_hash(pos.get_latitude(), pos.get_longitude(), bits_of_precision)
        for i in range(len(self.db)):
            if (self.db[i].prefix(bits_of_precision).bits == geoHash):
                self.db.pop(i)
                a = self.dap.pop(i)
                answer.append(a)
        return answer

    def contains(self, pos: Position, bits_of_precision: int) -> bool:
        geoHash = GeoHash.geo_hash(pos.get_latitude(), pos.get_longitude(), bits_of_precision)
        for i in range(len(self.db)):
            if (self.db[i].prefix(bits_of_precision).bits == geoHash):
                return True
        return False

    def nearby(self, pos: Position, bits_of_precision: int) -> Collection[DataAndPosition[T]]:
        answer = []
        geoHash = self.hash_factory.with_coordinates(pos.get_latitude(), pos.get_longitude(), bits_of_precision).bits
        for i in range(len(self.db)):
            if (self.db[i].prefix(bits_of_precision).bits == geoHash):
                answer.append(self.dap[i])
        return answer