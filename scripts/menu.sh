options=("Link Status" "Exit")
if [ -f /scripts/functions ]; then
	source /scripts/functions
elif [ -f ./functions ]; then
	source ./functions
fi
if [ -f /scripts/curses_menu.py ];then
	python /scripts/curses_menu.py
elif [ -f ./curses_menu.py ]; then
	python curses_menu.py
fi
#while true; do
#	clear
#	linkethtool
#	sleep 1
#done

#select opt in "${options[@]}"
#do
#        case $opt in
#                "Link Status")
#                       linkethtool 
#                        ;;
#                "Exit")
#                        break 2
#                        ;;
#        esac
#done

