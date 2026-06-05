#!/bin/bash


# Run directory generation workflow step.

# Name files for output of final commandline details and stdout/stderr

export CMDLOUT='vc_workflow_3_genrundirs_cmnd.log'
STDOUTERR='vc_workflow_3_genrundirs.log'

echo 'VM2 run directory generation workflow step ...' > $CMDLOUT
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


workflow="-workflow run -prepMode "

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


