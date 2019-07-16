import os
import unittest

import pyConTextNLP.itemData as itemData
import pyConTextNLP.pyConText as pyConText


class SimpleTestCase(unittest.TestCase):
    def test_1(self):
        sent1 = 'IMPRESSION: 1. R/O STUDY DEMONSTRATING NO GROSS EVIDENCE OF SIGNIFICANT PULMONARY EMBOLISM.'
        print(os.getcwd())
        modifiers = itemData.get_items(os.path.join(os.getcwd(),
                                                    "../../KB/pneumonia_modifiers.yml"))
        targets = itemData.get_items(os.path.join(os.getcwd(),
                                                  "../../KB/pneumonia_targets.yml"))
        markup = pyConText.ConTextMarkup()
        markup.setRawText(sent1.lower())

        markup.markItems(modifiers, mode="modifier")
        markup.markItems(targets, mode="target")
        found = False
        for node in markup.nodes(data=True):
            if 'r/o' in str(node):
                found = True
        assert found


if __name__ == '__main__':
    unittest.main()
