find /var/log * -mtime +7300 -print | while read filename; do
    # do whatever you want with the file
    echo $(date -r $filename) "$filename" 
    touch -r "$filename" -d "$(date -r "$filename") + 1 day" "$filename"
done
