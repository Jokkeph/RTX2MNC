import sys, os, dicom, commands, magic
from shutil import copy2
from datetime import datetime
import subprocess

#############################################################################################################
##### Rigshospitalet - Department of Clinical Physiology and Nuclear Medicine PET- and Cyclotron unit   #####
##### Author: Joachim Hansen                                                                            #####
##### Mail: Joachim.Pries.Hansen@regionh.dk                                                             #####
##### Phone: +45 60632283                                                                               #####
##### Supervisor: Flemming Littrup Andersen                                                             #####
#############################################################################################################

cwd = os.getcwd()
FNULL = open(os.devnull, 'w')
#--------------------------------------------------------------------------------------------------------#
#---------------------------------------------- main.py -------------------------------------------------#
#--------------------------------------------------------------------------------------------------------#


#Check if the path exists else exit
def checkExists(arg):
    if os.path.exists(cwd + "/" + arg) == False:
        print "\n" + cwd + "/" + arg
        print "\n --- " + str(arg) + " --- Path argument does not exist\n Exiting.."
        sys.exit()
#if arg ends with a slash remove it for consistency
def removeSlash(arg):
    if arg.endswith("/"):
        arg = arg[:-1]
    return arg

#--------------------------------------------------------------------------------------------------------#
#---------------------------------------------- collectpng.py -------------------------------------------#
#--------------------------------------------------------------------------------------------------------#


