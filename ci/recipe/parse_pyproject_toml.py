import toml
import os


def parse_toml(file_path):
    with open(file_path, 'r') as f:
        return toml.load(f)


# This function will be called by conda-build to load the pyproject.toml data
def main():
    pyproject_toml_path = os.path.join(os.getcwd(), 'pyproject.toml')
    return parse_toml(pyproject_toml_path)
