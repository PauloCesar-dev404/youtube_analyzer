from youtube_analyzer.__version__ import __version__, __autor__, __repo__, __source__, __lib__
from setuptools import setup, find_packages

# Lê o conteúdo do README.md
with open('README_PYPI.md', 'r', encoding='utf-8') as file:
    long_description = file.read()

setup(
    name="youtube-analyzer",
    version=__version__,
    description="Analize vídeos do youtube",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=__autor__,
    author_email="paulocesar0073dev404@gmail.com",
    license="MIT",
    keywords=["youtube"],
    install_requires=[
        'requests',
        'colorama',
        'beautifulsoup4',
        'emoji'
    ],
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms=["any"],
    project_urls={
        "Código Fonte": __source__,
        "lib": __lib__,
        'GitHub': __repo__,
        "Bugs/Melhorias": f"{__repo__}/issues",
        "Documentação": f"{__repo__}/wiki",
    },

)
