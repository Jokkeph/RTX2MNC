# coding=utf-8
import sys, os, shutil, dicom, magic, argparse, commands

######################################### Begin Argparse section #########################################
# parser = argparse.ArgumentParser()
# parser.add_argument("--RevRes", help="Reverses the resample so the PET is resampled as the RT, file saved the same place", action="store_true")
# parser.add_argument("--twoinput", help="Optional Input directory of Dicom files or a single mnc file, the second input file will be resampled upon this file")
# parser.add_argument("PET", help="Input directory of Dicom files or a single mnc file")
# parser.add_argument("RT", help="Input RT file")
# parser.add_argument("--ForceRT", help="Forces the program to run even though the RT file and input scanning file does not match", action="store_true")
# args = parser.parse_args()
######################################### End Argparse section ###########################################
def main(argPET, argRT, argRevRes, argmr, argForceRT):
    ############################################ Function section ############################################
    #Given a output directory and the remainder of the mincresample command it runs the mincresample command
    def Resample(Directory, res, like, out):
        if not os.path.exists(Directory):
            os.mkdir(Directory)
        #Terminal command mincresample -nearest_neighbour OutRT/20150602_113952.mnc -like PETmnc/20150602_113952.mnc out_resamp.mnc
        os.system("mincresample -clobber -nearest_neighbour " + res + " -like " + like + out)
        print "\nResampling file: ", res,
        print "\nLike file: ", like
        print "\nThe Resampled file is located in folder: " + cwd + "/" + RTOut + "/"
        print "\nWriting version control into mincheader(current version: 1.6)"
        os.system("minc_modify_header " + out + " -sinsert 'rtx2mnc:Version 1.0=Added flood fill algorithm so the contour is now filled'")
        os.system("minc_modify_header " + out + " -sinsert 'rtx2mnc:Version 1.1=Added interpolation when drawing the rt contour'")
        os.system("minc_modify_header " + out + " -sinsert 'rtx2mnc:Version 1.2=Added support for more than 1 contour'")
        os.system("minc_modify_header " + out + " -sinsert 'rtx2mnc:Version 1.3=Added so you can execute directories of severel RT and scanning files at once'")
        os.system("minc_modify_header " + out + " -sinsert 'rtx2mnc:Version 1.4=Added version control in the minc header file'")
        os.system("minc_modify_header " + out + " -sinsert 'rtx2mnc:Version 1.5=Added a check so the script can now check if the rt matches a mnc file input'")
        os.system("minc_modify_header " + out + " -sinsert 'rtx2mnc:Version 1.6=Added more dummy checks and error handling'")
        print "\nFinished pipescript.py and directoryscript.py"
    #Given a output directory, an rt file, and output name and the mnc file which the RT is defined on, it runs the global rtx2mnc command.
    def rtx2mnc(Directory, definedon, rtfile, outname):
        if not os.path.exists(Directory):
            os.mkdir(Directory)
        os.system("rtx2mnc " + definedon +  " " + rtfile +  " " + Directory +  "/" + outname)
    #Given a output directory and the end of the dcm2mnc string it runs the dcm2mnc command
    def dcm2mnc(Directory, resamplestring, outdir):
        #If not already present create directory
        if not os.path.exists(Directory):
            os.mkdir(Directory)
        #if the .mnc file does not already exist create
        if(os.path.isfile(outdir + "/" + DateTime + ".mnc") == False):
            os.system("dcm2mnc -usecoordinates -dname '' -fname %D_%T " + cwd + "/" + resamplestring + " " + outdir)
        #rename the .mnc file to our new name og studyuidrt + SeriesInstanceUID
        newname = outdir + "/" + tmp + ".mnc"
        oldname = outdir + "/" + DateTime + ".mnc"
        os.rename(oldname, newname)
        return newname
    #argscan is a mincfile, we check if the mincfiles studyuid matches with the rt file, if the case then run rtx2mnc
    def verifymincfile(argscan):
        #get studyuid from the mincfile using grep
        outtmp = str(commands.getstatusoutput('mincheader ' + argscan + ' |grep 000e')[1].split('"')[1::2][0])
        #Create new name for the files
        tmp = outtmp + "_" + SeriesInsUID + ".mnc"
        #If RT, MNC file matches:
        if StudyUIDRT == outtmp:
            print "\n file: ", argscan, "match with the rt file: ", argRT, "\n"
            rtx2mnc(RT, argscan, argRT, tmp)
        #If they do not match and the force argument is given
        elif argForceRT == True:
            print "file: ", argscan, " does not match with the rt file: ", argRT, "Running anyways.. \n"
            outtmp = outtmp + ".mnc"
            rtx2mnc(RT, argscan, argRT, tmp)
        #Neither case then:
        else:
            print "Error: RT file is not defined on input file \n Exiting..."
            sys.exit()
        return tmp

    #Given a directory we enter the directory and picks a dicom file, which we fetch the StudyID from, and then compaers it with the RT file for a match. Furthermore we take time and date for file name creation later.
    def fetchStudyID(fileTocheck):
        #We fetch a single dicom file in order to get the tag to check with RT file later
        for filename in os.listdir(cwd + "/" + fileTocheck):
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
        else:
            print "Error: RT file is not defined on input file \n Exiting..."
            sys.exit()
        return tmp, DateTime
    #check if the rtx2mnc command was successfull
    def checkrtx2mnc(Directory, filename):
        if os.path.isfile(Directory + "/" + filename) == True:
            return True
        else:
            return False
            print "Exiting..\n"
            sys.exit()



    ########################################## End function section ##########################################

    ####################################### Begin value setting section ######################################
    #Tmpfoldernames
    PET = "PETmnc"
    MR = "MRmnc"
    RT = "RT"
    RTOut = "Resampled"
    #Get Current dir
    cwd = os.getcwd()
    ####################################### End value setting section ########################################

    ####################################### Begin check if input exists ######################################
    #Check if the path exists first
    if os.path.exists(cwd + "/" + argPET) == False:
        print "\nPET path argument does not exist\n Exiting.."
        sys.exit()
    if os.path.exists(cwd + "/" + argRT) == False:
        print "\nRT path argument does not exist\n Exiting.."
        sys.exit()
    if argmr:
        if os.path.exists(cwd + "/" + argmr) == False:
            print "\nMR path argument does not exist\n Exiting.."
            sys.exit()

    ####################################### End check if input exists ########################################

    ###################################### Begin RT file check section #######################################
    #Check if RT file is in Dicom format
    if magic.from_file(argRT) == "DICOM medical imaging data":
        print "\n Succesfully confirmed RT input as dicom"
        #StudyInstanceUID inside the contour sequence for RT
        ds = dicom.read_file(argRT)
        if ([0x3006,0x0010] in ds and [0x0020,0x00e] in ds):
            StudyUIDRT = ds[0x3006,0x0010][0][0x3006,0x0012][0][0x3006,0x0014][0][0x0020,0x000e].value
            SeriesInsUID = ds[0x0020,0x000e].value
        else:
            print "\nThe RT file have no contours\n exiting..."
            sys.exit()
    else:
        print "\nError: The RT file is not Dicom format"

    ###################################### End RT file check section #######################################

    ################################ Begin Case handling for 2 image inputs ################################
    #Check for MR argument
    if argmr:
        #If we get a directory of files we need to use dcm2mnc before using rtx2mnc
        if os.path.isdir(argmr) and os.path.isdir(argPET):
            DateTime = fetchStudyID(argmr)[1]
            tmp = fetchStudyID(argmr)[0]
            newname = dcm2mnc(MR, argmr, MR)
            newname1 = dcm2mnc(PET, argPET, PET)
            rtx2mnc(RT, newname, argRT, tmp + ".mnc")

            #Resamples, the flag --RevRes choses which direction it ersamples
            if argRevRes == False and checkrtx2mnc(RT, tmp + ".mnc") == True:
                #Terminal command mincresample -nearest_neighbour OutRT/20150602_113952.mnc -like PETmnc/20150602_113952.mnc out_resamp.mnc
                Resample(RTOut, RT + "/" + tmp + ".mnc", newname1, " " + RTOut + "/" + tmp + ".mnc")
            elif checkrtx2mnc(RT, tmp + ".mnc") == True:
                Resample(RTOut, RT + "/" + tmp + ".mnc", newname1, " " + RTOut + "/" + tmp + ".mnc")

        #Case of Resample file input being a mnc file
        elif os.path.isdir(argmr) and argPET.endswith('.mnc'):
            DateTime = fetchStudyID(argPET)[1]
            tmp = fetchStudyID(argmr)[0]
            #Change mr.dcm files into mr.mnc and run rtx2mnc
            newname = dcm2mnc(MR, argmr, MR)
            rtx2mnc(RT, newname, argRT, tmp + ".mnc")
            #Resamples, the flag --RevRes choses which direction it ersamples
            if argRevRes == False and checkrtx2mnc(RT, tmp + ".mnc") == True:
                #Terminal command mincresample -nearest_neighbour OutRT/20150602_113952.mnc -like PETmnc/20150602_113952.mnc out_resamp.mnc
                Resample(RTOut, RT + "/" + tmp + ".mnc", argPET + " ", RTOut + "/" + tmp + ".mnc")
            elif checkrtx2mnc(RT, tmp + ".mnc") == True:
                Resample(RTOut, argPET, RT + "/" + tmp + ".mnc ", RTOut + "/" + tmp + ".mnc")

        #Case of both input files being mnc already
        elif argPET.endswith('.mnc') and argmr.endswith('.mnc'):
            outtmp = verifymincfile(argmr)
            if argRevRes == False and checkrtx2mnc(RT, outtmp) == True:
               #Terminal command mincresample -nearest_neighbour OutRT/20150602_113952.mnc -like PETmnc/20150602_113952.mnc out_resamp.mnc
               Resample(RTOut, RT + "/" + outtmp, argPET + " ", RTOut + "/" + outtmp)
            elif checkrtx2mnc(RT, "out_label.mnc") == True:
               Resample(RTOut, argPET, RT + "/" + outtmp, RTOut + "/" + outtmp)

    ################################ End Case handling for 2 image inputs ################################

    ################################ Begin Case handling for 1 image input ###############################
    else:
        #if the path is a directory we need to get some values from the dicom files inside
        if os.path.isdir(argPET):
            #Fetch some dicom tags and rename the file to the tmp value.
            DateTime = fetchStudyID(argPET)[1]
            tmp = fetchStudyID(argPET)[0]
            newname = dcm2mnc(PET, argPET, PET)
            rtx2mnc(RT, newname, argRT, tmp + ".mnc")
            #Resamples, the flag --RevRes choses which direction it ersamples
            if argRevRes == False and checkrtx2mnc(RT, tmp + ".mnc") == True:
                #Terminal command mincresample -nearest_neighbour OutRT/20150602_113952.mnc -like PETmnc/20150602_113952.mnc out_resamp.mnc
                Resample(RTOut, RT + "/" + tmp + ".mnc" , newname + " ", RTOut + "/" + tmp + ".mnc")
            elif checkrtx2mnc(RT, tmp + ".mnc") == True:
                Resample(RTOut, newname, RT + "/" + tmp + ".mnc ", RTOut + "/" + tmp + ".mnc")

        elif argPET.endswith('.mnc'):
            #Fetch some dicom tags and rename the file to the tmp value.
            outtmp = verifymincfile(argPET)
            #Resamples, the flag --RevRes choses which direction it ersamples
            if argRevRes == False and checkrtx2mnc(RT,  outtmp) == True:
                #Terminal command mincresample -nearest_neighbour OutRT/20150602_113952.mnc -like PETmnc/20150602_113952.mnc out_resamp.mnc
                Resample(RTOut, RT + "/" + outtmp, argPET + " ", RTOut + "/" + outtmp)
            elif checkrtx2mnc(RT, tmp + ".mnc") == True:
                Resample(RTOut, argPET, RT + "/" + outtmp + " ", RTOut + "/" + outtmp)




# os.system("mincresample -nearest_neighbour " + res + " -like " + like + out)
# os.system("minc_modify_header" + RTOut +  -sinsert 'Version:rtx2mnc=Version 1.1'")
# minc_modify_header Resampled/1.3.12.2.1107.5.1.4.99999.145978957753602_1.2.826.0.1.3680043.8.691.4.3362979749402.8770.1462446297981.227.mnc -sinsert 'Version:rtx2mnc=Version 1.1'

# mincheader Resampled/1.3.12.2.1107.5.1.4.99999.145978957753602_1.2.826.0.1.3680043.8.691.4.3362979749402.8770.1462446297981.227.mnc
    ################################### End handling for 1 image input #################################


    ####################################### Begin Cleanup section ######################################

    ####################################### End Cleanup section ########################################
if __name__ == "__main__":
    main()
