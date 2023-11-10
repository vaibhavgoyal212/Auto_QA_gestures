#!/bin/sh

for i in ~/ug4project-1/studyseqs_cond_new/*.bvh; do
    [ -f "$i" ] || break
    path_to_bvh=$i
    output_file="StudySeq${path_to_bvh#*/StudySeq}"
    output_file="${output_file%".bvh"}.mp4"
    output_path="${path_to_bvh%/StudySeq*.bvh}/${output_file}"
    if [ ! -f "$output_path" ];
    then
        python ~/ug4project-1/genea_visualizer/example.py --output=$output_path $path_to_bvh
    fi
done
