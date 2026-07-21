#!/usr/bin/env python

import unittest

from tests import rust_backend_test


def suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromModule(rust_backend_test)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=3).run(suite())
    if not result.wasSuccessful():
        raise SystemExit(2)
