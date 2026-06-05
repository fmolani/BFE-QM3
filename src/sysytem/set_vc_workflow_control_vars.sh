#!/bin/bash

# Timestamp: Fri May  6 12:23:47 PDT 2022

# This is an auto-generated template shell script that sets VeraChem
# VM2 workflow control environment variables.

# Edit as needed for your specific system and desired workflow.


#-------------------------------
# VM2 package install location
#-------------------------------

# You can set the VM2 package install location directly in this file if you wish ...

# export VCHOME=

#-------------------------------
# Choose molecular system
#-------------------------------

# MOLSYSTEMTYPE     : Available options are protein+ligand, host+ligand, ligand 

export MOLSYSTEMTYPE='protein+ligand'


#-------------------------------
# Calculation type 
#-------------------------------

# CALCNTYPE : Available options are vm2, feprocess, and confsearch.
#
#            'vm2'        : 2nd generation mining minima free energy calculation, which carries out an
#                           exhaustive conformational search, calculates configuration integrals for
#                           individual conformers, and carries out a Boltzmann weighting to give
#                           a total free energy.
#            'feprocess'  : Process a set of already generated molecular conformers for total free energy. 
#            'confsearch' : Carry out a conformational search providing potential energies of the resulting
#                           conformers.
#
#            (See 'Calculation engine control' section below for options related to these calculation types.) 

export CALCNTYPE='vm2'

#-------------------------------------
# Workflow exe, data, and project dirs 
#-------------------------------------

# VCWORKFLOWEXE   : Full path and name of python workflow exe.
# VCRAWDATADIR    : Full path of directory containing raw data such as: protein PDB file, ligand mol files, ...
#                   e.g. /home/myname/myrawdatadirs/rawdata_hivp_umass5_ad81template
#                   Protein-ligand subdirectories (required): /ligands /protein
#                                                 (optional): /experiment /template_ligand
#                   Host-ligand subdirectories    (required): /ligands /hosts
#                                                 (optional): /experiment
# VCPROJECTDIR    : Project directory to be used/created e.g. $PWD/hivp_umass5_vm2_coxtal

export VCWORKFLOWEXE=$VCHOME/exe/VM2.pyc

export VCRAWDATADIR=$PWD/../rawdata

export VCPROJECTDIR=$PWD/system_vm2

#-------------------------------
# Calculation resources
#-------------------------------

# VCCUSTOMEXE         : VeraChem calculation engine exe custom location: full path
#                       to directory. 

# QUEUETYPE           : Set queue type or just shell script type used to run calculations.
#                       If bsh script is selected calculations will run one after the
#                       other on the local machine. For slurm and pbs jobs will submitted
#                       to the queue system, except for short setup calculations.
# QUEUENAME           : Set the queue/partition name to use for pbs or slurm jobs. The default
#                       setting is 'default' i.e. your resource manager's default queue.
#                       Check your system resource manager for other available queue names.

# NUMNODES            : Number of compute nodes to use for receptor (protein or host)
#                       involved calculations.
# NUMMPIPROCS         : Total number of MPI processes to use for receptor involved calculations. 
# NUMOPENMPTHREADS    : Number of OpenMP threads to use per MPI process. If set to 0 a pure
#                       MPI run is performed.
# NUMGPUS             : Total number of GPUs to use for receptor runs.

# NUMLIGNODES         : Number of compute nodes to use for ligand calculations. 
# NUMLIGMPIPROCS      : Total number of MPI processes to use for ligand calculations. 
# NUMLIGOPENMPTHREADS : Number of OpenMP threads to use per MPI process. If set to 0 a pure
#                       MPI run is performed.
# NUMLIGGPUS          : Total number of GPUs to use for receptor runs. GPU use fo ligand
#                       calculations not recommended.

export VCCUSTOMEXE='none'

export QUEUETYPE='bsh'
export QUEUENAME='default'

export NUMNODES='1'
export NUMMPIPROCS='16'
export NUMOPENMPTHREADS='0'
export NUMGPUS='0'

export NUMLIGNODES='1'
export NUMLIGMPIPROCS='16'
export NUMLIGOPENMPTHREADS='0'
export NUMLIGGPUS='0'


