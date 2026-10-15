import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--bench-rounds",
        action="store",
        default="10",
        help="Number of rounds per benchmark",
    )


@pytest.fixture
def bench_rounds(request):
    return int(request.config.getoption("--bench-rounds"))
