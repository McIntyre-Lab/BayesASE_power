Two alleles of a diploid individual can show significantly different expression
referred to as allelic imbalance (AI). Comparing AI between conditions or 
tissues can provide new insights into the mechanisms of gene expression 
regulation. There is extensive literature demonstrating Type I error in AI studies 
is high, particularly when failing to account for map bias and/or using a binomial 
test. BayesASE_power was developed to address the current lack of understanding 
of the power for comparing AI between conditions and, in particular, what is the 
best allocation of resources for boosting power.

BayesASE_power consists of tools that enable users to simulate RNA-seq read counts
with a [previously published Bayesian model of AI](https://www.g3journal.org/content/8/2/447.long) 
as implemented in [BayesASE](https://pypi.org/project/BayesASE/) with 
any number of biological replicates, reads, and levels of AI. It aggregates the 
results across multiple simulated datasets to estimate and compare Type I error and power.

###### Software requirements
<ul>
<li>R >= 3.6.1 and "here" package</li>
<li>python3 with pandas-1.2.4, matplotlib-3.4.1, seaborn-0.11.1, and numpy-1.18.1</li>
</ul>
A sample script to run the software is provided in the scripts/ folder. 
