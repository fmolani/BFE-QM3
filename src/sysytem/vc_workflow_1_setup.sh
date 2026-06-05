#!/bin/bash


# Setup workflow step

# Name files for output of final commandline details and stdout/stderr

export CMDLOUT='vc_workflow_1_setup_cmnd.log'
STDOUTERR='vc_workflow_1_setup.log'

echo 'VM2 workflow setup step ...' > $CMDLOUT
echo >> $CMDLOUT

#--------------------------------------------------
# Set and output user changeable workflow variables 
#--------------------------------------------------

CTRLFILE=./set_vc_workflow_control_vars.sh

echo 'source' ${CTRLFILE} >> $CMDLOUT
echo >> $CMDLOUT

if [ ! -f "$CTRLFILE" ]; then
    echo "$CTRLFILE does not exist."
    exit
fi
source ${CTRLFILE}

#----------------------------
#  Assemble arguments 
#----------------------------


workflow="-workflow setup "

args=(${VCPYTHON} ${VCWORKFLOWEXE} ${EXPERIMENT} ${PREPMODE} \
      ${workflow} ${molsystem[@]} ${calcresources[@]} ${datadirs[@]} \
      ${proteinsetup[@]} ${hostsetup[@]} ${ligandsetup[@]} \
      ${calcenginectrl[@]} ${solvationmodel[@]} ${resultsextract[@]} \
      "> $STDOUTERR 2>&1")

#----------------------------
# Save commandline to file
#----------------------------

echo >> $CMDLOUT
echo 'Command Line for this run - prepend nohup on older systems :' >> $CMDLOUT
echo >> $CMDLOUT
echo "${args[@]}" >> $CMDLOUT

#----------------------------
#  Issue command 
#----------------------------

eval nohup "${args[@]}"


