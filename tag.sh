#!/bin/bash
echo current version:$(python -c "import hiro.version;print(hiro.version.__version__)")
read -p "new version:" new_version
sed -i -e "s/__version__.*/__version__ = \"${new_version}\" # pragma: no cover/g" hiro/version.py
echo "tagging $new_version"
git add hiro/version.py
git commit -m "updating version to ${new_version}"
git tag -s $(python setup.py --version) -m "tagging version ${new_version}"
rm -rf build/
python setup.py build sdist bdist_egg
twine upload dist/*


