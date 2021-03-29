mailman_port=jq ".MAILMAN" server_info.json
processor_port=jq ".PROCESSOR" server_info.json

echo ${mailman_port}
echo ${processor_port}
lsof -t -i:${mailman_port} | xargs kill -9
lsof -t -i:${processor_port} | xargs kill -9
sleep 3
tmux new-session -d
tmux send 'python processor.py' ENTER
sleep 3
tmux split-window -v
tmux send 'python mailman.py' ENTER
sleep 1
tmux split-window -v
tmux send 'python recorder.py' ENTER
sleep 1
tmux attach-session