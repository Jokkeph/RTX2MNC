#!/usr/bin/python
# coding=utf-8
import textwrap
import sys, os, shutil, dicom, magic, argparse, commands, time

import functions as f
import Plot_ADC_SUV
import UsePipe_rtx2mncOnDirectories

#############################################################################################################
##### Rigshospitalet - Department of Clinical Physiology and Nuclear Medicine PET- and Cyclotron unit   #####
##### Author: Joachim Hansen                                                                            #####
##### Mail: Joachim.Pries.Hansen@regionh.dk                                                             #####
##### Phone: +45 60632283                                                                               #####
##### Supervisor: Flemming Littrup Andersen                                                             #####
#############################################################################################################


######################################### Begin Argparse section #########################################
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
# parser.description = "There are two major options, either. \n\n. The other option would be to
parser.description=textwrap.dedent('''\
...               First Option
...         -----------------------------------------------------------------------------
...             Supply the required directory arguments below with two dashes(--)
...             running the program that converts 4 directories into mnc files,
...             then resamples them into the --re argument,
...             and then creates scatterplots with the --yaxis and --xaxis arguments in R
...
...             Below is an example with all arguments being of type MR/dir/    manyfiles.dcm
...                python main.py --defon MR/ --rt RT/ --yaxis ADC/ --xaxis PET/ --re MR/
...             Optional flags: "---keepmnc", "---totalscatter", "---xdim", "---title"
...              Outputtet in: MNCfiles/
...
...               Second Option
...         -----------------------------------------------------------------------------
...             Supply the required single dash arguments(-) -defon, -rts
...             The program then returns the rt file as minc and
...             resampled as the mr input or the pet input if this was given. "
...
...             Below is an example with rt being a file, and MR, PET being of type MR/ manyfiles.dcm
...                 python main.py -defon MR/ -rts rt
...                 python main.py -mr MR/ -rts rt -snd PET/
...             In this example the MR and rt argument is of type MR/dirs/  manyfiles.dcm and rt/dirs/rtfile
...             The auto flag allows proccessing alot of files at the same time
...                 python main -auto -forcert -defon MR/ -rts rt/
...
...             Optional flags: ---keepmnc, -revres, -forcert, -auto, -rtout
...              Outputtet in: MNCfiles/Resampled/ as default
...               Third Option
...         -----------------------------------------------------------------------------
...             Supply the program with calls -p1, -p2, -p3, -p4(only need 2 arguments 4 max) -pout
...             Given that the PNG filename is the same in e.g. -p1 -p2 dirs:
...                 Then the PNG's will be combined into one png file placed in the directory
...                 given by -pout
...             The arguments should be directory_of_PNG's/
''')
#directoryscript.py
parser.add_argument("-defon", help="Input directory of Dicom files or a single mnc file")
parser.add_argument("-snd", help="Input directory of Dicom files or a single mnc file, the second input file will be resampled upon this file")
parser.add_argument("-rts", help="Input rt file")
parser.add_argument("-rtout", help="Output directory to put the RT file in. If none given its placed in directory Resampled/")
parser.add_argument("-forcert", help="Forces the program to run even though the RT file and input file does not match", action="store_true")
parser.add_argument("-auto", help="Allow the input of directories, the scanning files should be inside a directory etc. dir/dicom/file.dcm and rt file rt/rtss.dcm", action="store_true")
parser.add_argument("-revres", help="Reverses the resample so the PET is resampled as the RT", action="store_true")

#scatterplots.py
parser.add_argument("--defon", help="Directory of directories containing dicom files, must be the ones that the RT is defined on or no output")
parser.add_argument("--yaxis", help="Directory of directories containing dicom files,")
parser.add_argument("--xaxis", help="Directory of directories containing dicom files,")
parser.add_argument("--rt", help="The directory containing rt directory/files")
parser.add_argument("--re", help="The file the other files will be resampled as")
parser.add_argument("--out", help="Output directory")

