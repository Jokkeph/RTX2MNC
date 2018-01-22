# coding=utf-8
import Pipescript
import sys, os, shutil, dicom, magic, argparse

######################################### Begin Argparse section #########################################
parser = argparse.ArgumentParser()
parser.add_argument("--revres", help="Reverses the resample so the PET is resampled as the RT, file saved the same place", action="store_true")
parser.add_argument("--mr", help="Optional Input directory of Dicom files or a single mnc file, the second input file will be resampled upon this file")
parser.add_argument("PET", help="Input directory of Dicom files or a single mnc file")
parser.add_argument("RT", help="Input RT file")
parser.add_argument("--ForceRT", help="Forces the program to run even though the RT file and input scanning file does not match", action="store_true")
parser.add_argument("--auto", help="Allow the input of directories, the scanning files should be inside a directory etc. dir/dicom/file.dcm and rt file rt/rtss.dcm", action="store_true")
parser.add_argument("--xtraprint", help=" Prints additional messages about the scripts execution", action="store_true")
parser.add_argument("--keepmnc", help="Keeps the directories with mnc fiels that are created during the script", action="store_true")
args = parser.parse_args()

if args.PET.endswith("/"):
    args.PET = args.PET[:-1]
if args.RT.endswith("/"):
    args.RT = args.RT[:-1]
if args.mr and args.mr.endswith("/"):
    args.mr = args.mr[:-1]
#Tmpfoldernames
PET = "PETmnc"
MR = "MRmnc"
RT = "RT"
RTOut = "Resampled"
cwd = os.getcwd()
#Erase the folders we wanna make
os.system("rm -r -f " + PET + " " + MR + " " + RT)
def petmrdir(arg):
    liste = []
    path = cwd + "/" + arg + "/"
    #iterates over args.pet(dicom)
    for filename1 in os.listdir(path):
        liste.append(filename1)
        if os.path.isdir(path + filename1):
            for filename in os.listdir(path + filename1):
                #after traversing 2 levels we now have all the dicom files, we check if the first is dicom
                if magic.from_file(path + filename1 + "/" + filename) == "DICOM medical imaging data":
                    ds = dicom.read_file(path + filename1 + "/" + filename)
                    #if dicom file rename it to the studyid
                    if "SeriesInstanceUID" in ds:
                        StudyID = ds[0x0020,0x000e].value
                        os.rename(path + filename1, path + StudyID)
                        #print "Renaming files... \n"
                else:
                    print "File is not dicom ", path + filename1 + "/" + filename
                break
        else:
            print "Error: The directory structure should be DirOfDicomDirs/DirectoryOfDicomFiles/file.dcm \n"
            print "Exiting..\n"
            sys.exit()
    return liste

def handleInput(tval):
    tmp1 = False
    tmp2 = False
    if tval == True:
        MRlist = petmrdir(args.mr)
        tmp1 = True
    if os.path.isdir(args.PET) and os.path.isdir(args.RT):
        PETliste = petmrdir(args.PET)
        tmp2 = True
        RTlist = []
        #iterate over rt files in directory
        rtpath = cwd + "/" + args.RT + "/"
        for filename in os.listdir(rtpath):
            if magic.from_file(rtpath + filename) == "DICOM medical imaging data":
                ds = dicom.read_file(rtpath + filename)
                #if dicom file we wanna rename as studyid of an rt sequence
                if ([0x3006,0x0010] in ds):
                    StudyUIDRT = ds[0x3006,0x0010][0][0x3006,0x0012][0][0x3006,0x0014][0][0x0020,0x000e].value
                    SeriesInsUID = ds[0x0020,0x000e].value
                    newname = rtpath + StudyUIDRT + "_" + SeriesInsUID
                    RTlist.append(newname)
                    os.rename(rtpath + filename, newname)
                    #print "Renaming files... \n"
                else:
                    print "RT file have no contours"
    if tmp1 == True and tmp2 == True:
        return MRlist, PETliste, RTlist
    elif tmp1 == False and tmp2 == True:
        return PETliste, RTlist




#Check if all three args are directories
if args.auto == True and args.mr:
    MRlist = handleInput(True)[0]
    PETlist = handleInput(True)[1]
    RTlist = handleInput(True)[2]
    #call the pipescript on the different files
    for i in range(0,len(MRlist)):
        for k in range(0,len(RTlist)):
            rest = RTlist[k].split('_', 1)[0].split(args.RT + "/", 1)[1]
            rtlistpath = RTlist[k].split(args.RT + "/", 1)[1]
            if (MRlist[i] == rest):
                Pipescript.main(args.PET + "/" + PETlist[i], args.RT + "/" + rtlistpath, args.revres, args.mr + "/" + MRlist[i], args.ForceRT)
            elif args.xtraprint == True:
                print "The RT file: ", RTlist[k] ," is not defined on the input file: ", MRlist[i]

#Check if both arguments are directories
elif args.auto == True:
    PETlist = handleInput(False)[0]
    RTlist = handleInput(False)[1]
    #call the pipescript on the different files
    for i in range(0,len(PETlist)):
        for k in range(0,len(RTlist)):
            rest = RTlist[k].split('_', 1)[0].split(args.RT + "/", 1)[1]
            rtlistpath = RTlist[k].split(args.RT + "/", 1)[1]
            if (PETlist[i] == rest):
                Pipescript.main(args.PET + "/" + PETlist[i], args.RT + "/" + rtlistpath, args.revres, args.mr, args.ForceRT)
            elif args.xtraprint == True:
                print "The RT file: ", RTlist[k] ," is most likely not defined on the input file: ", PETlist[i]

else:
    if os.path.isdir(args.RT) == False:
        Pipescript.main(args.PET, args.RT, args.revres, args.mr, args.ForceRT)# do whatever is in Pipescript
    else:
        print "RT input is a directory please use the --Auto option"

#Erase the folders we used in the process
if args.keepmnc == False:
    os.system("rm -r -f " + PET + " " + MR + " " + RT)
