from setuptools import setup, find_packages

setup(
    name='q2-vizard',
    version='0.0.1.dev0',
    packages=find_packages(),
    package_data={
        'q2_vizard': ['assets/*'],
    },
    author='q2d2',
    author_email='q2d2@qiime2.org',
    description='The first choice of wizard lizards for protection and'
                ' entertainment',
    license='BSD-3-Clause',
    url='https://github.com/qiime2/q2-vizard',
    zip_safe=False,
    entry_points={
        'qiime2.plugins': ['q2-vizard=q2_vizard.plugin_setup:plugin']
    }
)