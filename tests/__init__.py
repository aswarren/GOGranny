import unittest

from FileBasedStorageTest import *
FileBasedStorageSuite = unittest.TestLoader().loadTestsFromTestCase(FileBasedStorageTest)
storageSuite = unittest.TestSuite([FileBasedStorageSuite])

from GODiGraphTest import *
GODiGraphSuite = unittest.TestLoader().loadTestsFromTestCase(GODiGraphTest)
graphingSuite = unittest.TestSuite([GODiGraphSuite])

from SteinerTreeTest import *
SteinerTreeSuite = unittest.TestLoader().loadTestsFromTestCase(TestSteinerTree)
steinersuite = unittest.TestSuite([SteinerTreeSuite])
