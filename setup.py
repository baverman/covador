from setuptools import setup
import covador

setup(
    name='covador',
    version=covador.version,
    url='https://github.com/baverman/covador/',
    license='MIT',
    author='Anton Bobrov',
    author_email='baverman@gmail.com',
    description='Python data validation with web in-mind',
    long_description=open('README.rst', 'rb').read().decode('utf-8'),
    packages=['covador'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',
    ]
)
