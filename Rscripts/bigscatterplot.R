#!/usr/bin/env Rscript
library(RColorBrewer)
library(dcemriS4)
library(oro.nifti)
library("optparse")
library(ggplot2)

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

#calculate pearson correlation
rvalue <- cor(unlist(mpet)[!is.na(unlist(madc))], unlist(madc)[!is.na(unlist(madc))], method="pearson")
#convert double to character vector
rvalue <- as.character(rvalue)
#put them together
rvalue <- paste("R-Value:", rvalue, sep=" ")

#Set output
png(filename=opt$out)
#Create the plot
plot(mpet[[1]][!is.na(madc[[1]])], madc[[1]][!is.na(madc[[1]])], main=opt$title, xlab = "SUV", ylab = "ADC", xlim=c(0, opt$xaxis), ylim=c(0, 4000))
#plot the points into the plot
for (i in 2:length(adc_data)){
points(mpet[[i]][!is.na(madc[[i]])],madc[[i]][!is.na(madc[[i]])], col=i)
}
#Draw linear regression line
abline(lm(unlist(madc)[!is.na(unlist(madc))]~unlist(mpet)[!is.na(unlist(madc))]), col="red")
#Add R value to left bottom
mtext(rvalue, 1, line=2, adj=0)
legend(x= "topright",y= "topright", c("Linear Regression"), lty=c(1,1), lwd=c(2.5,2.5),col=c("red")) # gives the legend lines the correct color and width
#Close plot writing it to output
dev.off()
