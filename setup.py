from setuptools import setup, find_packages
import glob
import os

if os.path.exists('VERSION'):
    version = open("VERSION").readline().strip()
else:
    for line in open('PKG-INFO'):
        if 'Version' in line:
            version=(line.split()[1]).strip()
install_requires=[]

for line in open('requirements.txt'):
    install_requires.append(line.strip())

setup(name='image-check',
      version=version,
      description='',
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers  # nopep8
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='ddc',
      author_email='ufwt@hotmail.com',
      url='xxx',
      license='GPL',
      packages=find_packages(exclude=["ez_setup","test.*", "test"]),
      namespace_packages=[],
      include_package_data=True,
      test_suite='nose.collector',
      zip_safe=False,
      install_requires=install_requires,
       #scripts=['bin/parse_mq','bin/parse_file'],
      data_files=[("bin",glob.glob("bin/*")),
                ("logs",[]),
                ("etc",glob.glob("etc/*.*"))                         
                ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
