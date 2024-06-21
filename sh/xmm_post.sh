#!/bin/sh

# This script runs an asynchronous post request to ESAC based on a query txt file and input votable

#Files
query_file="/Users/kciurleo/Documents/kciurleo/AGN/queries/XMM_query.txt"
table="/Users/kciurleo/Documents/kciurleo/test_votable.vot"

# Read the query from query.txt, changing new lines and tabs to spaces
query=$(cat "$query_file" | tr '\n\t' ' ')

# Execute the curl command
curl -i -X POST \
    --form PHASE=run \
    --form UPLOAD="table_f,param:table2" \
    --form table2=@"$table" \
    --form LANG=ADQL \
    --form FORMAT=votable \
    --form REQUEST=doQuery \
    --form QUERY="$query" \
    "https://nxsa.esac.esa.int/tap-server/tap/async"