def deleteNone_In_input(arg, argprint, out):
    if (argprint == True):
        subprocess.call("rm -r " + out, shell=True)
        subprocess.call("mkdir " + out, shell=True)
    else:
        subprocess.call("rm -r " + out, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call("mkdir " + out, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
    arg = vars(arg).items()
    for j in range(0, len(arg)):
        for i in range(0,len(arg)):
            if(arg[i][1] == None or arg[i][1] == False):
                del arg[i]
                break
    return arg

def create2Darray(arg):
    destination = [[] for x in xrange(len(arg))]
    filenames = [[] for x in xrange(len(arg))]
    for i in range(0,len(arg)):
        for filename in os.listdir(arg[i][1]):
            if filename.endswith(".png"):
                destination[i].append(arg[i][1] + filename)
                filenames[i].append(filename)
    return destination, filenames

def findbiggestfolder(filenames):
    longest = 0
    for i in xrange(len(filenames)-1):
        if len(filenames[i]) > longest:
            longest = len(filenames[i])
            integer = i
    newarr = filenames[integer]
    return integer, longest, newarr

def concatenate_correct_files(longest, filenames, newarr, out, destination):
    cwd = os.getcwd()
    for i in xrange(longest):
        string = ""
        for j in xrange(len(filenames)):
            if newarr[i] in filenames[j]:
                string += str(destination[j][filenames[j].index(newarr[i])]) + " "
        os.system("montage -mode concatenate " + string + cwd + "/" + out + "/" + newarr[i])

#-----------------------------------------------------------------------------------------------------#
#------------------------------- both directoryscript and scatterplots -------------------------------#
#-----------------------------------------------------------------------------------------------------#


#function that traverses down to the file.dcm and gets the values and renames the file to path + studyid
def dirRename(arg):
    liste = []
    #Where the command is called from plus the arg path.
    path = cwd + "/" + arg + "/"
    #iterates over args.DefinedOn(dicom)
    #Check if path is dir as we want
    if os.path.isdir(path):
        for filename1 in os.listdir(path):
            #create a list of filenames in the argument directory
            liste.append(filename1)
            #if the file inside the directory is a directory then go on
            if os.path.isdir(path + filename1):
                #Now iterate over all the dicom files
                for filename in os.listdir(path + filename1):
                    #after traversing 2 levels we now have all the dicom files, we check if the first is dicom
                    if magic.from_file(path + filename1 + "/" + filename) == "DICOM medical imaging data":
                        ds = dicom.read_file(path + filename1 + "/" + filename)
                        #if dicom file rename it to the studyid
                        if "SeriesInstanceUID" in ds:
                            StudyID = ds[0x0020,0x000e].value
                            os.rename(path + filename1, path + StudyID)

                    else:
                        print "File is not dicom ", path + filename1 + "/" + filename
                    break
            else:
                print "Error: The directory structure should be DirOfDicomDirs/DirectoryOfDicomFiles/file.dcm and rt file DirectoryOfRTFiles/rtss.dcm\n"
                print "Exiting..\n"
                sys.exit()
    else:
        print "Error: Input is not a directory, structure should be DirOfDicomDirs/DirectoryOfDicomFiles/file.dcm and rt file DirectoryOfRTFiles/rtss.dcm\n"
        print "Exiting..\n"
        sys.exit()
    return liste

def checkrtx2mnc(path):
    if not os.path.exists(path):
        print "rtx2mnc did not compile the file intented to be placed at: " + path
#--------------------------------------------------------------------------------------------------------#
#------------------------------------------- directoryscript.py -----------------------------------------#
#--------------------------------------------------------------------------------------------------------#


#Given a output directory and the remainder of the mincresample command it runs the mincresample command
def Resample_dirscp(Directory, res, like, out, argprint):
    if not os.path.exists(Directory):
        os.mkdir(Directory)
    if(argprint == True):
    #Terminal command mincresample -nearest_neighbour OutRT/20150602_113952.mnc -like PETmnc/20150602_113952.mnc out_resamp.mnc
        # os.system("mincresample -clobber -nearest_neighbour " + res + " -like " + like + out)
        print "\nResampling file: ", res,
        print "\nLike file: ", like
        print "\nWriting version control into mincheader(current version: 1.8)"
        subprocess.call("mincresample -clobber -nearest_neighbour " + res + " -like " + like + " " + out, shell=True)
        subprocess.call("minc_modify_header " + out + " -sinsert 'pyrtx2mnc:Version 1.0=Added flood fill algorithm so the contour is now filled'", shell=True)
        subprocess.call("minc_modify_header " + out + " -sinsert 'pyrtx2mnc:Version 1.1=Added interpolation when drawing the rt contour'", shell=True)
        subprocess.call("minc_modify_header " + out + " -sinsert 'pyrtx2mnc:Version 1.2=Added support for more than 1 contour'", shell=True)
        subprocess.call("minc_modify_header " + out + " -sinsert 'pyrtx2mnc:Version 1.3=Added so you can execute directories of severel RT and scanning files at once'", shell=True)
        subprocess.call("minc_modify_header " + out + " -sinsert 'pyrtx2mnc:Version 1.4=Added version control in the minc header file'", shell=True)
        subprocess.call("minc_modify_header " + out + " -sinsert 'pyrtx2mnc:Version 1.5=Added a check so the script can now check if the rt matches a mnc file input'", shell=True)
        subprocess.call("minc_modify_header " + out + " -sinsert 'pyrtx2mnc:Version 1.6=Added more dummy checks and error handling'", shell=True)
        subprocess.call("minc_modify_header " + out + " -sinsert 'pyrtx2mnc:Version 1.7=Added option to give MR,PET,ADC,RT as input to plot the ADC,SUV values using an R Scatterplot'", shell=True)
        subprocess.call("minc_modify_header " + out + " -sinsert 'pyrtx2mnc:Version 1.8=Silenced printing to print use ---verbose'", shell=True)
        subprocess.call("minc_modify_header " + out + " -sinsert 'pyrtx2mnc:Version 2.0=The rtx2mnc is written anew in python instead. Gives increased contour accuracy'", shell=True)
    else:
        #print "Resampling files"
        subprocess.call("mincresample -clobber -nearest_neighbour " + res + " -like " + like + " " + out, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call("minc_modify_header " + out + " -sinsert 'pyrtx2mnc:Version 1.0=Added flood fill algorithm so the contour is now filled'", shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call("minc_modify_header " + out + " -sinsert 'pyrtx2mnc:Version 1.1=Added interpolation when drawing the rt contour'", shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call("minc_modify_header " + out + " -sinsert 'pyrtx2mnc:Version 1.2=Added support for more than 1 contour'", shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call("minc_modify_header " + out + " -sinsert 'pyrtx2mnc:Version 1.3=Added so you can execute directories of severel RT and scanning files at once'", shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call("minc_modify_header " + out + " -sinsert 'pyrtx2mnc:Version 1.4=Added version control in the minc header file'", shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call("minc_modify_header " + out + " -sinsert 'pyrtx2mnc:Version 1.5=Added a check so the script can now check if the rt matches a mnc file input'", shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call("minc_modify_header " + out + " -sinsert 'pyrtx2mnc:Version 1.6=Added more dummy checks and error handling'", shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call("minc_modify_header " + out + " -sinsert 'pyrtx2mnc:Version 1.7=Added option to give MR,PET,ADC,RT as input to plot the ADC,SUV values using an R Scatterplot'", shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call("minc_modify_header " + out + " -sinsert 'pyrtx2mnc:Version 2.0=The rtx2mnc is written anew in python instead. Gives increased contour accuracy'", shell=True, stdout=FNULL, stderr=subprocess.STDOUT)





#Given a output directory and the end of the dcm2mnc string it runs the dcm2mnc command
def dcm2mnc_dirscp(Directory, resamplestring, outdir, DateTime, tmp, argprint):
    #If not already present create directory
    if not os.path.exists(Directory):
        os.mkdir(Directory)
    #if the .mnc file does not already exist create
    if(argprint == True):
        if(os.path.isfile(outdir + "/" + DateTime + ".mnc") == False):
            subprocess.call("dcm2mnc -usecoordinates -dname '' -fname %D_%T " + cwd + "/" + resamplestring + " " + outdir, shell=True)
    else:
        if(os.path.isfile(outdir + "/" + DateTime + ".mnc") == False):
            print "Converting dicom to minc"
            subprocess.call("dcm2mnc -usecoordinates -dname '' -fname %D_%T " + cwd + "/" + resamplestring + " " + outdir, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
    #rename the .mnc file to our new name og studyuidrt + SeriesInstanceUID
    newname = outdir + "/" + tmp + ".mnc"
    oldname = outdir + "/" + DateTime + ".mnc"
    os.rename(oldname, newname)
    return newname

def rtx2mnc_dirscp(Directory, definedon, rtfile, outname, argprint):
    if not os.path.exists(Directory):
        os.mkdir(Directory)
    if(argprint == True):
        subprocess.call("pyrtx2mnc " + rtfile +  " " + definedon +  " " + Directory +  "/" + outname + " --verbose", shell=True)
    else:
        print "Converting rt file to .mnc"
        subprocess.call("pyrtx2mnc " + rtfile +  " " + definedon +  " " + Directory +  "/" + outname, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

#argscan is a mincfile, we check if the mincfiles studyuid matches with the rt file, if the case then run rtx2mnc
def verifymincfile_dirscp(argmr, StudyUIDRT, out, argRT, SeriesInsUID, argprint, argForceRT):
    #get studyuid from the mincfile using grep
    outtmp = str(commands.getstatusoutput('mincheader ' + argmr + ' |grep 000e')[1].split('"')[1::2][0])
    #Create new name for the files
    tmp = outtmp + "_" + SeriesInsUID + ".mnc"
    #If RT, MNC file matches:
    if StudyUIDRT == outtmp:
        print "\n file: ", argmr, "match with the rt file: ", argRT, "\n"
        rtx2mnc_dirscp(out, argmr, argRT, tmp, argprint)
        checkrtx2mnc(out +  "/" + tmp)
    #If they do not match and the force argument is given
    elif argForceRT == True:
        print "file: ", argmr, " does not match with the rt file: ", argRT, "Running anyways.. \n"
        rtx2mnc_dirscp(out, argmr, argRT, tmp, argprint)
        checkrtx2mnc(out +  "/" + tmp)
    #Neither case then:
    else:
        print "Error: RT file is not defined on input file \n Exiting..."
        sys.exit()
    return tmp

#Given a directory we enter the directory and picks a dicom file, which we fetch the StudyID from, and then
#compares it with the RT file for a match. Furthermore we take time and date for file name creation later.
def fetchStudyID_dirscp(fileTocheck, StudyUIDRT, SeriesInsUID, argForceRT, pet):
    #We fetch a single dicom file in order to get the tag to check with RT file later
    for filename in os.listdir(cwd + "/" + fileTocheck):
        if os.path.isdir(cwd + "/" + fileTocheck + "/" + filename):
            print "Error: No directories are allowed inside the directory input \n Exiting..."
            sys.exit()
        else:
            tmp = filename
        break
    # If we have MR argument check if the RT file match and turn mr.dcm files into mr.mnc

    ds1 = dicom.read_file(fileTocheck + "/" + tmp)
    if "SeriesInstanceUID" in ds1 and ds1[0x0020,0x000e].value == StudyUIDRT:
        DateTime = ds1[0x0008,0x0020].value + "_" + ds1[0x0008,0x0030].value[:-7]
        tmp = StudyUIDRT + "_" + SeriesInsUID
    elif("SeriesInstanceUID" in ds1 and argForceRT == True):
        print "Continuing even though RT and scan file is a mismatch \n"
        DateTime = ds1[0x0008,0x0020].value + "_" + ds1[0x0008,0x0030].value[:-7]
        tmp = StudyUIDRT + "_" + SeriesInsUID
    elif("SeriesInstanceUID" in ds1 and pet == True):
        DateTime = ds1[0x0008,0x0020].value + "_" + ds1[0x0008,0x0030].value[:-7]
        tmp = StudyUIDRT + "_" + SeriesInsUID
    else:
        print "Error: RT file is not defined on input file \n Exiting..."
        sys.exit()
    return tmp, DateTime
#check if the rtx2mnc command was successfull
def checkrtx2mnc_dirscp(Directory, filename):
    if os.path.isfile(Directory + "/" + filename) == True:
        return True
    else:
        return False
        print "Exiting.. Something went wrong in checkrtx2mnc_dirscp\n"
        sys.exit()

def handleInput_dirscp(tval, mr, rt, pet):
    tmp1 = False
    tmp2 = False
    if mr:
        if tval == True and os.path.isdir(mr):
            MRlist = dirRename(mr)
            tmp1 = True
        else:
            print "Error: The MR input is flawed, directory structure should be DirOfDicomDirs/DirectoryOfDicomFiles/file.dcm and rt file DirectoryOfRTFiles/rtss.dcm"
            print "Exiting..\n"
            sys.exit()
    if os.path.isdir(pet) and os.path.isdir(rt):
        PETliste = dirRename(pet)
        tmp2 = True
        RTlist = []
        #iterate over rt files in directory
        rtpath = cwd + "/" + rt + "/"
        for filename in os.listdir(rtpath):
            if os.path.isfile(rtpath + "/" + filename):
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
            else:
                print "Error: File: " + filename + " is not a file. \nThe directory structure is flawed\nThe directory structure should be DirOfDicomDirs/DirectoryOfDicomFiles/file.dcm and rt file DirectoryOfRTFiles/rtss.dcm\n"
                print "Exiting..\n"
                sys.exit()
    else:
        print "Error: The PET input is flawed, directory structure should be DirOfDicomDirs/DirectoryOfDicomFiles/file.dcm and rt file DirectoryOfRTFiles/rtss.dcm\n"
        print "Exiting..\n"
        sys.exit()
    if tmp1 == True and tmp2 == True:
        return MRlist, PETliste, RTlist
    elif tmp1 == False and tmp2 == True:
        return PETliste, RTlist


#-----------------------------------------------------------------------------------------------------#
#------------------------------------------- scatterplots.py -----------------------------------------#
#-----------------------------------------------------------------------------------------------------#


#for every file in re(resampled as input) directory we check if we have a file in deon, file1, file2, rtout that match
#if so we resample those files as the file found in re and places them in Resampled1,2,3,4 folders
def Resampling(re, deon, file1, file2, rtOut, Resampled1, Resampled2, Resampled3, Resampled4, argprint):
    ite = 0
    for filename in os.listdir(re):
        for filename1 in os.listdir(deon):
            if(filename == filename1):
                Resample_dirscp(Resampled1, deon + "/" + filename1, re + "/" + filename, Resampled1 + "/" + filename, argprint)
                ite += 1
                print "Resampling files: ", ite, "/", len(os.listdir(re))*4
        for filename1 in os.listdir(file1):
            if(filename == filename1):
                Resample_dirscp(Resampled2, file1 + "/" + filename1, re + "/" + filename, Resampled2 + "/" + filename, argprint)
                ite += 1
                print "Resampling files: ", ite, "/", len(os.listdir(re))*4
        for filename1 in os.listdir(file2):
            if(filename == filename1):
                Resample_dirscp(Resampled3, file2 + "/" + filename1, re + "/" + filename, Resampled3 + "/" + filename, argprint)
                ite += 1
                print "Resampling files: ", ite, "/", len(os.listdir(re))*4
        for filename1 in os.listdir(rtOut):
            if(filename == filename1):
                Resample_dirscp(Resampled4, rtOut + "/" + filename1, re + "/" + filename, Resampled4 + "/" + filename, argprint)
                ite += 1
                print "Resampling files: ", ite, "/", len(os.listdir(re))*4

def replace_withspace(string):
    for char in ['_']:
        if char in string:
            string=string.replace(char," ")
    return string
#Creates our outdirectory and runs rtx2mnc with the files in defondir and rtdir and places the files in outdir.
#For later use we also put the patientid(CPR) inside the mincheader
def rtx2mnc(DefOnDir, outDir, rtDir, argprint):

    Dir = cwd + "/" + DefOnDir
    outDir = cwd + "/" + outDir
    rtDir = cwd + "/" + rtDir
    ite = 0
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    for scan in os.listdir(Dir):
        for rt in os.listdir(rtDir):
            # try:
                withoutFileExtension = os.path.splitext(scan)[0]
                rtfile = rtDir + "/" + rt
                if(withoutFileExtension == rt):
                    ite += 1
                    DefinedOnFile = Dir + "/" + scan
                    outtmp = str(commands.getstatusoutput('mincheader ' + DefinedOnFile + ' |grep 0x0010:el_0x0020')[1].split('"')[1::2][0])
                    if(argprint == True):
                        subprocess.call("pyrtx2mnc " + rtfile +  " " + definedon + " " + outDir + "/" + rt + ".mnc" " --verbose", shell=True)
                        checkrtx2mnc(outDir + "/" + rt + ".mnc")
                        subprocess.call("minc_modify_header " + outDir + "/" + rt + ".mnc" + " -sinsert 'patientid:number=" + outtmp + "'", shell=True)
                    else:
                        subprocess.call("pyrtx2mnc " + rtfile +  " " + definedon + " " + outDir + "/" + rt + ".mnc", shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
                        checkrtx2mnc(outDir + "/" + rt + ".mnc")
                        subprocess.call("minc_modify_header " + outDir + "/" + rt + ".mnc" + " -sinsert 'patientid:number=" + outtmp + "'", shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
                    print "Converting rt file from DICOM to .minc: ", ite, "/", len(os.listdir(rtDir))


#Given a output directory and the end of the dcm2mnc string it runs the dcm2mnc command
def dcm2mnc(Directory, dcmdir, argprint, iterator):
    #If not already present create directory
    if not os.path.exists(Directory):
        os.mkdir(Directory)

    for filename in os.listdir(cwd + "/" + dcmdir):
        if(argprint == True):
            subprocess.call("dcm2mnc -usecoordinates -dname '' -fname %D_%T " + cwd + "/" + dcmdir + "/" + filename + " " + Directory, shell=True)
        else:
            iterator += 1
            print "Converting DICOM files to .mnc format: ", iterator, "/", len(os.listdir(cwd + "/" + dcmdir)) * 4
            subprocess.call("dcm2mnc -usecoordinates -dname '' -fname %D_%T " + cwd + "/" + dcmdir + "/" + filename + " " + Directory, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
    return iterator

#Takes as input a directory with mnc files and renames the files inside as the studyuidrt
def renameMNCtoStudyUID(arg, argprint):
    for filename in os.listdir(arg):
        try:
            #get studyuid tag from mnc file
            outtmp = str(commands.getstatusoutput('mincheader ' + arg + "/" + filename + ' |grep 000e')[1].split('"')[1::2][0])
            #rename the file as studyuid
            os.rename(arg + "/" + filename, arg + "/" + outtmp + ".mnc")
            if (checkforfile(arg, outtmp + ".mnc") == True):
                if(argprint == True):
                    print "Succesfully renamed ", arg + "/" + filename, "as ", arg + "/" + outtmp + ".mnc"
            else:
                print "Could not rename ", arg + "/" + filename, "as ", arg + "/" + outtmp + ".mnc"
        except:
            print "Error renaming definedonmr files as StudyUIDRT"


#Given a path we grep the mincheader command from terminal, fetching the patientid(cpr) and renames the files in the directory as patientid.mnc
#for rt files we created our own patientid number which we fetches with a special command if rt input is set to TRUE
def renamepatientid(path, rt):
    for filename in os.listdir(path):
        newpath = path + "/" + filename
        if(rt == True):
            outtmp = str(commands.getstatusoutput('mincheader ' + newpath + ' |grep patientid:number')[1].split('"')[1::2][0])
        else:
            outtmp = str(commands.getstatusoutput('mincheader ' + newpath + ' |grep 0x0010:el_0x0020')[1].split('"')[1::2][0])
        os.rename(newpath, path + "/" + outtmp + ".mnc")


#check if the file exists command was successfull
def checkforfile(Directory, filename):
    if os.path.isfile(Directory + "/" + filename) == True:
        return True
    else:
        return False
        print "Exiting..\n"
        sys.exit()


#DICOM
#Fetches the values we need to compute SUV and then calculates the value we need to divide pixel intensity with.
def getsuvvalues(filename):
    liste =[]
    for filename1 in os.listdir(filename):
        tmp = 0
        for filename2 in os.listdir(filename + "/" + filename1):
            path = filename + "/" + filename1 + "/" + filename2
            if magic.from_file(path) == "DICOM medical imaging data":
                #only run for one dicom file values identical in all files
                if(tmp == 0):
                    ds = dicom.read_file(path)
                    if "RadiopharmaceuticalInformationSequence" in ds:
                        #Fetch dicom information
                        dose = ds[0x0054,0x0016][0][0x0018,0x1074].value
                        halflife = ds[0x0054,0x0016][0][0x0018,0x1075].value
                        scantime = ds[0x0054,0x0016][0][0x0018,0x1072].value.split('.')[0]
                        weight = ds[0x0010,0x1030].value
                        acqtime = ds[0x0008,0x0032].value.split('.')[0]
                        patientID = ds[0x0010,0x0020].value
                        tmp = 1
                        #Convert to format 02:44 and substract
                        tdelta = datetime.strptime(acqtime, '%H%M%S') - datetime.strptime(scantime, '%H%M%S')
                        #convert to minutes so e.g 02:44 = 2.73
                        tdelta = tdelta.total_seconds()
                        #Calculate the value
                        value = (dose * (0.5)**(tdelta/(halflife*0.5)))/weight
                        liste.append(tuple((patientID, value)))

    return liste


#Converts a directory with .mnc files into nifti files and places them in outdir
def convertToNifti(directory, outdir, argprint):
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    for filename in os.listdir(directory):
        if not os.path.exists(directory + "/" + filename + ".nii"):
            name = filename.split('.')[0]
            if(argprint == True):
                subprocess.call("mnc2nii -nii " + directory + "/" + filename + " " + outdir + "/" + name, shell=True)
            else:
                subprocess.call("mnc2nii -nii " + directory + "/" + filename + " " + outdir + "/" + name, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)


#Enters the RT file and renames it as studyuidrt and moves it into the mncfiles/rt folder
def checkrt(Directory, rtliste, argrt, argprint):
    cwd = os.getcwd()
    #check if the mncfiles/rt directory exists if not create it
    if not os.path.exists(Directory):
        os.mkdir(Directory)

    for filename in rtliste:
        #Create a path of current working directory/rt argument/rtliste input
        path = cwd + "/" + argrt + "/" + filename + "/"
        for filename1 in os.listdir(path):
            if magic.from_file(path + filename1) == "DICOM medical imaging data":
                if(argprint == True):
                    print "Succesfully confirmed RT input as dicom"
                #StudyInstanceUID inside the contour sequence for RT
                ds = dicom.read_file(path + filename1)
                if ([0x3006,0x0010] in ds and [0x0020,0x00e] in ds):
                    StudyUIDRT = ds[0x3006,0x0010][0][0x3006,0x0012][0][0x3006,0x0014][0][0x0020,0x000e].value
                    SeriesInsUID = ds[0x0020,0x000e].value
                    os.rename(path + filename1,  path + StudyUIDRT)
                    copy2(path + StudyUIDRT, Directory)
                    os.rename(path, cwd + "/" + argrt + "/" + StudyUIDRT)

                else:
                    print "\nThe RT file have no contours\n exiting..."
                    sys.exit()
            else:
                print "\nError: The RT file is not Dicom format"


def bigplots(suv, mnc, niftiY, niftiX, niftiRT, dim, argtitle, argprint, outbig, outjoint):

    print "Creating the pool scatterplot..."
    subprocess.call("./Rscripts/bigscatterplot.R -a " + niftiY + " -p " + niftiX + " -r " + niftiRT + " -d " + suv + " -x " + str(dim) + " -t " + '"' + argtitle + '"' + " -o " + outbig, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
    print "Creating Joint Histogram"
    subprocess.call("./Rscripts/jointHisto.R -a " + niftiY + " -p " + niftiX + " -r " + niftiRT + " -d " + suv + " -x " + str(dim) + " -t " + '"' + argtitle + '"' + " -o " + outjoint, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
    if(argprint == True):
        print "SUV Values: ", suv
        print "./Rscripts/bigscatterplot.R -a " + niftiY + " -p " + niftiX + " -r " + niftiRT + " -d " + suv + " -x " + str(dim) + " -t " + '"' + argtitle + '"' + " -o " + outbig
        print "./Rscripts/jointHisto.R -a " + niftiY + " -p " + niftiX + " -r " + niftiRT + " -d " + suv + " -x " + str(dim) + " -t " + '"' + argtitle + '"' + " -o " + outjoint
def function_output(path, argprint, once, func_out):
    if(once == 0):
        entry = "|     CPR    |      Skewness      |      Kurtosis     |\n-----------------------------------------------------\n"
        with open(func_out, "w+") as f:
            f.write(entry)
    if(argprint == True):
        subprocess.call(path, shell=True)
    else:
        subprocess.call(path, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)






    #-----------------------------------------------------------------------------------------------------#
    #----------------------------------------------- XTRA ------------------------------------------------#
    #-----------------------------------------------------------------------------------------------------#


#MINC FILE
#Fetches the values we need to compute SUV and then calculates the value we need to divide pixel intensity with.
# def getsuvvalues(filename):
#     weight = float(commands.getstatusoutput('mincheader ' + filename + ' |grep -a patient:weight')[1].split(' ')[2].split('.')[0])
#     dos = float(commands.getstatusoutput('mincheader ' + filename + ' |grep acquisition:injection_dose')[1].split(' ')[2])
#     halflife = float(commands.getstatusoutput('mincheader ' + filename + ' |grep acquisition:radionuclide_halflife')[1].split(' ')[2])
#     acq_time = str(commands.getstatusoutput('mincheader ' + filename + ' |grep acquisition:acquisition_time')[1].split('"')[1::2][0].split('.')[0])
#     imagetime = str(commands.getstatusoutput('mincheader ' + filename + ' |grep acquisition:image_time')[1].split('"')[1::2][0].split('.')[0])
#     FMT = '%H%M%S'
#     #Convert to format 02:44 and substract
#     tdelta = datetime.strptime(imagetime, FMT) - datetime.strptime(acq_time, FMT)
#     #convert to float so e.g 02:44 = 2.73
#     tdelta = tdelta.total_seconds()/60
#     # print weight, dos, halflife, tdelta, value
#     #calculate D_cor/W_patient
#     halflife = halflife
#     #print (halflife)
#     # print halflife, tdelta
#     # print dos
#     print(halflife)
#     value = (dos*0.5**(tdelta/(halflife))) / weight
#     return value
    # print weight, dos, halflife, tdelta, value
