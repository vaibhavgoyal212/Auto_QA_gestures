for file in ./AppropriatenessStudyVideos/Cond_BA/*.mp4; do
    ffmpeg -i "$file" -ab 160k -ac 2 -ar 44100 -vn "${file%.*}.wav"
done