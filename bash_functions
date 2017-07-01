


# https://superuser.com/questions/199088/highlight-console-search-output-while-displaying-entire-command-output
function highlight()
{
    sed "s/$1/`tput smso`&`tput rmso`/gi" "${2:--}"
}
