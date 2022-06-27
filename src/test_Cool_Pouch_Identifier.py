import unittest
from Cool_Pouch_Identifier import postcode_corrector
from Cool_Pouch_Identifier import geocoder
from Cool_Pouch_Identifier import temperature_fetcher
from Cool_Pouch_Identifier import bandfinder
from datetime import datetime

class test_cool_pouch(unittest.TestCase):
    def test_postcode_corrector(self):
        actual = postcode_corrector('NW118NP')
        expected = 'NW11 8NP'
        self.assertEqual(actual,expected)

    def test_geocoder(self):
        actual = geocoder('NW11 8NP')
        expected = ('51.56643', '-0.19724')
        self.assertEqual(actual,expected)

    def test_temperature_fetcher(self):
        Latitude = 53.35197
        Longitude = -2.98643
        date_time_obj = datetime.strptime('2022-2-19', '%Y-%m-%d')
        actual = temperature_fetcher(date_time_obj, Latitude, Longitude)
        expected = (4.2)
        self.assertEqual(actual,expected)

    def test_bandfinder(self):
        actual = bandfinder(8)
        expected = ('B')
        self.assertEqual(actual,expected)

if __name__ == '__main__':
    unittest.main()