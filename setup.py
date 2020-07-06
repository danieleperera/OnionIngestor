from setuptools import setup


def readme_file_contents():
    with open('README.md') as readme_file:
        data = readme_file.read()
    return data


setup(
    name='OnionIngestor',
    version='1.0.0',
    description='Python app to scraper and index hidden websites',
    long_description=readme_file_contents(),
    author='dan',
    author_email='test@google.com',
    license='MIT',
    packages=['onioningestor'],
    zip_safe=False,
    install_requires=[]
)

