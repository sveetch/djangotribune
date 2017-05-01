from setuptools import setup, find_packages

setup(
    name='djangotribune',
    version=__import__('djangotribune').__version__,
    description=__import__('djangotribune').__doc__,
    long_description=open('README.rst').read(),
    author='David Thenon',
    author_email='sveetch@gmail.com',
    url='http://pypi.python.org/pypi/djangotribune',
    license='MIT',
    packages=find_packages(exclude=['project_test*']),
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Communications :: Chat',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'Django',
        'texttable',
        #'crispy-forms-foundation>=0.2.3.1',
        'pytz',
    ],
    include_package_data=True,
    zip_safe=False
)