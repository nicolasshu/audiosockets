port=jq ".PORT" server_info.json

echo ${port}
lsof -t -i:${port} | xargs kill -9
sleep 3
tmux new-session -d
tmux send 'python my_server.py' ENTER
sleep 1
tmux split-window -v
tmux send 'python recorder.py' ENTER
sleep 1
tmux attach-session