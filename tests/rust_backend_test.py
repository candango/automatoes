import threading
import time
import unittest

import rust_backend


class RustBackendTestCase(unittest.TestCase):
    def test_sleep_detached_releases_gil(self):
        reached_python = threading.Event()
        ready = threading.Barrier(2)

        def python_worker():
            ready.wait()
            time.sleep(0.05)
            reached_python.set()

        worker = threading.Thread(target=python_worker)
        worker.start()
        ready.wait()
        rust_backend.sleep_detached(300)
        worker.join()

        self.assertTrue(reached_python.is_set())

    def test_exported_functions(self):
        self.assertEqual(42, rust_backend.add(20, 22))
        self.assertEqual(
            "Hello, Automatoes! Rust is handling this function.",
            rust_backend.hello("Automatoes"),
        )
