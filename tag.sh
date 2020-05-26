#!/bin/bash
dryrun=0
while [ "$1" != "" ]; do
    case $1 in
        -d | --dryrun )    dryrun=1
                           ;;
    esac
    shift
done
rm -rf build dist
last_tag=$(git tag | sort -nr | head -n 1)
echo current version:$(python setup.py --version), current tag: $last_tag
read -p "new version:" new_version
echo "tagging $new_version"
git tag -s ${new_version} -m "tagging version ${new_version}"
python setup.py build sdist bdist_egg bdist_wheel
test $dryrun != 1 && twine upload dist/*
