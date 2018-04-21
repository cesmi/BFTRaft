for log in server*_log.txt; do
  diff server0_log.txt $log
done
