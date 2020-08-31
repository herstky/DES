import unittest

from src.event import Event
from src.species import gases_dict, liquids_dict, solids_dict, State


class TestEvent(unittest.TestCase):
    def setUpClass():
        Event.register_species([('water', State.liquid), ('fiber', State.solid)])

    def setUp(self):
        species = []
        self.volume = 1000
        for species_name, state in Event.registered_species:
            fraction = 1 / len(Event.registered_species)
            species.append((species_name, state, fraction * self.volume))
        self.event = Event(species)
    
    def tearDown(self):
        del self.event

    def test_init(self):
        self.assertEqual(self.event.registered_species[0], ('water', State.liquid))
        self.assertEqual(self.event.registered_species[1], ('fiber', State.solid))
        self.assertEqual(self.event.count, 1)
        self.assertEqual(self.event.species[State.gas], {})
        self.assertEqual(self.event.species[State.liquid], {'water': {'data': liquids_dict['water'], 'volume': 500}})
        self.assertEqual(self.event.species[State.solid], {'fiber': {'data': solids_dict['fiber'], 'volume': 500}})

    def test_register_species(self):
        test_species = ('hydrogen', State.gas)
        Event.register_species(test_species)
        self.assertIn(test_species, self.event.registered_species)
        self.event.registered_species.remove(test_species)

    def test_aggregate_volume(self):
        self.assertEqual(self.event.aggregate_magnitude(), 1000)
        self.event.add_species_volume(('water', State.liquid), 500)
        self.assertEqual(self.event.aggregate_magnitude(), 1500)
        self.event.set_species_magnitude(('fiber', State.solid), 1000)
        self.assertEqual(self.event.aggregate_magnitude(), 2000)
        self.event.split_species_magnitude(('water', State.liquid), .5)
        self.assertEqual(self.event.aggregate_magnitude(), 1500)

    def test_species_volume(self):
        test_species = ('water', State.liquid)
        self.assertEqual(self.event.species_magnitude(test_species), 500)

    def test_set_species_volume(self):
        test_species = ('fiber', State.solid)
        self.event.set_species_magnitude(test_species, 100)
        self.assertEqual(self.event.species_magnitude(test_species), 100)

    def test_add_species_volume(self):
        test_species = ('fiber', State.solid)
        self.event.add_species_volume(test_species, 100)
        self.assertEqual(self.event.species_magnitude(test_species), 600)

    def test_split_species_volume(self):
        test_species = ('water', State.liquid)
        flows = self.event.split_species_magnitude(test_species, .1)
        self.assertEqual(flows[0], 50)
        self.assertEqual(flows[1], 450)
        self.assertEqual(self.event.species_magnitude(test_species), 50)
