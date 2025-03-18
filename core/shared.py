"""Shared code"""

import os

from dotenv import load_dotenv


load_dotenv()


def getenv(env, default=""):
    """
    Retrieve the value of an environment variable, stripping any surrounding
    single or double quotes.

    Args:
        env (str): The name of the environment variable to retrieve.
        default (Any, optional): The default value to return if the environment
            variable is not set. Defaults to None.

    Returns:
        str: The value of the environment variable with surrounding quotes removed,
        or the default value if the environment variable is not set.
    """
    return os.getenv(env, default).strip("'").strip('"')