#universal
parser.add_argument("---keepmnc", help="Keeps the intermediary files that are created during runtime, e.g .nifti, .mnc, resampled.mnc, beforeresampled.mnc", action="store_true")
parser.add_argument("---verbose", help="Prints additional information of the programs progress", action="store_true")
parser.add_argument("---totalscatter", help="Creates one big scatterplot with all the scans", action="store_true")
parser.add_argument("---xdim", help="Scatterplot length of xaxis", type=int)
parser.add_argument("---title", help="Title of the scatterplots")
#collect png pictures
parser.add_argument("-p1", help="Directory containing PNG's")
parser.add_argument("-p2", help="Directory containing PNG's")
parser.add_argument("-p3", help="Directory containing PNG's")
parser.add_argument("-p4", help="Directory containing PNG's")
parser.add_argument("-pout", help="Defines output directory of combined PNG's")
args = parser.parse_args()
start_time = time.time()
    ####################################### Begin check if input exists ######################################


    ####################################### End check if input exists ########################################
#Create lists of the "important arguments" so we can create nicer if statements below
Scatterplot_Input = [args.rt, args.yaxis, args.xaxis, args.re, args.defon]
Collected_PNG = [args.p1, args.p2, args.p3, args.p4, args.pout]
rtx_Single = [args.snd, args.rts]
rest = [args.revres, args.defon, args.forcert, args.auto, args.keepmnc, args.verbose, args.totalscatter, args.xdim, args.title]

if(all(Scatterplot_Input) and not(all(Collected_PNG + rtx_Single))):
    #Before doing anything lets be sure the path arguments does actually exist
    f.checkExists(args.rt)
    f.checkExists(args.yaxis)
    f.checkExists(args.re)
    f.checkExists(args.xaxis)
    f.checkExists(args.defon)
    #Remove all slashes e.g tmp/folder/ becomes tmp/folder
    args.defon = f.removeSlash(args.defon)
    args.rt = f.removeSlash(args.rt)
    args.yaxis = f.removeSlash(args.yaxis)
    args.xaxis = f.removeSlash(args.xaxis)
    args.re = f.removeSlash(args.re)

    #Run seperate script
    Plot_ADC_SUV.main(args.defon, args.rt, args.yaxis, args.xaxis, args.re, args.keepmnc, args.verbose, args.totalscatter, args.xdim, args.title, args.out)
    m, s = divmod(time.time() - start_time, 60)
    h, m = divmod(m, 60)
    print("---  Executed in: %d:%02d:%02d  ---" % (h, m, s))
elif(args.defon or all(rtx_Single) and not(all(Scatterplot_Input + Collected_PNG))):
    #Before doing anything lets be sure the path arguments does actually exist

    f.checkExists(args.defon)
    f.checkExists(args.rts)


    #Remove all slashes e.g tmp/folder/ becomes tmp/folder
    args.defon = f.removeSlash(args.defon)
    args.rt = f.removeSlash(args.rts)


    if(args.snd):
        f.checkExists(args.snd)
        args.snd = f.removeSlash(args.snd)
    #Run seperate script
    UsePipe_rtx2mncOnDirectories.main(args.snd, args.defon, args.rts, args.revres, args.forcert, args.auto, args.keepmnc, args.verbose, args.rtout)
    m, s = divmod(time.time() - start_time, 60)
    h, m = divmod(m, 60)
    print("---  Executed in: %d:%02d:%02d  ---" % (h, m, s))
elif(any(Collected_PNG) and not(all(Scatterplot_Input + rtx_Single + rest))):
    arg = f.deleteNone_In_input(args, args.verbose, args.pout)
    destination, filenames = f.create2Darray(arg)
    integer, longest, newarr = f.findbiggestfolder(filenames)
    f.concatenate_correct_files(longest, filenames, newarr, args.pout, destination)
else:
    print("---  Wrong arguments given see --help  ---")
