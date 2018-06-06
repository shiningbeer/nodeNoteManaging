screennode=$'node'
screen -S $screennode -X quit
screen -dmS $screennode
sleep 2s
cmd=$"node ./src/nServer.js"
screen -S $screennode -X stuff "$cmd"
screen -S $screennode -X stuff $'\n' 

screennode=$'zmap'
screen -S $screennode -X quit
screen -dmS $screennode
sleep 2s
cmd=$"python ./src/zmapFilter.py"
screen -S $screennode -X stuff "$cmd"
screen -S $screennode -X stuff $'\n' 

screennode=$'worker'
screen -S $screennode -X quit
screen -dmS $screennode
sleep 2s
cmd=$"python ./src/worker.py"
screen -S $screennode -X stuff "$cmd"
screen -S $screennode -X stuff $'\n' 
