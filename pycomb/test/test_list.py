from pycomb import combinators as t
from pycomb.test import util
from unittest.case import TestCase

class TestList(TestCase):

    def setUp(self):
        self.Point = t.struct({
            'x': t.Number,
            'y': t.Number
        })

        self.MyElement = t.struct({}, 'MyElement')
        self.MyList = t.list(self.MyElement, 'MyList')
        self.ListOfNumbers = t.list(t.Number, 'ListOfNumbers')
        self.Path = t.list(self.Point, 'Path')

        self.PathOfPoint = t.list(self.Point);
        self.p1 = self.Point({'x': 0, 'y': 0})
        self.p2 = self.Point({'x': 1, 'y': 1})

    def test_list_type_combinator_then(self):
        util.throws_with_message(
          lambda: t.list(),
          'list() missing 1 required positional argument: \'combinator_element\'')

        util.throws_with_message(
          lambda: t.list(self.Point)([1]),
          'Invalid name supplied to List(Struct{x: Number, y: Number}): expected str for \'name\'')

    def test_should_throw_with_contextual_error_message_wrong_args(self):
        util.throws_with_message(
            lambda: self.ListOfNumbers([]),
            'Error on ListOfNumbers: missing 1 required positional argument: \'x\'')

        util.throws_with_message(
            lambda: self.ListOfNumbers('a'),
            'Error on ListOfNumbers[0]: expected Int or Float but was str'
        )

        util.throws_with_message(
            lambda: self.ListOfNumbers([1, ['root']]),
            'Error on ListOfNumbers[1]: expected Int or Float but was list')

    def test_hydrate_elements(self):
        instance = self.MyList([{}])
        self.assertTrue(self.MyElement.is_type(instance[0]))

    def test_hydrate_production(self):
    #    , util.production(function () {
    #      var instance = MyList([{}]);
    #      assert.equal(MyElement.is(instance[0]), true);
    #    }));
        self.fail(msg='TODO: Implement production mode!')


    def test_should_be_idempotent(self):
        numbers0 = [1, 2];
        numbers1 = self.ListOfNumbers(numbers0)
        numbers2 = self.ListOfNumbers(numbers1)
        self.assertEqual((1, 2), numbers1)
        self.assertEqual(numbers1, numbers2)

        path0 = [{'x': 0, 'y': 0}, {'x': 1, 'y': 1}]
    
        path1 = self.Path(path0)
        path2 = self.Path(path1)
        self.assertFalse(path0 == path1)
        self.assertTrue(path1 == path2)

    def test_should_be_idempotent_production(self):
    #    , util.production(function () {
    #      var numbers0 = [1, 2];
    #      var numbers1 = ListOfNumbers(numbers0);
    #      var numbers2 = ListOfNumbers(numbers1);
    #      assert.equal(numbers0 === numbers1, true);
    #      assert.equal(numbers1 === numbers2, true);

    #      var path0 = [{x: 0, y: 0}, {x: 1, y: 1}];
    #      var path1 = Path(path0);
    #      var path2 = Path(path1);
    #      assert.equal(path0 === path1, false);
    #      assert.equal(path1 === path2, true);
    #    }));
        self.fail(msg='TODO: Implement production mode!')

    def test_should_freeze_the_instance(self):
        instance = self.ListOfNumbers([1, 2])
        self.assertEqual(type(instance), tuple)

    def test_should_not_freeze_instance_in_production(self):
        self.fail(msg='TODO: Implement production mode!')
    # , util.production(function () {
    #      var instance = ListOfNumbers([1, 2]);
    #      assert.equal(Object.isFrozen(instance), false);
    #    }));
    #  });


    def test_list_type_should_return_true_when_x_is_list_of_type(self):
        self.assertTrue(self.PathOfPoint.is_type([]))
        self.assertTrue(self.PathOfPoint.is_type([self.p1, self.p2]))
        self.assertFalse(self.PathOfPoint.is_type(1))

    def test_list_predicate_used_as_predicate(self):
        self.assertTrue(self.PathOfPoint.is_type([self.p1, self.p2]))

    def test_should_return_new_instance(self):
          ListOfStrings = t.list(t.String)
          instance = ['a', 'b']
          newInstance = ListOfStrings.update(instance, {'$push': ['c']})
          self.assertFalse(newInstance == instance)
          self.assertEqual(newInstance, ['a', 'b', 'c'])
