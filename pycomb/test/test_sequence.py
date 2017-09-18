from pycomb import combinators as t, context as ctx
from pycomb.test import util
from unittest.case import TestCase


class TestSequence(TestCase):

    def setUp(self):
        self.Point = t.struct({
            'x': t.Number,
            'y': t.Number
        })

        self.MyElement = t.struct({}, 'MyElement')
        self.MySequence = t.sequence(self.MyElement, 'MySequence')
        self.SequenceOfNumbers = t.sequence(t.Number, 'SequenceOfNumbers')
        self.Path = t.sequence(self.Point, 'Path')

        self.PathOfPoint = t.sequence(self.Point)
        self.p1 = self.Point({'x': 0, 'y': 0})
        self.p2 = self.Point({'x': 1, 'y': 1})

    # noinspection PyArgumentList
    def test_sequence_type_combinator_then(self):
        with self.assertRaises(TypeError):
            t.sequence()

        with util.throws_with_message(
          'Error on Sequence(Struct{x: Number, y: Number})[0]: expected Struct{x: Number, y: Number} but was int',
          'Error on Sequence(Struct{y: Number, x: Number})[0]: expected Struct{y: Number, x: Number} but was int'):
            t.sequence(self.Point)([1])

    def test_should_throw_with_contextual_error_message_wrong_args(self):
        with util.throws_with_message('Error on SequenceOfNumbers[0]: expected Int or Float but was str'):
            self.SequenceOfNumbers('a')

        with util.throws_with_message('Error on SequenceOfNumbers[1]: expected Int or Float but was list'):
            self.SequenceOfNumbers([1, ['root']])

    def test_hydrate_elements(self):
        instance = self.MySequence([{}])
        self.assertTrue(self.MyElement.is_type(instance[0]))

    def test_hydrate_production(self):
        instance = self.MySequence([{}], ctx=ctx.create(production_mode=True))
        self.assertTrue(self.MyElement.is_type(instance[0]))

    def test_should_be_idempotent(self):
        numbers0 = [1, 2]
        numbers1 = self.SequenceOfNumbers(numbers0)
        numbers2 = self.SequenceOfNumbers(numbers1)
        self.assertEqual((1, 2), numbers1)
        self.assertEqual(numbers1, numbers2)

        path0 = [{'x': 0, 'y': 0}, {'x': 1, 'y': 1}]
    
        path1 = self.Path(path0)
        path2 = self.Path(path1)
        self.assertFalse(path0 == path1)
        self.assertTrue(path1 == path2)

    def test_should_be_idempotent_production(self):
        production_ctx = ctx.create(production_mode=True)
        numbers0 = [1, 2]
        numbers1 = self.SequenceOfNumbers(numbers0, ctx=production_ctx)
        numbers2 = self.SequenceOfNumbers(numbers1, ctx=production_ctx)
        self.assertTrue(numbers0 is numbers1)
        self.assertTrue(numbers1 is numbers2)

        path0 = [{'x': 0, 'y': 0}, {'x': 1, 'y': 1}]
        path1 = self.Path(path0, ctx=production_ctx)
        path2 = self.Path(path1, ctx=production_ctx)
        self.assertTrue(path0 is path1)
        self.assertTrue(path1 is path2)

    def test_should_freeze_the_instance(self):
        instance = self.SequenceOfNumbers([1, 2])
        self.assertEqual(type(instance), tuple)

    def test_sequence_type_should_return_true_when_x_is_list_of_type(self):
        self.assertTrue(self.PathOfPoint.is_type([]))
        self.assertTrue(self.PathOfPoint.is_type([self.p1, self.p2]))
        self.assertFalse(self.PathOfPoint.is_type(1))

    def test_sequence_predicate_used_as_predicate(self):
        self.assertTrue(self.PathOfPoint.is_type([self.p1, self.p2]))

    def test_empty_sequence(self):
        self.PathOfPoint([])
        with util.throws_with_message(
                'Error on Sequence(Struct{x: Number, y: Number}): '
                'expected Sequence(Struct{x: Number, y: Number}) but was NoneType',
                'Error on Sequence(Struct{y: Number, x: Number}): '
                'expected Sequence(Struct{y: Number, x: Number}) but was NoneType'
        ):
            self.PathOfPoint(None)

    def test_custom_sequence(self):
        class ByIndexSequence:
            def __getitem__(self, item):
                if item > 3:
                    raise StopIteration
                return item ** 2

            def __len__(self):
                return 3

        self.assertTrue(t.sequence(t.Number, 'MySequence').is_type(ByIndexSequence()))
        t.sequence(t.Number, 'MySequence')(ByIndexSequence())

    def test_generator(self):
        class MyGenerator:
            def __iter__(self):
                return (x for x in range(3))

        with util.throws_with_message('Error on Sequence(Number): expected Sequence(Number) but was MyGenerator'):
            t.sequence(t.Number)(MyGenerator())
