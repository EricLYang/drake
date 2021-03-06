#!/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import print_function

import copy
import unittest
import numpy as np

from pydrake.systems.framework import (
    AbstractValue,
    BasicVector,
    Value,
    )
from pydrake.systems.test.test_util import (
    make_unknown_abstract_value,
    MoveOnlyType,
)


def pass_through(x):
    return x


# TODO(eric.cousineau): Add negative (or positive) test cases for AutoDiffXd
# and Symbolic once they are in the bindings.


class TestValue(unittest.TestCase):
    def test_basic_vector_double(self):
        # Test constructing vectors of sizes [0, 1, 2], and ensure that we can
        # construct from both lists and `np.array` objects with no ambiguity.
        for n in [0, 1, 2]:
            for wrap in [pass_through, np.array]:
                # Ensure that we can get vectors templated on double by
                # reference.
                expected_init = wrap(map(float, range(n)))
                expected_add = wrap([x + 1 for x in expected_init])
                expected_set = wrap([x + 10 for x in expected_init])

                value_data = BasicVector(expected_init)
                value = value_data.get_mutable_value()
                self.assertTrue(np.allclose(value, expected_init))

                # Add value directly.
                # TODO(eric.cousineau): Determine if there is a way to extract
                # the pointer referred to by the buffer (e.g. `value.data`).
                value[:] += 1
                self.assertTrue(np.allclose(value, expected_add))
                self.assertTrue(
                    np.allclose(value_data.get_value(), expected_add))
                self.assertTrue(
                    np.allclose(value_data.get_mutable_value(), expected_add))

                # Set value from `BasicVector`.
                value_data.SetFromVector(expected_set)
                self.assertTrue(np.allclose(value, expected_set))
                self.assertTrue(
                    np.allclose(value_data.get_value(), expected_set))
                self.assertTrue(
                    np.allclose(value_data.get_mutable_value(), expected_set))
                # Ensure we can construct from size.
                value_data = BasicVector(n)
                self.assertEquals(value_data.size(), n)

    def test_abstract_value_copyable(self):
        expected = "Hello world"
        value = Value[str](expected)
        self.assertTrue(isinstance(value, AbstractValue))
        self.assertEquals(value.get_value(), expected)
        expected_new = "New value"
        value.set_value(expected_new)
        self.assertEquals(value.get_value(), expected_new)
        # Test docstring.
        self.assertFalse("unique_ptr" in value.set_value.__doc__)

    def test_abstract_value_move_only(self):
        obj = MoveOnlyType(10)
        # This *always* clones `obj`.
        value = Value[MoveOnlyType](obj)
        self.assertTrue(value.get_value() is not obj)
        self.assertEquals(value.get_value().x(), 10)
        # Set value.
        value.get_mutable_value().set_x(20)
        self.assertEquals(value.get_value().x(), 20)
        # Test custom emplace constructor.
        emplace_value = Value[MoveOnlyType](30)
        self.assertEquals(emplace_value.get_value().x(), 30)
        # Test docstring.
        self.assertTrue("unique_ptr" in value.set_value.__doc__)

    def test_abstract_value_py_object(self):
        expected = {"x": 10}
        value = Value[object](expected)
        # Value is by reference, *not* by copy.
        self.assertTrue(value.get_value() is expected)
        # Update mutable version.
        value.get_mutable_value()["y"] = 30
        self.assertEquals(value.get_value(), expected)
        # Cloning the value should perform a deep copy of the Python object.
        value_clone = copy.deepcopy(value)
        self.assertEquals(value_clone.get_value(), expected)
        self.assertTrue(value_clone.get_value() is not expected)
        # Using `set_value` on the original value changes object reference.
        expected_new = {"a": 20}
        value.set_value(expected_new)
        self.assertEquals(value.get_value(), expected_new)
        self.assertTrue(value.get_value() is not expected)

    def test_abstract_value_make(self):
        value = AbstractValue.Make("Hello world")
        self.assertTrue(isinstance(value, Value[str]))
        value = AbstractValue.Make(MoveOnlyType(10))
        self.assertTrue(isinstance(value, Value[MoveOnlyType]))
        value = AbstractValue.Make({"x": 10})
        self.assertTrue(isinstance(value, Value[object]))

    def test_abstract_value_unknown(self):
        value = make_unknown_abstract_value()
        self.assertTrue(isinstance(value, AbstractValue))
        with self.assertRaises(RuntimeError) as cm:
            value.get_value()
        self.assertTrue(all(
            s in cm.exception.message for s in [
                "AbstractValue",
                "UnknownType",
                "get_value",
                "AddValueInstantiation",
            ]), cm.exception.message)


if __name__ == '__main__':
    unittest.main()
