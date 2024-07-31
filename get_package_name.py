import toml


def toml_package_name():
    pyproject_data = toml.load('pyproject.toml')
    pkg_name = pyproject_data.get('project', {}).get('name')
    return pkg_name


if __name__ == '__main__':
    print(toml_package_name())
