#!/usr/bin/env Rscript
library(ggplot2)
library(manipulate)
library("optparse")
library(dcemriS4)
library(oro.nifti)
library(RColorBrewer)

#############################################################################################################
##### Rigshospitalet - Department of Clinical Physiology and Nuclear Medicine PET- and Cyclotron unit   #####
##### Author: Joachim Hansen                                                                            #####
##### Mail: Joachim.Pries.Hansen@regionh.dk                                                             #####
##### Phone: +45 60632283                                                                               #####
##### Supervisor: Flemming Littrup Andersen                                                             #####
#############################################################################################################

option_list = list(
  make_option(c("-a", "--adc"), type="character", default=NULL,
              help="dataset file name", metavar="character"),
  make_option(c("-p", "--pet"), type="character", default=NULL,
              help="dataset file name", metavar="character"),
  make_option(c("-r", "--rt"), type="character", default=NULL,
              help="dataset file name", metavar="character"),
  make_option(c("-d", "--constant"), type="character", default=NULL,
              help="correction divided by patientweight", metavar="character"),
  make_option(c("-x", "--xaxis"), type="double", default="35",
              help="Dimension of x axis", metavar="double"),
  make_option(c("-t", "--title"), type="character", default="Scatterplot",
              help="Name of the plot", metavar="character"),
  make_option(c("-o", "--out"), type="character", default="MNCfiles",
              help="Output directory", metavar="character")
);

opt_parser = OptionParser(option_list=option_list);
opt = parse_args(opt_parser);

if (is.null(opt$adc) | is.null(opt$pet) | is.null(opt$rt)){
  print_help(opt_parser)
  stop("At least one argument must be supplied (input file).n", call.=FALSE)
}

suv <- as.vector(strsplit(opt$constant, ","))
#List the files in the folders
adc <- list.files(opt$adc, pattern="*.nii", full.names=TRUE)
pet <- list.files(opt$pet, pattern="*.nii", full.names=TRUE)
rt <- list.files(opt$rt, pattern="*.nii", full.names=TRUE)
#Convert with img_data
adc_data <- lapply(adc, img_data)
pet_data <- lapply(pet, img_data)
rt_data <- lapply(rt, img_data)
#apply mask to adc data
adcmask <- Map('*', rt_data, adc_data)
#Create output lists
madc = list()
mpet = list()
#Convert adc and pet into matrix type, also apply mask to petdata and divide with suv value, Furthermore set all 0's to NA in the adc
for (i in 1:length(adc_data)){
madc[[i]] <- as.matrix(adcmask[[i]])
mpet[[i]] <- ((pet_data[[i]]*rt_data[[i]]) / as.numeric(suv[[1]][i])) * 1000 #from kilo to gram bql
mpet[[i]] <- as.matrix(mpet[[i]])
madc[[i]][madc[[i]]==0] <- NA
}

#Create custom color palette
rf <- colorRampPalette(rev(brewer.pal(11,'Spectral')))
r <- rf(32)
#Chose output filename
firstfilename <- paste(opt$out, "JointHistogram200bins.png", sep = "")
png(filename=firstfilename)
#Create plot
p <- ggplot(data = NULL, aes(unlist(mpet)[!is.na(unlist(madc))],unlist(madc)[!is.na(unlist(madc))])) + xlab("SUV") + ylab("ADC") + ggtitle(opt$title) + xlim(0, opt$xaxis) + ylim(0, 4000)
#Make it quadratic bins
h3 <- p + stat_bin2d(bins=200, drop = TRUE) + scale_fill_gradientn(colours=r)
#Actually plot the plot in a window
h3
#Close plot window so we save the image
dev.off()
secondfilename <- paste(opt$out, "JointHistogram200bins_logscale.png", sep = "")
png(filename=secondfilename)
h3 <- p + stat_bin2d(bins=200, drop = TRUE) + scale_fill_gradientn(trans = "log", colours=r)
#Actually plot the plot in a window
h3
#Close plot window so we save the image
dev.off()

# for (i in 1:length(mpet)){
# rvalue <- cor(mpet[[i]][!is.na(madc[[i]])], madc[[i]][!is.na(madc[[i]])], method="pearson")
# # rvalue <- paste("", rvalue, sep=" ")
# write(rvalue,file="../rvalues",append=TRUE)
# }

# #convert double to character vector
# rvalue <- as.character(rvalue)
# #put them together
# rvalue <- paste("", rvalue, sep=" ")
#
# line="blah text blah blah etc etc"
# write(line,file="rvalues",append=TRUE)
