import sys
import time
import warnings

from popgen import Project

warnings.filterwarnings("ignore")

class ArgumentsError(Exception):
    pass


def run():
    """
    Runs the PopGen program to generate a synthetic population.
    Please refer to PopGen documentation on the GitHub site
    for guidance on setting up the configuration file.
    """
    args = sys.argv[1:]

    if len(args) != 1:
        raise ArgumentsError(
            """The module accepts only one argument which is the location of
            the configuration file.

            Example usage on linux or Mac:
                popgen_run /location/of/file.yaml

            Example usage on Windows:
                popgen_run c:/location/of/file.yaml""")

    t = time.time()
    p_obj = Project(config_loc=args[0])
    p_obj.load_project()
    p_obj.run_scenarios()
    print("Time it took: %.4f" % (time.time() - t))


if __name__ == "__main__":
    run()
