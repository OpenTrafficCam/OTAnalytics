#!/bin/sh
## now loop through the above array
for inner_folder in "pos1/time1" "pos1/time2" "pos2/time1" "pos2/time2"
do
  folder="data/L1115-B328_Zeitlueckenerfassung K1,K4/${inner_folder}"

  for file in "${folder}"/*.ottrk; do
      echo "${file}"
      if [ -f "$file" ]; then
          filename=${file%.*}
          flow_file="${folder}"/flows.otflow
          echo "filename: $filename"
          echo "flowfile: $flow_file"
          python -m OTAnalytics --cli --otflow "${flow_file}" --ottrks "${file}" --save-name "${filename}" --event-format xlsx
      fi
  done

  python analysis.py "${folder}"
done
