# coding=utf-8
import sys, os, shutil, dicom, magic, argparse

######################################### Begin Argparse section #########################################
parser = argparse.ArgumentParser()
parser.add_argument("--RevRes", help="Reverses the resample so the PET is resampled as the RT, file saved the same place", action="store_true")
parser.add_argument("--Resample", help="Input directory of Dicom files or a single mnc file")
parser.add_argument("PET", help="Input directory of Dicom files or a single mnc file")
parser.add_argument("RT", help="Input RT file")
args = parser.parse_args()
######################################### End Argparse section ###########################################

############################################ Function section ############################################
#Given a output directory and the remainder of the mincresample command it runs the mincresample command
def Resample(Directory, resamplestring):
        if not os.path.exists(Directory):
            os.mkdir(Directory)
        #Terminal command mincresample -nearest_neighbour OutRT/20150602_113952.mnc -like PETmnc/20150602_113952.mnc out_resamp.mnc
        os.system("mincresample -nearest_neighbour " + resamplestring)
#Given a output directory, an rt file, and output name and the mnc file which the RT is defined on, it runs the global rtx2mnc command.
def rtx2mnc(Directory, definedon, rtfile, outname):
    if not os.path.exists(Directory):
        os.mkdir(Directory)
    os.system("rtx2mnc " + definedon +  " " + rtfile +  " " + Directory +  "/" + outname)
#Given a output directory and the end of the dcm2mnc string it runs the dcm2mnc command
def dcm2mnc(Directory, resamplestring):
    if not os.path.exists(Directory):
        os.mkdir(Directory)
    os.system("dcm2mnc -usecoordinates -dname '' -fname %D_%T " + resamplestring)
#Given a directory we enter the directory and picks a dicom file, which we fetch the StudyID from, and then compaers it with the RT file for a match. Furthermore we take time and date for file name creation later.
def fetchStudyID(fileTocheck):
    #We fetch a single dicom file in order to get the tag to check with RT file later
    for filename in os.listdir(cwd + "/" + fileTocheck):
        tmp = filename
        break
    # If we have MR argument check if the RT file match and turn mr.dcm files into mr.mnc
    ds1 = dicom.read_file(fileTocheck + "/" + tmp)
    if "SeriesInstanceUID" in ds1 and ds1[0x0020,0x000e].value == StudyUIDRT:
        Date = ds1[0x0008,0x0020].value
        Time = ds1[0x0008,0x0030].value
        tmp = Date + "_" + Time[:-7]
    else:
        print "Error: RT file is not defined on input file \n exiting..."
        sys.exit()
    return tmp
########################################## End function section ##########################################

####################################### Begin value setting section ######################################
#Tmpfoldernames
PET = "PETmnc1"
MR = "MRmnc1"
RT = "RT1"
RTOut = "ResampledPET1"
#Erase the folders we wanna make
os.system("rm -r -f " + PET + " " + MR + " " + RT + " " + RTOut)
#Get Current dir
cwd = os.getcwd()
####################################### End value setting section ########################################

###################################### Begin RT file check section #######################################
#Check if RT file is in Dicom format
if magic.from_file(args.RT) == "DICOM medical imaging data":
    #StudyInstanceUID inside the contour sequence for RT
    ds = dicom.read_file(args.RT)
    if ([0x3006,0x0010] in ds):
        StudyUIDRT = ds[0x3006,0x0010][0][0x3006,0x0012][0][0x3006,0x0014][0][0x0020,0x000e].value
    else:
        print "The RT file have no contours\n exiting..."
        sys.exit()
else:
    print "Error: The RT file is not Dicom format"
    sys.exit()

###################################### End RT file check section #######################################

