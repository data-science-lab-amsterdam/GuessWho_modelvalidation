while true
do
	rsync -aE –delete -remove-source-files ~./Pictures/Photo\ Booth\ Library/Pictures/ ./data/images/faces/
	sleep 5s
done