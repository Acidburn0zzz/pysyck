
import unittest

import _syck

import gc

class TestNodes(unittest.TestCase):

    def testBaseNode(self):
        self.assertRaises(TypeError, lambda: _syck.Node())

    def testScalar(self):
        self.assert_(issubclass(_syck.Scalar, _syck.Node))
        scalar = _syck.Scalar()
        self.assertEqual(scalar.kind, 'scalar')
        self.assertEqual(scalar.value, '')
        self.assertEqual(scalar.anchor, None)
        self.assertEqual(scalar.tag, None)
        self.assertEqual(scalar.style, None)
        self.assertEqual(scalar.indent, 0)
        self.assertEqual(scalar.width, 0)
        self.assertEqual(scalar.chomp, None)
        scalar = _syck.Scalar('a value', tag='a_tag', style='fold',
                indent=4, width=80, chomp='+')
        self.assertEqual(scalar.value, 'a value')
        self.assertEqual(scalar.tag, 'a_tag')
        self.assertEqual(scalar.style, 'fold')
        self.assertEqual(scalar.indent, 4)
        self.assertEqual(scalar.width, 80)
        self.assertEqual(scalar.chomp, '+')
        self.assertRaises(TypeError, lambda: setattr(scalar, 'kind', 'map'))
        self.assertRaises(TypeError, lambda: setattr(scalar, 'value', None))
        self.assertRaises(TypeError, lambda: setattr(scalar, 'value', []))
        self.assertRaises(TypeError, lambda: setattr(scalar, 'tag', []))
        self.assertRaises(TypeError, lambda: setattr(scalar, 'style', 'block'))
        self.assertRaises(TypeError, lambda: setattr(scalar, 'style', []))
        self.assertRaises(TypeError, lambda: setattr(scalar, 'indent', '1'))
        self.assertRaises(TypeError, lambda: setattr(scalar, 'width', '1'))
        self.assertRaises(TypeError, lambda: setattr(scalar, 'chomp', []))
        scalar.value = 'another value'
        scalar.tag = 'another_tag'
        scalar.style = 'literal'
        scalar.indent = 2
        scalar.width = 100
        scalar.chomp = '-'
        self.assertEqual(scalar.value, 'another value')
        self.assertEqual(scalar.tag, 'another_tag')
        self.assertEqual(scalar.style, 'literal')
        self.assertEqual(scalar.indent, 2)
        self.assertEqual(scalar.width, 100)
        self.assertEqual(scalar.chomp, '-')
        scalar.tag = None
        scalar.style = None
        self.assertEqual(scalar.tag, None)
        self.assertEqual(scalar.style, None)

    def testSeq(self):
        self.assert_(issubclass(_syck.Seq, _syck.Node))
        seq = _syck.Seq()
        self.assertEqual(seq.kind, 'seq')
        self.assertEqual(seq.value, [])
        self.assertEqual(seq.anchor, None)
        self.assertEqual(seq.tag, None)
        self.assertEqual(seq.style, None)
        value = [_syck.Scalar(str(k)) for k in range(10)]
        seq = _syck.Seq(value, tag='a_tag', style='inline')
        self.assertEqual(seq.value, value)
        self.assertEqual(seq.tag, 'a_tag')
        self.assertEqual(seq.style, 'inline')
        value = [_syck.Scalar(str(k)) for k in range(20)]
        seq.value = value
        seq.tag = 'another_tag'
        seq.style = 'block'
        self.assertEqual(seq.value, value)
        self.assertEqual(seq.tag, 'another_tag')
        self.assertEqual(seq.style, 'block')

    def testMap(self):
        self.assert_(issubclass(_syck.Map, _syck.Node))
        map = _syck.Map()
        self.assertEqual(map.kind, 'map')
        self.assertEqual(map.value, {})
        self.assertEqual(map.anchor, None)
        self.assertEqual(map.tag, None)
        self.assertEqual(map.style, None)
        value = dict([(_syck.Scalar(str(k)), _syck.Scalar(str(-k))) for k in range(10)])
        map = _syck.Map(value, tag='a_tag', style='inline')
        self.assertEqual(map.value, value)
        self.assertEqual(map.tag, 'a_tag')
        self.assertEqual(map.style, 'inline')
        value = dict([(_syck.Scalar(str(k)), _syck.Scalar(str(-k))) for k in range(20)])
        map.value = value
        map.tag = 'another_tag'
        map.style = 'block'
        self.assertEqual(map.value, value)
        self.assertEqual(map.tag, 'another_tag')
        self.assertEqual(map.style, 'block')

    def testGarbage(self):
        gc.collect()
        scalar1 = _syck.Scalar()
        scalar2 = _syck.Scalar()
        seq = _syck.Seq()
        map1 = _syck.Map()
        map2 = _syck.Map()
        map1.value[scalar1] = seq
        map1.value[scalar2] = map2
        map2.value[scalar1] = map1
        map2.value[scalar2] = seq
        seq.value.append(map1)
        seq.value.append(map2)
        del scalar1, scalar2, seq, map1, map2
        self.assertEqual(gc.collect(), 8)