################################ Begin Case handling for 2 image inputs ################################
#Check for MR argument
if args.Resample:
    #If we get a directory of files we need to use dcm2mnc before using rtx2mnc
    if os.path.isdir(args.Resample) and os.path.isdir(args.PET):
        tmp = fetchStudyID(args.Resample)
        dcm2mnc(MR, cwd + "/" + args.Resample + " " + MR)
        dcm2mnc(PET, cwd + "/" + args.PET + " " + PET)
        rtx2mnc(RT, "MRmnc1/*", args.RT, tmp + ".mnc")
        #Resamples, the flag --RevRes choses which direction it ersamples
        if args.RevRes == False:
            #Terminal command mincresample -nearest_neighbour OutRT/20150602_113952.mnc -like PETmnc/20150602_113952.mnc out_resamp.mnc
            Resample(RTOut, RT + "/" + tmp + ".mnc" + " -like " + PET + "/*" + " " + RTOut + "/" + tmp + ".mnc")
        else:
            Resample(RTOut, RT + "/" + tmp + ".mnc" + " -like " + PET + "/*" + " " + RTOut + "/" + tmp + ".mnc")

    #Case of Resample file input being a mnc file
    elif os.path.isdir(args.Resample) and args.PET.endswith('.mnc'):
        tmp = fetchStudyID(args.Resample)
        #Change mr.dcm files into mr.mnc and run rtx2mnc
        dcm2mnc(MR, cwd + "/" + args.Resample + " " + MR)
        rtx2mnc(RT, "MRmnc1/*", args.RT, tmp + ".mnc")
        #Resamples, the flag --RevRes choses which direction it ersamples
        if args.RevRes == False:
            #Terminal command mincresample -nearest_neighbour OutRT/20150602_113952.mnc -like PETmnc/20150602_113952.mnc out_resamp.mnc
            Resample(RTOut, RT + "/" + tmp + ".mnc" + " -like " + args.PET + " " + RTOut + "/" + tmp + ".mnc")
        else:
            Resample(RTOut, args.PET + " -like " + RT + "/" + tmp + ".mnc " + RTOut + "/" + tmp + ".mnc")

    #Case of both input files being mnc already
    elif args.PET.endswith('.mnc') and args.Resample.endswith('.mnc'):
        print "Warning using the Resample input as mincfile will results in no verification of RT - Resample file match"
        rtx2mnc(RT, args.Resample, args.RT, "out_label.mnc")
           #Resamples, the flag --RevRes choses which direction it ersamples
        if args.RevRes == False:
           #Terminal command mincresample -nearest_neighbour OutRT/20150602_113952.mnc -like PETmnc/20150602_113952.mnc out_resamp.mnc
           Resample(RTOut, RT + "/" + "out_label.mnc" + " -like " + args.PET + " " + RTOut + "/" + "out_label.mnc")
        else:
           Resample(RTOut, args.PET + " -like " + RT + "/" + "out_label.mnc " + RTOut + "/" + "out_label.mnc")

################################ End Case handling for 2 image inputs ################################

################################ Begin Case handling for 1 image input ###############################
else:
    if os.path.isdir(args.PET):
        tmp = fetchStudyID(args.PET)
        dcm2mnc(MR, cwd + "/" + args.PET + " " + PET)
        rtx2mnc(RT, "PETmnc1/*", args.RT, tmp + ".mnc")
        #Resamples, the flag --RevRes choses which direction it ersamples
        if args.RevRes == False:
            #Terminal command mincresample -nearest_neighbour OutRT/20150602_113952.mnc -like PETmnc/20150602_113952.mnc out_resamp.mnc
            Resample(RTOut, RT + "/" + tmp + ".mnc" + " -like " + PET + "/*" + " " + RTOut + "/" + tmp + ".mnc")
        else:
            Resample(RTOut, PET + "/*" " -like " + RT + "/" + tmp + ".mnc " + RTOut + "/" + tmp + ".mnc")
    elif args.PET.endswith('.mnc'):
         print "Warning: using the mincfile alone will results in no verification of RT - PET file match"
         rtx2mnc(RT, args.PET, args.RT, "out_label.mnc")
            #Resamples, the flag --RevRes choses which direction it ersamples
         if args.RevRes == False:
            #Terminal command mincresample -nearest_neighbour OutRT/20150602_113952.mnc -like PETmnc/20150602_113952.mnc out_resamp.mnc
            Resample(RTOut, RT + "/" + "out_label.mnc" + " -like " + args.PET + " " + RTOut + "/" + "out_label.mnc")
         else:
            Resample(RTOut, args.PET + " -like " + RT + "/" + "out_label.mnc " + RTOut + "/" + "out_label.mnc")


################################### End handling for 1 image input #################################

####################################### Begin Cleanup section ######################################
#Erase the folders we used in the process
os.system("rm -r -f " + PET + " " + MR + " " + RT)
print "The Resampled file is located at " + cwd + "/" + RTOut + "/"
####################################### End Cleanup section ########################################
