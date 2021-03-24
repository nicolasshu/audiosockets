here="/home/nickshu/Documents/experiments/voice_activity/saved_models"
docker run -p 8501:8501 --name tfresnet --mount type=bind,source=$here/super-bird-20,target=/models/super-bird-20 -e MODEL_NAME=super-bird-20 -t tensorflow/serving &
