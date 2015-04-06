import unittest

from FileBasedStorageTest import *
FileBasedOWLSuite = unittest.TestLoader().loadTestsFromTestCase(FileBasedStorageOWLTest)
storageSuite = unittest.TestSuite([FileBasedOWLSuite])

from GODiGraphTest import *
GODiGraphSuite = unittest.TestLoader().loadTestsFromTestCase(GODiGraphTest)
graphingSuite = unittest.TestSuite([GODiGraphSuite])

from SteinerTreeTest import *
SteinerTreeSuite = unittest.TestLoader().loadTestsFromTestCase(TestSteinerTree)
steinersuite = unittest.TestSuite([SteinerTreeSuite])

from semGODiGraphTest import *
semGODiGraphSuite = unittest.TestLoader().loadTestsFromTestCase(semGODiGraphTest)
semSuite = unittest.TestSuite([semGODiGraphSuite])
