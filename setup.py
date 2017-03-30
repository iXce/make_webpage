import os
from setuptools import setup

def fileslist(root, base):
    out = []
    for curdir, dirnames, filenames in os.walk(os.path.join(root, base)):
        for fname in filenames:
            if not fname.startswith("."):
                fpath = os.path.join(curdir.replace(root, "", 1), fname)
                if fpath.startswith(os.sep):
                    fpath = fpath.replace(os.sep, "", 1)
                out.append(fpath)
    return out

setup(
    name='webpagemaker',
    version='0.1',
    description='Easily produce webpage showing tables of images, plots and other fancy science thingies.',
    long_description=open("README.md").read(),
    url='https://github.com/iXce/make_webpage',
    author='Guillaume Seguin',
    author_email='guillaume@segu.im',
    license='MIT',
    packages=['webpagemaker'],
    package_data={'webpagemaker': (fileslist('webpagemaker', 'templates') +
                                   fileslist('webpagemaker', 'static'))},
    scripts=['clitohtml.py', 'jsontohtml.py'],
    install_requires=[
        'jinja2',
        'Pillow'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: English',
    ],
)
