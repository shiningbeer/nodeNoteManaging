cd src
screennode=$'node'
screen -S $screennode -X quit
screen -dmS $screennode
sleep 2s
cmd=$"node nserver.js"
screen -S $screennode -X stuff "$cmd"
screen -S $screennode -X stuff $'\n' 

screennode=$'task'
screen -S $screennode -X quit
screen -dmS $screennode
sleep 2s
cmd=$"sudo python ./tasks/runTask.py"
screen -S $screennode -X stuff "$cmd"
screen -S $screennode -X stuff $'\n' 