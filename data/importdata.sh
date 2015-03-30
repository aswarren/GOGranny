#!/bin/bash

# This is the location of the root directory containing the DB DATA 
# probably shouldn't ever change.  There should be no "/" at the end
DB_LOCATION=http://archive.geneontology.org/latest-full

############# END CONFIG ###############
if [ "$2" = "" ]
then
    echo "Usage: $0 <mysql database name> <mysql username> [<mysql password]"
    exit 1
fi

errortest ()
{
    if [ "$?" != "0" ]
    then
	echo "Error: $1"
	exit 1
    fi
}

echo "Fetching the names of the most recent files..."
DATE=$(wget -O - $DB_LOCATION | grep '[0-9]-assocdb-data\.gz' | awk '{ print substr($0, index($0, /go_[0-9]-assocdb-data\.gz/)-1, 6); }')
errortest "Could not get the names of the most recent files..."

# term db and assoc db data - these should not end with the .gz
TERM_DB_DATA="go_$DATE-termdb-data"
ASSOC_DB_DATA="go_$DATE-assocdb-data"

echo "Most recent term database file is $TERM_DB_DATA"
echo "Most recent association database file is $ASSOC_DB_DATA"

echo "Checking for $TERM_DB_DATA ..."
test -e $TERM_DB_DATA || wget "$DB_LOCATION/$TERM_DB_DATA.gz"
errortest "Could not download $DB_LOCATION/$TERM_DB_DATA.gz"
echo "Checking for $ASSOC_DB_DATA ..."
test -e $ASSOC_DB_DATA || wget "$DB_LOCATION/$ASSOC_DB_DATA.gz"
errortest "Could not download $DB_LOCATION/$ASSOC_DB_DATA.gz"

echo "Gunzipping if necessary..."
if [ -e "$TERM_DB_DATA.gz" ]
then
    gunzip "$TERM_DB_DATA.gz"
    errortest "Could not gunzip $TERM_DB_DATA"
fi
if [ -e "$ASSOC_DB_DATA.gz" ]
then
    gunzip "$ASSOC_DB_DATA.gz"
    errortest "Could not gunzip $ASSOC_DB_DATA"
fi

# if no password given
if [ "$3" = "" ]
then
    echo "No password specified, attempting to import data..."
    echo "Importing term data..."
    mysql -u $2 $1 < $TERM_DB_DATA
    errortest "Could not import data from $TERM_DB_DATA into mysql"
    echo "Importing assoc data..."
    mysql -u $2 $1 < $ASSOC_DB_DATA
    errortest "Could not import data from $ASSOC_DB_DATA into mysql"
else
    echo "Importing term data..."
    mysql -u $2 $1 --password=$3 < $TERM_DB_DATA
    errortest "Could not import data from $TERM_DB_DATA into mysql"
    echo "Importing assoc data..."
    mysql -u $2 $1 --password=$3 < $ASSOC_DB_DATA
    errortest "Could not import data from $ASSOC_DB_DATA into mysql"
fi