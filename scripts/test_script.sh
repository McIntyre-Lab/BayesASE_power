############################
#
# Set variables. 
#
#############################
Project_Folder=/home/ksherbina/BayesASE_power # Change this to whereever you saved the package on your machine
R_Libraries=rstan
R_Programs=${Project_Folder}/BayesASE_power/tasks
Python_Programs=${Project_Folder}/BayesASE_power
Input=${Project_Folder}/example_in
Output=${Project_Folder}/example_out

############################
#
# Virtual environmnet set-up. 
#
#############################

python3 -m venv .venv_bayesase
source .venv_bayesase/bin/activate
python3 -m pip install BayesASE

############################
#Install libary "here" in R
#Single line from shell
#Can do from inside R
############################

Rscript -e 'install.packages("here")'

#####################################
#Simulate read counts according to negative binomial model as described in G3 paper 
#using the user specified simulation parameters in the CSV desing file.  
###############################################################
cd $Python_Programs
python3 ${Python_Programs}/run_read_count_simul.py -d ${Input}/design_H1_null.csv -o ${Output}
python3 ${Python_Programs}/run_read_count_simul.py -d ${Input}/design_H1_not_null.csv -o ${Output}

##############################################################
#Merges pairs of datasets based on the design files that were used to simulate them. 
#Datasets are merged if they all have the same parameters except for theta. 
#User can now specify a different output directory. 
###############################################################

python3 ${Python_Programs}/merge_simul_conditions.py -d1 $Input/design_H1_null.csv -d2 $Input/design_H1_null.csv -i $Output
python3 ${Python_Programs}/merge_simul_conditions.py -d1 $Input/design_H1_null.csv -d2 $Input/design_H1_not_null.csv -i $Output
python3 ${Python_Programs}/merge_simul_conditions.py -d1 $Input/design_H1_not_null.csv -d2 $Input/design_H1_not_null.csv -i $Output


###############################################################
#For each read count dataset for which you want to fit the model, first you create a design file. 
#The "compID" is set to the input filename to make sure that all of the parameters used 
#to simulate the data are recorded in the file output after fitting the BayesASE model. 
#Then, this design file is used to fit the NBmodel to the simulated data. 
###############################################################

mkdir ${Output}/ase_bayesian_out
cd ${Output}/ase_bayesian_out

for input_file in $Output/H1_null_H2_null_H3_null/theta1_0.5_theta2_0.5_rsim-g1_0.8_rsim-g2_0.8_nbiorep_3_allelicreads_960_simruns_5.tsv \
$Output/H1_null_H2_not_null_H3_not_null/theta1_0.5_theta2_0.6_rsim-g1_0.8_rsim-g2_0.8_nbiorep_3_allelicreads_960_simruns_5.tsv \
$Output/H1_not_null_H2_not_null_H3_null/theta1_0.6_theta2_0.6_rsim-g1_0.8_rsim-g2_0.8_nbiorep_3_allelicreads_960_simruns_5.tsv
do
python3 ${Python_Programs}/create_nbmodel_design_file.py -i ${input_file} -o $Input/condition_design_file.tsv
nbmodel_stan2.py -d $Input/condition_design_file.tsv -i ${input_file} -c 2 -t 6000 -w 3000 
done


###############################################################
#Compute summary statistics of posterior estimates and include simulation parameter information 
#for each simulated dataset in a directory specified by the user that was fit by the NB model. 
#More than one directory can be given to the argument -i.
###############################################################
python ${Python_Programs}/summarize_posterior_estimates.py -o $Output/ase_bayesian_out_posterior_estimates_summary.csv -i $Output/ase_bayesian_out


###############################################################
#Create plots of power and type I error versus one of the simulation parameters of interest (given to -p argument): 
#num_bioreps, num_allele_specific_reads_per_biorep, nfeature, delta_AI. 
#For a simulation parameter on the xaxis, as many plots are created as the combinations of values 
#of the simulation parameters that are fixed to create the plot. 
#If there are repeated measurements for a value on the x axis, the average and the standard error of the mean are plotted.
###############################################################


python ${Python_Programs}/plot_power.py -p num_bioreps -o $Output/data_visualization -i $Output/posterior_estimates_summary.csv 

python ${Python_Programs}/plot_power.py -p num_allele_specific_reads_per_biorep -o $Output/data_visualization -i $Output/posterior_estimates_summary.csv 

python ${Python_Programs}/plot_power.py -p nfeature -o $Output/data_visualization -i $Output/posterior_estimates_summary.csv 

python ${Python_Programs}/plot_power.py -p delta_AI -o $Output/data_visualization -i $Output/posterior_estimates_summary.csv



 
