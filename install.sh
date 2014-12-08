#!/bin/bash
#
# run this in top level install directory
#
test -d Personis || { echo 'Please run in top-level install directory'; exit 1; }

major=`python -c "import sys
print sys.version_info[0]"`
minor=`python -c "import sys
print sys.version_info[1]"`

if [ $major -lt 3 ]; then
    if [ $major -lt 2 ] || [ $minor -lt 7 ]; then
        echo "Python version too old."
        echo "Installed: $major.$minor"
        echo "Required: >= 2.7"
        exit
    fi  
fi

cd Personis
export PYTHONPATH=`pwd`/Src:`pwd`/lib/python:`pwd`/lib64/python

PLIB=`pwd`
echo installing Cherrypy
tar zxf CherryPy-3.2.2.tar.gz
cd CherryPy-3.2.2
python setup.py install --home=$PLIB

cd ..
echo installing simplejson
tar zxf simplejson-2.1.1.tar.gz
cd simplejson-2.1.1
python setup.py install --home=$PLIB

cd ..
echo installing pyCrypto
tar zxf pycrypto-2.6.tar.gz
cd pycrypto-2.6
python setup.py install --home=$PLIB

echo done.
echo
echo '==============================================================================='
echo "Don't forget to set your PYTHONPATH to:"
echo $PYTHONPATH
echo "before attempting to use Personis."
echo
echo "Please read the Introduction and Tutorial in Personis/Doc/Personis.pdf"
echo '==============================================================================='
