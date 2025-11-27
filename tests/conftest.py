import bpy
import pytest


@pytest.fixture(autouse=True)
def run_around_test():
    # run before each test
    bpy.ops.wm.read_homefile(app_template="")
    yield
    # run after each test
    pass
