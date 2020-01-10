#!/bin/bash
#
########################################
# USER MODIFIABLE PARAMETERS:
 PART=broadwl
 TASKS=4       # 4 cores
 TIME="2:00:00" # 2 hours
########################################
#
# TRAP SIGINT AND SIGTERM OF THIS SCRIPT
function control_c {
    echo -en "\n SIGINT: TERMINATING SLURM JOBID $JOBID AND EXITING \n"
    scancel $JOBID
    rm jupyter-server.sbatch
    exit $?
}
trap control_c SIGINT
trap control_c SIGTERM
#
create_sbatch() {
cat << EOF
#!/bin/bash
#
#SBATCH --partition=$PART
#SBATCH --ntasks=$TASKS
#SBATCH --account=macs60000
#SBATCH --cpus-per-task=1
#SBATCH --time=$TIME
#SBATCH -J nb_server
#SBATCH -o ~/nb_session_%J.out

# LOAD A PYTHON MOUDLE WITH JUPYTER
module load Anaconda3/4.1.1
#
# TO EXECUTE A NOTEBOOK TO CONNECT TO FROM YOUR LOCAL MACHINE YOU  NEED TO
# GET THE IP ADDRESS OF THE REMOTE MACHINE
 export HOST_IP=\`hostname -i\`
#SET THE PORT NUMBER
let PORT_NUM=($UID-6025)%65274
launch='jupyter notebook --no-browser --ip=\${HOST_IP} --port \$PORT_NUM'
echo "  \$launch "
eval \$launch
EOF
}
#
# CREATE JUPYTER NOTEBOOK SERVER SBATCH FILE
create_sbatch > jupyter-server.sbatch
#
# START NOTEBOOK SERVER
#
sleep 1
export JOBID=$(sbatch jupyter-server.sbatch  | awk '{print $4}')
NODE=$(squeue -hj $JOBID -O nodelist )
if [[ -z "${NODE// }" ]]; then
   echo  " "
   echo -n "    WAITING FOR RESOURCES TO BECOME AVAILABLE (CTRL-C TO EXIT) ..."
fi
while [[ -z "${NODE// }" ]]; do
   echo -n "."
   sleep 3
   NODE=$(squeue -hj $JOBID -O nodelist )
done
  NB_ADDRESS=$(cat ~/nb_session_${JOBID}.out | grep "] http" | awk -F 'http' '{print $2}' )
  TIMELIM=$(squeue -hj $JOBID -O timeleft )
  if [[ $TIMELIM == *"-"* ]]; then
  DAYS=$(echo $TIMELIM | awk -F '-' '{print $1}')
  HOURS=$(echo $TIMELIM | awk -F '-' '{print $2}' | awk -F ':' '{print $1}')
  MINS=$(echo $TIMELIM | awk -F ':' '{print $2}')
  TIMELEFT="THIS SESSION WILL TIMEOUT IN $DAYS DAY $HOURS HOUR(S) AND $MINS MINS "
  else
  HOURS=$(echo $TIMELIM | awk -F ':' '{print $1}' )
  MINS=$(echo $TIMELIM | awk -F ':' '{print $2}')
  TIMELEFT="THIS SESSION WILL TIMEOUT IN $HOURS HOUR(S) AND $MINS MINS "
  fi
  echo " "
  echo "  --------------------------------------------------------------------"
  echo "    STARTING JUPYTER NOTEBOOK SERVER ON NODE $NODE           "
  echo "    $TIMELEFT"
  echo "    SESSION LOG WILL BE STORED IN ~/nb_session_${JOBID}.out  "
  echo "  --------------------------------------------------------------------"
  echo "  "
  echo "    TO ACCESS THIS NOTEBOOK SERVER, COPY AND PASTE "
  echo "    THE FOLLOWING FULL URL WITH TOKEN INTO YOUR BROWSER: "
  echo "  "
  echo "    http${NB_ADDRESS}  "
  echo "  "
  echo "    *NOTE* YOU MUST BE ON THE CAMPUS NETWORK TO ACCESS THIS NB SERVER "
  echo "    IF YOU ARE OFF CAMPUS YOU NEED TO CONNECT THROUGH THE UCHICAGO VPN   "
  echo "  --------------------------------------------------------------------"
  echo "    TO KILL THIS NOTEBOOK SERVER ISSUE THE FOLLOWING COMMAND: "
  echo "  "
  echo "       scancel $JOBID "
  echo "  "
  echo "  --------------------------------------------------------------------"
  echo "  "
#
# CLEANUP
  rm jupyter-server.sbatch
#
# EOF
