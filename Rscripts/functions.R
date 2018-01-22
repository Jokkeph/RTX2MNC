#!/usr/bin/env Rscript

library(manipulate)
library(dcemriS4)
library(oro.nifti)
library("optparse")
library(moments)

#############################################################################################################
##### Rigshospitalet - Department of Clinical Physiology and Nuclear Medicine PET- and Cyclotron unit   #####
##### Author: Joachim Hansen                                                                            #####
##### Mail: Joachim.Pries.Hansen@regionh.dk                                                             #####
##### Phone: +45 60632283                                                                               #####
##### Supervisor: Flemming Littrup Andersen                                                             #####
#############################################################################################################

option_list = list(
  make_option(c("-p", "--pet"), type="character", default=NULL, help="dataset file name", metavar="character"),
  make_option(c("-r", "--rt"), type="character", default=NULL, help="dataset file name", metavar="character"),
  make_option(c("-n", "--name"), type="character", default=NULL, help="Name of output", metavar="character"),
  make_option(c("-c", "--cpr"), type="character", default=NULL, help="number to categorize by", metavar="character")
);

opt_parser = OptionParser(option_list=option_list);
opt = parse_args(opt_parser);

if (is.null(opt$pet) | is.null(opt$rt)){
  print_help(opt_parser)
  stop("At least one argument must be supplied (input file).n", call.=FALSE)
}
## program...
pet <- img_data(opt$pet)
rt <- img_data(opt$rt)

petmask_statistics <- (rt * pet)

#Convert to matrix form
petmask_statistics <- as.matrix(petmask_statistics)
clean_mpet_statistics <- petmask_statistics[ petmask_statistics != 0 ]

# #Remove all the (0,0) coordinates in the matrixes keep e.g (2323,0)
# mpet[mpet==0] <- NULL


#Calculate pearson correlation value
# kurtosis(rnorm(100000, 3, .25))
specify_decimal <- function(x, k) trimws(format(round(x, k), nsmall=k))

skew <- skewness(clean_mpet_statistics)
kurt <- kurtosis(clean_mpet_statistics)
# out <- paste(opt$cpr, skew, kurt, sep="  |  ")
out <- paste(" ", paste(opt$cpr, specify_decimal(skew, 14), specify_decimal(kurt, 14), sep="   "), " ", sep=" ")


write(out,file=opt$name,append=TRUE)
write("-----------------------------------------------------",file=opt$name,append=TRUE)
# write("________________________________________________________",file=opt$name,append=TRUE)
# fileConn<-file(opt$name)
# writeLines(as.character(kurt), fileConn)
# writeLines(as.character(skew), fileConn)
# close(fileConn)
# png(filename="histogramtest.png")
# hist(clean_mpet)
# dev.off()
