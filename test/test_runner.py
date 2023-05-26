import pytest
from runner import parse_params


@pytest.mark.parametrize(
    "args, exception_expected",
    [
        # Correct values, no exception expected
        (["latitude=48.0", "longitude=2.0", "radius=100"], False),
        # Incorrect latitude, exception expected
        (["latitude=string", "longitude=2.0", "radius=100"], True),
        # Incorrect longitude, exception expected
        (["latitude=48.0", "longitude=string", "radius=100"], True),
        # Incorrect radius, exception expected
        (["latitude=48.0", "longitude=2.0", "radius=string"], True),
        # Latitude not set, exception expected
        (["longitude=2.0", "radius=100"], True),
        # Longitude not set, exception expected
        (["latitude=48.0", "radius=100"], True),
        # Radius not set, exception expected
        (["latitude=48.0", "longitude=2.0"], True),
        # All parameters not set, exception expected
        ([], True),
        # Invalid parameter, exception expected
        (["latitude=48.0", "longitude=2.0", "radius=100", "invalid=abc"], True),
    ],
)
def test_parse_params(args, exception_expected):
    if exception_expected:
        with pytest.raises(ValueError):
            parse_params(args)
    else:
        parsed_args = parse_params(args)
        assert parsed_args.latitude == 48.0
        assert parsed_args.longitude == 2.0
        assert parsed_args.radius == 100
