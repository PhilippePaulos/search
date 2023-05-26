import importlib.resources


def get_resources_file(file_name: str) -> str:
    """
        Get the absolute path of a resource file.

        :param file_name: The name of the resource file.
        :type file_name: str
        :return: The absolute path of the resource file as a string.
        :rtype: str
        :raises FileNotFoundError: If the resource cannot be found.
        """
    with importlib.resources.path('resources', file_name) as path:
        return str(path)