#-------------------------------
# Set -prepMode (uncommon). 
#-------------------------------

# PREPMODE     : If -prepMode is set by uncommenting below, the run script for
#                the requested QUEUETYPE is placed in each run directory,
#                but the calculations are not submitted. Will rarely need to
#                be set from this script as the workflow step scripts take
#                care of this for the most common usages.

export PREPMODE=''
#export PREPMODE='-prepMode'


#-------------------------------
# Protein setup 
#-------------------------------

# PROTEINFILENAME   : Protein PDB (or .prmtop) file name in VCRAWDATADIR/protein
# PROTEINREFLIGAND  : Ligand chosen from VCRAWDATADIR/ligand that can be superimposed
#                     on the template ligand (if suitable e.g. related  co-xtal) in
#                     VCRAWDATADIR/template_ligand. It will be included for protein
#                     geometry relaxations during setup. Must be given if PREGENLIGCONFS is
#                     'snap', which it should be for coxtal or scaffold matching runs.
# PROTEINFORCEFIELD : Currently only the default forcefield 'amber' is available.
# PROTEINPREP       : Control preparation of protein. Currently only options are the
#                     default 'ambertools' and 'none'.
# PROTEINTYPER      : Control typing of the protein. Currently only options are the
#                     default 'ambertools' and 'none'.
#
# (Note: Currently if not using ambertools both PROTEINPREP and PROTEINTYPER must be 'none',
#  and pregenerated parameter files must be supplied e.g. .prmtop, .inpcrd, .mol2, and .pdb
#  for amber forcefield. Also .prmtop file name must be given below through PROTEINFILENAME.)
#
# LIVEREALREFCHOICE : Choice of source of reference for distance based definition of protein
#                     real/live atom set. Choices are 'proteinreflig', 'file', 'dir', and
#                     'template'.  
# LIVEREALREFFILE   : If 'file' selected in the preceeding, the name of the file in the
#                     raw data directory /live_real_ref to be set as the reference.
# REALATOMCUTOFF    : Cutoff distance from supplied template ligand atoms to determine protein
#                     atoms present in the calculation - residues will be completed. 
# LIVEATOMCUTOFF    : Cutoff distance from supplied template ligand atoms to determine protein
#                     atoms that will be present and mobile in the calculation.
# COMPLETELIVERES   : If 'on' mobile residue completion will be carried out. No completion if 'off'.
# MINLIVEFORCMPLT   : The minimum number of mobile (live) atoms in a residue required to trigger
#                     residue completion, otherwise all atoms in the reside are made real and fixed.
#                     Has no effect if COMPLETELIVERES is 'off'.
# PROTEINOPTH       : If 'on' initial optimization of only protein hydrogen atoms is carried out.
#                     No relaxation if 'off'. 
# PROTEINOPTHCUTOFF : Controls the cutoff distance for which hydrogen atoms are mobile. 
#                     A recommended size is at least REALATOMCUTOFF + 2.0 
# PROTEINRELAX      : If 'on' relaxation of protein atoms is carried out. No relaxation if 'off'. 
# PROTEINRELAXCUTOFF: Controls the cutoff distance for which atoms are mobile during the relaxation. 
#                     A recommended size is the value of LIVEATOMCUTOFF + 2.0 

export PROTEINFILENAME='protein.pdb'

export PROTEINREFLIGAND='lig_15'
export PROTEINFORCEFIELD='amber'
export PROTEINPREP='ambertools'
export PROTEINTYPER='ambertools'
export LIVEREALREFCHOICE='proteinreflig'
export LIVEREALREFFILE='none'
export REALATOMCUTOFF=6.0
export LIVEATOMCUTOFF=4.0
export COMPLETELIVERES='off'
export MINLIVEFORCMPLT=5
export PROTEINOPTH='on'
export PROTEINOPTHCUTOFF=12.0
export PROTEINRELAX='on'
export PROTEINRELAXCUTOFF=6.0


#-------------------------------
# Ligand setup 
#-------------------------------

