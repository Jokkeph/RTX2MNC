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
  make_option(c("-a", "--adc"), type="character", default=NULL,
              help="dataset file name", metavar="character"),
  make_option(c("-p", "--pet"), type="character", default=NULL,
              help="dataset file name", metavar="character"),
  make_option(c("-r", "--rt"), type="character", default=NULL,
              help="dataset file name", metavar="character"),
  make_option(c("-d", "--constant"), type="double", default=NULL,
              help="correction divided by patientweight", metavar="double"),
	make_option(c("-x", "--xaxis"), type="double", default="35",
              help="Dimension of x axis", metavar="double"),
  make_option(c("-t", "--title"), type="character", default="Scatterplot",
              help="Name of the plot", metavar="character"),
  make_option(c("-n", "--name"), type="character", default=NULL,
              help="Name of output", metavar="character")
);

opt_parser = OptionParser(option_list=option_list);
opt = parse_args(opt_parser);

if (is.null(opt$adc) | is.null(opt$pet) | is.null(opt$rt)){
  print_help(opt_parser)
  stop("At least one argument must be supplied (input file).n", call.=FALSE)
}

## program...
pet <- img_data(opt$pet)
adc <- img_data(opt$adc)
rt <- img_data(opt$rt)

#apply the mask
adcmask <- rt * adc
#Divide by suv value
petmask <- ((rt * pet) / opt$constant)*1000


#Convert to matrix form
mpet <- as.matrix(petmask)
madc <- as.matrix(adcmask)

#Calculate statistics

# #Remove all the (0,0) coordinates in the matrixes keep e.g (2323,0)
madc[madc==0] <- NA
#Calculate pearson correlation value
rvalue <- cor(mpet[!is.na(madc)], madc[!is.na(madc)], method="pearson")
#convert double to character vector
rvalue <- as.character(rvalue)

#Put string and character together.
rvalue <- paste("R-Value:", rvalue, sep=" ")


#Output name
png(filename=opt$name)
#Create plot
plot(mpet[!is.na(madc)], madc[!is.na(madc)], main=opt$title, xlab = "SUV", ylab = "ADC", xlim=c(0, opt$xaxis), ylim=c(0, 4000))
#Plot linear regression
abline(lm(madc[!is.na(madc)]~mpet[!is.na(madc)]), col="red") # regression line (y~x)
#put rvalue in left bottom corner

mtext(rvalue, 1, line=2, adj=0)

#Add legend
legend(x= "topright",y= "topright", c("Linear Regression"), lty=c(1,1), lwd=c(2.5,2.5),col=c("red")) # gives the legend lines the correct color and width
dev.off()
