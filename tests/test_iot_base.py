import unittest
import os
from iot_base_app import ConfigFile

class Test1BaseApp(unittest.TestCase):
    def test_01_config(self):
        input_path = '../../wp_iot/var_deployment/Output Files'
        config_file = ConfigFile(f'{input_path}/iot_base_app.config.json')
        self.assertIsNotNone(config_file)
        self.assertTrue(config_file.contains('logging'))
        self.assertTrue(config_file.contains('config_db_path'))
        self.assertTrue(config_file.contains('statistics_db_path'))
        self.assertTrue(config_file.contains('process_groups'))

        conf_part = config_file['logging']
        self.assertIsNotNone(conf_part)
        self.assertIsInstance(conf_part, dict)

        conf_part = config_file['config_db_path']
        self.assertIsNotNone(conf_part)
        self.assertIsInstance(conf_part, str)
        self.assertTrue(os.path.exists(f'{input_path}/{conf_part}'))
        
        conf_part = config_file['statistics_db_path']
        self.assertIsNotNone(conf_part)
        self.assertIsInstance(conf_part, str)
        self.assertTrue(os.path.exists(f'{input_path}/{conf_part}'))

        conf_part = config_file['process_groups']
        self.assertIsNotNone(conf_part)
        self.assertIsInstance(conf_part, list)
        self.assertTrue(len(conf_part) > 0)
        for num in conf_part:
            self.assertIsInstance(num, int)

if __name__ == '__main__':
    unittest.main(verbosity=5)