# LIGANDFORCEFIELD : Currently only the default forcefield 'gaff' is available.
# LIGANDPREP       : Control preparation of ligands. Currently only options are the
#                    default 'ambertools' and 'none'.
# LIGANDTYPER      : Control typing of the ligands. Currently only options are the
#                    default 'ambertools' and 'none'.
#
# (Note: Currently if not using ambertools both LIGANDPREP and LIGANDTYPER must be 'none',
#  and pregenerated parameter files must be supplied e.g. .prmtop, .inpcrd, .mol2 and
#  .mol for amber forcefield.)
#
# LIGAND2D3D       : Method to do ligand 2D to 3D conversion. Choices are 'vconf'
#                    or if your ligand is already 3D 'none'
# LIGANDCHARGER    : Method to assign ligand partial atomic charges. Choices are
#                    'vcharge' (recommended) or 'am1bcc' via AmberTools.
# MAPLIGTOTEMPLATE : Method to map input ligand atoms to equivalent atoms in the
#                    supplied template. Usage is to map common scaffolds etc.
#                    Only current option is 'vmap' and is required for co-xtal
#                    runs. 
# LIGSDFFROMINPCRD : Turns on overwriting of SDF coordinates using .inpcrd coordinates.
#                    Only use for direct from .prmtop, .inpcrd, etc. gaff runs or if
#                    .inpcrd file with coordinates you want to use is available.
#                    For direct from .prmtop run, only use if SDF coordinates are different
#                    from .inpcrd and also using vconf and/or vmap options for starting
#                    coordinate manipulation.
# PREGENLIGCONFS   : Method to pre-generate ligand conformations to be placed in
#                    binding site and seed a free energy calculation. Options
#                    are 'snap', which forces superposition of atoms common with
#                    the template, and 'random' for random orientated conformers.
#                    The 'snap' option is required for coxtal/scaffold mapping runs.
# USETEMPLATESDF   : If USETEMPLATESDF='-useTemplateSdf' and if PROTEINREFLIGAND 
#                    has been set, use the template 'snapped' coordinates SDF for
#                    all other mapping. For this option to be off PROTEINREFLIGAND=''.

export LIGANDFORCEFIELD='gaff'
export LIGANDPREP='ambertools'
export LIGANDTYPER='ambertools'
export LIGAND2D3D='vconf'
export LIGANDCHARGER='vcharge'
export MAPLIGTOTEMPLATE='vmap'
export PREGENLIGCONFS='snap'
export LIGSDFFROMINPCRD=''
export USETEMPLATESDF='-useTemplateSdf'


#-------------------------------
# Calculation engine control 
#-------------------------------

# MPISEARCHSTYLE      : Controls how the MPI-distributed conformational search behaves.
#                       If 'uncoupled' all MPI processes carry out independent searches
#                       and only communicate their lowest energy conformers at the end
#                       of a search; if 'coupled', each MPI process communicates its
#                       lowest energy conformer and the lowest energy coordinates are
#                       then used by all processes as a new search basis; if 'mixed'
#                       then uncoupled searches are performed on even VM2 iterations,
#                       and coupled searches on odd ones.
# MPIMAXUCPLDITERS    : Maximum number of iterations with 'uncoupled' or 'mixed' set.
#                       After it is reached the search style is reset to 'coupled'.
#                       For MPISEARCHSTYLE 'uncoupled' a value of '10' is recommended
#                       otherwise '20' is recomoneded for 'mixed'
# CONFSEARCHSTYLE     : Controls the receptor-involved conformational search style.
#                       Available are 'enhanced' for single and random-pair mode searching;
#                       'rigorous' adds ligand nad protein focused mode searchin to this;
#                       'vrigorous' further adds ligand rotation/translation searching. 
#                       The default is 'rigorous'.
# MAXCONFSEARCHES     : Maximum of searches to carry out per search type (e.g. single mode,
#                       pair-mode) per VM2 iteration. The default is 100.
# LIGCONFSEARCHSTYLE  : Controls the ligand-only conformational search style. Available
#                       are 'minimal' for single mode searches only, 'enhanced' adds
#                       random-pair mode searching; 'rigorous' adds focused mode
#                       searching. The default is 'enhanced'. 
# MAXLIGCONFSEARCHES  : Maximum of searches to carry out per search type (e.g. single mode,
#                       pair-mode) per VM2 iteration. The default is 100.

