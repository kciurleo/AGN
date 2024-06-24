#!/bin/sh

# This script runs an asynchronous post request based on a query txt file, input votable, and API endpoint. 
# Used for both XMM and eROSITA query

# Files
#query_file="/Users/kciurleo/Documents/kciurleo/AGN/queries/XMM_query.txt"
query_file="/Users/kciurleo/Documents/kciurleo/AGN/queries/eROSITA_query.txt"
#endpoint="https://nxsa.esac.esa.int/tap-server/tap/async"
endpoint="https://heasarc.gsfc.nasa.gov/xamin/vo/tap/async"
table="/Users/kciurleo/Documents/kciurleo/AGN/csvs/seyferts.vot"

# Read the query from query.txt, changing new lines and tabs to spaces
query=$(tr -s '[:space:]' ' ' < "$query_file")

# Execute the curl command
curl -i -X POST "$endpoint"\
    --form PHASE=run \
    --form UPLOAD="table_f,param:table2" \
    --form table2=@"$table" \
    --form LANG=ADQL \
    --form FORMAT=votable \
    --form REQUEST=doQuery \
    --form QUERY="\"$query\"" \

# After running this script, the request lists a location 
# (e.g. Location: http://nxsa.esac.esa.int/tap-server/tap/async/1718984677210O)
# Add /results/result to the end of the location to see whether the action is
# still executing, or to download the resulting vot table.

# Alternatively, curl -o output_table.vot "$location/results/result" 