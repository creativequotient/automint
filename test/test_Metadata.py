import unittest

from automint.utils import validate_metadata


class MetadataTests(unittest.TestCase):
    def test_validate_metadata_positive(self):
        # Positive test cases

        self.assertTrue(validate_metadata('test/metadata_test_1.json', ['tokenA', 'tokenB'], '123'))

        # Negative test cases

        # Wrong tokens
        with self.assertRaises(Exception):
            validate_metadata('test/metadata_test_1.json', ['tokenA', 'tokenC'], '123')

        # Wrong policy ID
        with self.assertRaises(Exception):
            validate_metadata('test/metadata_test_1.json', ['tokenA', 'tokenB'], '12345')

        # No "721" key
        with self.assertRaises(Exception):
            validate_metadata('test/metadata_test_2.json', ['tokenA', 'tokenB'], '12345')

        # Duplicate top level keys (besides 721)
        with self.assertRaises(Exception):
            validate_metadata('test/metadata_test_3.json', ['tokenA', 'tokenB'], '123')