export MPISEARCHSTYLE='uncoupled'
export MPIMAXUCPLDITERS=10
export CONFSEARCHSTYLE='rigorous'
export MAXCONFSEARCHES=100
export LIGCONFSEARCHSTYLE='enhanced'
export MAXLIGCONFSEARCHES=100


#-------------------------------
# Calculation engine solvation 
#-------------------------------

# DIELECINTERNAL   : Set the internal dielectric used for the GB and PB continuum
#                    solvation models. 
# DIELECEXTERNAL   : Set the external dielectric used for the GB and PB continuum
#                    solvation models. 

export DIELECINTERNAL=1.0
export DIELECEXTERNAL=80.0


#-------------------------------
# Compare with experiment? 
#-------------------------------

# HAVEEXPT  : Requests that experimental data given in VCRAWDATADIR/experiment
#             be included in results tables for comparison.
# EXPREFLIG : Identifies ligand from supplied ligand series in VCRAWDATADIR/ligands
# (Defunct)   whose calculated energy will be adjusted to the experimental value
#             to provide an offset to generate relative affinities i.e. DeltaDeltaG's.
#             (This variable no longer has an effect. Offset energies are now
#              calculated based on the average error w.r.t. experimental binding
#              affiities.) 

export HAVEEXPT='-experiment'
export EXPERIMENT='-experiment'


#-------------------------------
# Control extraction of results
#-------------------------------

# EXTRACTFOR       : Controls whether to extract energy data and conformer structure
#                    formatted files for human manipulation i.e. manual loading of
#                    .csv's into Excel, sdf's, mol2's, pdb's into molecular viewers;
#                    or for parsing and 'automated' manipulation/analysis by, for
#                    example, MOE. Current choices are 'humans', 'perconfpp', or 'moe'.
# MAXCONFSTOEX     : Maximum conformers to extract from the run directories into the
#                    result directory formatted files.
# POSTPROCCONFLMIT : Maximum number of conformers to include in any post-processing.

export EXTRACTFOR='perconfpp'
export MAXCONFSTOEX=8
export POSTPROCCONFLMIT=2


#-----------------------------------
# Gather/organize workflow variables
#-----------------------------------

export molsystem=("-molSystemType" ${MOLSYSTEMTYPE})

export calcresources=("-vcPackCustomLocn" ${VCCUSTOMEXE} \
                      "-queueType" ${QUEUETYPE} "-queueName" ${QUEUENAME} \
                      "-nodes" ${NUMNODES} "-mpi" ${NUMMPIPROCS} \
                      "-openmp" ${NUMOPENMPTHREADS} "-gpu" ${NUMGPUS} \
                      "-ligandNodes" ${NUMLIGNODES} "-ligandMpi" ${NUMLIGMPIPROCS} \
                      "-ligandOpenmp" ${NUMLIGOPENMPTHREADS} "-ligandGpu" ${NUMLIGGPUS})

export datadirs=("-rawInputData" ${VCRAWDATADIR} "-projectDir" ${VCPROJECTDIR})

if [ $MOLSYSTEMTYPE = 'protein+ligand' ] ; then
    export proteinsetup=("-proteinFileName" ${PROTEINFILENAME} "-proteinForcefield" ${PROTEINFORCEFIELD} \
                         "-proteinPrep" ${PROTEINPREP} "-proteinTyper" ${PROTEINTYPER} \
                         "-proteinRefLig" ${PROTEINREFLIGAND} "-proteinRealCutoff" ${REALATOMCUTOFF} \
                         "-liveRealRefChoice" ${LIVEREALREFCHOICE} "-liveRealRefFile" ${LIVEREALREFFILE} \
                         "-proteinLiveCutoff" ${LIVEATOMCUTOFF} "-completeLiveRes" ${COMPLETELIVERES} \
                         "-minLiveForCompln" ${MINLIVEFORCMPLT} "-proteinRelax" ${PROTEINRELAX} \
                         "-proteinRelaxCutoff" ${PROTEINRELAXCUTOFF})
