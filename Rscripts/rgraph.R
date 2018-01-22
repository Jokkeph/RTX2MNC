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

# Read in the data
x <- scan("../rvalues", what="", sep="\n")
# sink('../test.txt')
# length(x[1:17])
# x[1]
# length(x[18:34])
# x
# sink()
png(filename="../rvaluesscatter.png")
plot(x[1:17], x[18:34], main="Rvalues", xlab = "ADC FDG", ylab = "FUGUE ADC FDG")
name = letters[1:10]
identify(x[1:17], x[18:34], labels = name, plot=TRUE)
dev.off()
