import argparse
import sys

from search.process.process import SearchProcess

# Define the parameters and their types
PARAMS = {
    "latitude": float,
    "longitude": float,
    "radius": int
}


def parse_params(args):
    """
    Parse the input arguments and convert them to the desired types.

    :param args: A list of input arguments.
    :type args: List[str]
    :return: An object containing the parsed arguments.
    :rtype: argparse.Namespace
    :raises ValueError: If any of the required input arguments are missing or cannot be converted to the desired type.
    """
    # Convert the arguments to the desired types
    converted_args = {}
    for arg in args:
        key, value = arg.split("=")
        if key in PARAMS:
            param_type = PARAMS[key]
            try:
                converted_args[key] = param_type(value)
            except ValueError:
                raise ValueError(f"Incorrect value for {key}. Expected {param_type.__name__}, "
                                 f"got {value}")
        else:
            raise ValueError(f"Invalid parameter: {key}")

    # Check if all required parameters are provided
    missing_params = set(PARAMS.keys()) - set(converted_args.keys())
    if missing_params:
        raise ValueError(f"Missing required parameter(s): {', '.join(missing_params)}")

    return argparse.Namespace(**converted_args)


def run():
    """
    Execute the search based on the provided command-line arguments.
    """
    # Parse the command-line arguments
    args = sys.argv[1:]
    parsed_args = parse_params(args)

    search_process = SearchProcess(parsed_args.latitude, parsed_args.longitude, parsed_args.radius)
    search_process.process()


if __name__ == "__main__":
    run()