else
    export proteinsetup=''
fi

if [ $MOLSYSTEMTYPE = 'host+ligand' ] ; then
    export hostsetup=("-hostForcefield" ${HOSTFORCEFIELD} "-hostPrep" ${HOSTPREP} "-hostTyper" ${HOSTTYPER} \
                      "-hostCharger" ${HOSTCHARGER})
else
    export hostsetup=''
fi
                 
export ligandsetup=("-ligandForcefield" ${LIGANDFORCEFIELD} "-ligandPrep" ${LIGANDPREP} \
                    "-ligandTyper" ${LIGANDTYPER} "-ligand2D3D" ${LIGAND2D3D} "-ligandCharger" ${LIGANDCHARGER} \
                    ${LIGSDFFROMINPCRD} "-mapLigToTemplate" ${MAPLIGTOTEMPLATE} \
                    "-preGenLigConfs" ${PREGENLIGCONFS} ${USETEMPLATESDF})

export calcenginectrl=("-calcnType" ${CALCNTYPE} "-mpiSearchStyle" ${MPISEARCHSTYLE} \
                       "-mpiMaxUncoupledIters" ${MPIMAXUCPLDITERS} \
                       "-confSearchStyle" ${CONFSEARCHSTYLE} "-maxConfSearches" ${MAXCONFSEARCHES} \
                       "-ligConfSearchStyle" ${LIGCONFSEARCHSTYLE} "-maxLigConfSearches" ${MAXLIGCONFSEARCHES})

export solvationmodel=("-solvDielecInternal" ${DIELECINTERNAL} "-solvDielecExternal" ${DIELECEXTERNAL})

export resultsextract=("-extractFor" ${EXTRACTFOR} "-numConfsToExtract" ${MAXCONFSTOEX})

export postproclimit=("-postprocessConfLimit" ${POSTPROCCONFLMIT})

export currentDate=`date`
echo "# Timestamp: $currentDate" >> $CMDLOUT 
echo >> $CMDLOUT 

#----------------------------
# Output the set variables
#----------------------------

# Workflow exe and data directory names

echo 'Workflow exe location :' $VCWORKFLOWEXE >> $CMDLOUT
echo 'Raw data directory    :' $VCRAWDATADIR >> $CMDLOUT
echo 'Project directory     :' $VCPROJECTDIR >> $CMDLOUT
echo >> $CMDLOUT

# Molecular system type

echo 'Molecular system type :' $MOLSYSTEMTYPE >> $CMDLOUT
echo >> $CMDLOUT

# Possible custom directory location of VM2 calculation engine exe 

echo 'Custom vm2 calcn engine location :' $VCCUSTOMEXE >> $CMDLOUT
echo >> $CMDLOUT

# Queue type 

echo 'Queue type or shell script type  : '$QUEUETYPE >> $CMDLOUT
echo 'Non default queue name/partition : '$QUEUENAME >> $CMDLOUT
echo 'Prep mode                        : '$PREPMODE >> $CMDLOUT
echo >> $CMDLOUT

# Parallel processing control

echo 'Parallel processing control for receptor involved calcs:' >> $CMDLOUT
echo 'Number of compute nodes  :' $NUMNODES >> $CMDLOUT
echo 'Number of MPI processes  :' $NUMMPIPROCS >> $CMDLOUT
echo 'Number of OpenMP threads :' $NUMOPENMPTHREADS >> $CMDLOUT
echo 'Number of GPUs           :' $NUMGPUS >> $CMDLOUT
echo >> $CMDLOUT

echo 'Parallel processing control for ligand calcs:' >> $CMDLOUT
echo 'Number of compute nodes  :' $NUMLIGNODES >> $CMDLOUT
echo 'Number of MPI processes  :' $NUMLIGMPIPROCS >> $CMDLOUT
echo 'Number of OpenMP threads :' $NUMLIGOPENMPTHREADS >> $CMDLOUT
echo 'Number of GPUs           :' $NUMLIGGPUS >> $CMDLOUT
echo >> $CMDLOUT

# Protein setup 

