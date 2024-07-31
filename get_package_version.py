import versioneer


def get_project_version():
    project_version = versioneer.get_version()
    return project_version


if __name__ == '__main__':
    print(get_project_version())
