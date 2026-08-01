#!/usr/bin/env python

import importlib.util
import os
import unittest


def _load_test_module(name):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(os.path.dirname(__file__), f"{name}.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rust_backend_test = _load_test_module("rust_backend_test")


def suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromModule(rust_backend_test)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=3).run(suite())
    if not result.wasSuccessful():
        raise SystemExit(2)
