import unittest
from nzbandwidth.nzbandwidth import calculate_rate
import configparser


class TestCalculateRate(unittest.TestCase):

    def setUp(self):
        self.Config = configparser.ConfigParser()
        self.Config.read('nzbandwidth/config.ini')

    def test_mode_high(self):
        self.assertEqual(calculate_rate(int(self.Config.get('nzbandwidth', 'connection_speed')), "high"), 61440)

if __name__ == '__main__':
    unittest.main()