if [ $MOLSYSTEMTYPE = 'protein+ligand' ] ; then
    echo 'Protein forcefield             :' $PROTEINFORCEFIELD >> $CMDLOUT
    echo 'Protein preparation            :' $PROTEINPREP >> $CMDLOUT
    echo 'Protein typer                  :' $PROTEINTYPER >> $CMDLOUT
    echo 'Protein data file name         :' $PROTEINFILENAME >> $CMDLOUT
    echo 'Protein reference ligand       :' $PROTEINREFLIGAND >> $CMDLOUT
    echo 'Real/Live atom reference choice:' $LIVEREALREFCHOICE >> $CMDLOUT
    echo 'Real/Live atom reference file  :' $LIVEREALREFFILE >> $CMDLOUT
    echo 'Real atom cutoff distance      :' $REALATOMCUTOFF >> $CMDLOUT
    echo 'Live atom cutoff distance      :' $LIVEATOMCUTOFF >> $CMDLOUT
    echo 'Live residue completion        :' $COMPLETELIVERES >> $CMDLOUT
    echo 'Min. live atoms for completion :' $MINLIVEFORCMPLT >> $CMDLOUT
    echo 'Protein atom relaxation        :' $PROTEINRELAX >> $CMDLOUT
    echo 'Protein atom relaxation cutoff :' $PROTEINRELAXCUTOFF >> $CMDLOUT
    echo >> $CMDLOUT
fi

# Host setup 

if [ $MOLSYSTEMTYPE = 'host+ligand' ] ; then
    echo 'Host forcefield             :' $HOSTFORCEFIELD >> $CMDLOUT
    echo 'Host preparation            :' $HOSTPREP >> $CMDLOUT
    echo 'Host typer                  :' $HOSTTYPER >> $CMDLOUT
    echo 'Host partial charges method : '$HOSTCHARGER >> $CMDLOUT
    echo >> $CMDLOUT
fi

# Ligand setup 

echo 'Ligand forcefield                :' $LIGANDFORCEFIELD >> $CMDLOUT
echo 'Ligand preparation               :' $LIGANDPREP >> $CMDLOUT
echo 'Ligand typer                     :' $LIGANDTYPER >> $CMDLOUT
echo 'Ligand SDF overwriten by inpcrd  :' $LIGSDFFROMINPCRD >> $CMDLOUT
echo 'Ligand 2D to 3D method           : '$LIGAND2D3D >> $CMDLOUT
echo 'Ligand partial charges method    : '$LIGANDCHARGER >> $CMDLOUT
echo 'Ligand atom mapping method       : '$MAPLIGTOTEMPLATE >> $CMDLOUT
echo 'Ligand conformer pre-generation  : '$PREGENLIGCONFS >> $CMDLOUT
echo 'Use template ligand SD file      : '$USETEMPLATESDF >> $CMDLOUT
echo >> $CMDLOUT

# VM2 calculation engine control

echo 'MPI conformational search style  :' $MPISEARCHSTYLE >> $CMDLOUT
echo 'Max no. of uncoupled/mixed iters :' $MPIMAXUCPLDITERS >> $CMDLOUT
echo 'Receptor involved search style   :' $CONFSEARCHSTYLE >> $CMDLOUT
echo 'Max no. of searches/search type  :' $MAXCONFSEARCHES >> $CMDLOUT
echo 'LIgand-only search style         :' $LIGCONFSEARCHSTYLE >> $CMDLOUT
echo 'Max no. of searches/search type  :' $MAXLIGCONFSEARCHES >> $CMDLOUT
echo >> $CMDLOUT

# Set continuum solvation models dielectric constants 

echo 'Internal dielectric constant     :' $DIELECINTERNAL >> $CMDLOUT
echo 'External dielectric constant     :' $DIELECEXTERNAL >> $CMDLOUT
echo >> $CMDLOUT

# Compare with experiment? 

echo 'Compare with experimental data   : '$HAVEEXPT >> $CMDLOUT
echo >> $CMDLOUT

# Results extraction

echo 'Extract results for covenience of : '$EXTRACTFOR >> $CMDLOUT
echo 'Maximum conformers to extract     : '$MAXCONFSTOEX >> $CMDLOUT
echo >> $CMDLOUT
