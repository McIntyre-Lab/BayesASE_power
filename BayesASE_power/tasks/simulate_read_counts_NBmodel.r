args = commandArgs(trailingOnly=TRUE)
my.theta <- as.numeric(args[1])  ## Level of allelic imbalance
simruns <- as.numeric(args[2])   ## Number of simulations
out.file <- args[3]
nreps <- as.numeric(args[4])     ## Number of biological replicates
n_allele_specific_reads <- as.numeric(args[5]) ## Sum of unambiguously mapped reads (i.e. map better to one allele) 
                                               ## in the experiment across all bioreps

my.qtest <- 0.8
my.qline <- 0.8
myreads <- n_allele_specific_reads/2/nreps/mean(my.qtest, my.qline) ## This is coverage from the G3 paper
my.alpha <- sqrt((1/my.theta)-1) ## In the stan2 model, theta = 1/(alpha[i]^2+1)
out.file <- paste0(paste(out.file, 'theta', my.theta, 'rsim-g1', my.qtest, 'rsim-g2', 
                  my.qline, 'nbiorep', nreps, 'allelicreads', n_allele_specific_reads, 
                  'simruns', simruns, sep='_'), '.tsv')

#Removed set.seed(0) because always gave the same result!!!!!
#set.seed(0)

seqcond <- "c1"

repsuffix <- paste0("_rep", seq(1, nreps))

## The three possible alignment states: better to allele g1 (formerly tester), 
## better to allele g2 (formerly line), equally good to both.
counttester <- as.vector(sapply(paste("counts_", seqcond, "_g1_total", sep=""), paste0, repsuffix))
countline <- as.vector(sapply(paste("counts_", seqcond, "_g2_total", sep=""), paste0, repsuffix))
countboth <- as.vector(sapply(paste("counts_", seqcond, "_both_total", sep=""), paste0, repsuffix))
countheader <- paste(counttester, countline, countboth, sep="\t", collapse="\t")
priorstester <- paste("prior_", seqcond, "_g1", sep="")
priorsline <- paste("prior_", seqcond, "_g2", sep="")
allpriors <- sort(c(priorstester, priorsline))
seqreps <- paste(seqcond, "_num_reps", sep="")
activeflag <- paste(seqcond, "flag_analyze", sep="_")
headers <- paste(c("FEATURE_ID", seqreps, countheader, allpriors, activeflag), collapse="\t")
print(unlist(strsplit(headers,"\t")))
cat(headers, file=out.file, append=FALSE, sep="\n")

## End of arguments and names copied from the scripts used for the analysis of real data

##################################
##
## Simulation
##
##################################
print(simruns)
for (aaa in 1:simruns)
{
  ## Parameters of true model
  # true_betas_row1 <- c(1, 1.2, 0.7)*myreads   #These are the biorep effets, the beta_i s
  true_betas_row1 <- rep(1, nreps)*myreads
  true_alpha <- my.alpha     ## if different from 1, AI in the environment
  true_gamma <- 1            ## The current model assumes 1, but it used to be useful before
  true_tau <- 1              ## The current model assumes 1, but at some point we considered it different from 1


  allq <- c(my.qtest, my.qline)

  true_phi <- 0.02           #Neg binomial dispersion parameter, the bigger it is the higher the variance=mu+phi mu^2 is

  flaganalyze <- 1

  means <- c(allq[1]/true_alpha, allq[2]*true_alpha, ((1-allq[1])/true_alpha+(1-allq[2])*true_alpha)*true_tau)
	for(i in 1:nreps)
  {
    xs <- rnbinom(1, size=1/true_phi, mu=means[1]*true_betas_row1[i])
		ys <- rnbinom(1, size=1/true_phi, mu=means[2]*true_betas_row1[i])
		zs <- rnbinom(1, size=1/true_phi, mu=means[3]*true_betas_row1[i])
    if(i==1) mycounts <- paste(xs, ys, zs, sep="\t") else mycounts <- paste(mycounts, xs, ys, zs, sep="\t")
	}

	cat("mycounts is", mycounts, "\n")

	out <- paste("fusion_id", nreps,
	          mycounts,
	          paste(as.vector(t(allq)), collapse="\t"), paste(flaganalyze, collapse="\t"), sep="\t")
	cat(out, file=out.file, append=TRUE, sep="\n")
}
