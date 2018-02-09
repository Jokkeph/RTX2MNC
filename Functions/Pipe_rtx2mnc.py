# coding=utf-8
import sys, os, shutil, dicom, magic, commands
import functions as f

#############################################################################################################
##### Rigshospitalet - Department of Clinical Physiology and Nuclear Medicine PET- and Cyclotron unit   #####
##### Author: Joachim Hansen                                                                            #####
##### Mail: Joachim.Pries.Hansen@regionh.dk                                                             #####
##### Phone: +45 60632283                                                                               #####
##### Supervisor: Flemming Littrup Andersen                                                             #####
#############################################################################################################

def main(argPET, argRT, argRevRes, argmr, argForceRT, argprint):
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
        print "\nError: The RT file is not Dicom format so no point in running\n exiting..."
        sys.exit()

    ###################################### End RT file check section #######################################

    ################################ Begin Case handling for 2 image inputs ################################
    #Check for MR argument
    if argmr:
        #If we get a directory of files we need to use f.dcm2mnc_dirscp before using f.rtx2mnc_dirscp
        if os.path.isdir(argmr) and os.path.isdir(argPET):
            tmp, DateTime = f.fetchStudyID_dirscp(argmr, StudyUIDRT, SeriesInsUID, argForceRT, False)
            newname = f.dcm2mnc_dirscp(MR, argmr, MR, DateTime, tmp, argprint)
            newname1 = f.dcm2mnc_dirscp(PET, argPET, PET, DateTime, tmp, argprint)
            f.rtx2mnc_dirscp(RT, newname, argRT, tmp + ".mnc", argprint)
            f.checkrtx2mnc(RT +  "/" + tmp + ".mnc")

            #Resamples, the flag --RevRes choses which direction it ersamples
            if argRevRes == False and f.checkrtx2mnc_dirscp(RT, tmp + ".mnc") == True:
                #Terminal command mincresample -nearest_neighbour OutRT/20150602_113952.mnc -like PETmnc/20150602_113952.mnc out_resamp.mnc
                f.Resample_dirscp(RTOut, RT + "/" + tmp + ".mnc", newname1, " " + RTOut + "/" + tmp + ".mnc", argprint)
            elif f.checkrtx2mnc_dirscp(RT, tmp + ".mnc") == True:
                f.Resample_dirscp(RTOut, RT + "/" + tmp + ".mnc", newname1, " " + RTOut + "/" + tmp + ".mnc", argprint)

        #Case of f.Resample_dirscp file input being a mnc file
        elif os.path.isdir(argmr) and argPET.endswith('.mnc'):
            tmp, DateTime = f.fetchStudyID_dirscp(argmr, StudyUIDRT, SeriesInsUID, argForceRT, False)
            print tmp, DateTime
            #Change mr.dcm files into mr.mnc and run f.rtx2mnc_dirscp
            newname = f.dcm2mnc_dirscp(MR, argmr, MR, DateTime, tmp, argprint)
            f.rtx2mnc_dirscp(RT, newname, argRT, tmp + ".mnc", argprint)
            f.checkrtx2mnc(RT +  "/" + tmp + ".mnc")
            #Resamples, the flag --RevRes choses which direction it ersamples
            if argRevRes == False and f.checkrtx2mnc_dirscp(RT, tmp + ".mnc") == True:
                #Terminal command mincresample -nearest_neighbour OutRT/20150602_113952.mnc -like PETmnc/20150602_113952.mnc out_resamp.mnc
                f.Resample_dirscp(RTOut, RT + "/" + tmp + ".mnc", argPET + " ", RTOut + "/" + tmp + ".mnc", argprint)
            elif f.checkrtx2mnc_dirscp(RT, tmp + ".mnc") == True:
                f.Resample_dirscp(RTOut, argPET, RT + "/" + tmp + ".mnc ", RTOut + "/" + tmp + ".mnc", argprint)
        #Case of mr being mnc and pet being dir
        #
        elif os.path.isdir(argPET) and argmr.endswith('.mnc'):
            outtmp = f.verifymincfile_dirscp(argmr, StudyUIDRT, RT, argRT, SeriesInsUID, argprint, argForceRT)

            tmp, DateTime = f.fetchStudyID_dirscp(argPET, StudyUIDRT, SeriesInsUID, argForceRT, True)

            #Change mr.dcm files into mr.mnc and run f.rtx2mnc_dirscp
            newname = f.dcm2mnc_dirscp(PET, argPET, PET, DateTime, tmp, argprint)

            #Resamples, the flag --RevRes choses which direction it ersamples
            if argRevRes == False and f.checkrtx2mnc_dirscp(RT, outtmp) == True:
                #Terminal command mincresample -nearest_neighbour OutRT/20150602_113952.mnc -like PETmnc/20150602_113952.mnc out_resamp.mnc
                f.Resample_dirscp(RTOut, RT + "/" + outtmp, newname + " ", RTOut + "/" + tmp + ".mnc", argprint)
            elif f.checkrtx2mnc_dirscp(RT, tmp + ".mnc") == True:
                f.Resample_dirscp(RTOut, newname, RT + "/" + tmp + ".mnc ", RTOut + "/" + tmp + ".mnc", argprint)

        #Case of both input files being mnc already
        elif argPET.endswith('.mnc') and argmr.endswith('.mnc'):
            outtmp = f.verifymincfile_dirscp(argmr, StudyUIDRT, RT, argRT, SeriesInsUID, argprint, argForceRT)

            if argRevRes == False and f.checkrtx2mnc_dirscp(RT, outtmp) == True:
               #Terminal command mincresample -nearest_neighbour OutRT/20150602_113952.mnc -like PETmnc/20150602_113952.mnc out_resamp.mnc
               f.Resample_dirscp(RTOut, RT + "/" + outtmp, argPET + " ", RTOut + "/" + outtmp, argprint)
            elif f.checkrtx2mnc_dirscp(RT, "out_label.mnc") == True:
               f.Resample_dirscp(RTOut, argPET, RT + "/" + outtmp, RTOut + "/" + outtmp, argprint)
        else:
            print "Error: One of the input file either MR or PET is not minc or a directory"
            print "Exiting..\n"
            sys.exit()

    ################################ End Case handling for 2 image inputs ################################
#pdftoppm -png 0608510370.pdf  out

    ################################ Begin Case handling for 1 image input ###############################
    else:
        #if the path is a directory we need to get some values from the dicom files inside
        if os.path.isdir(argPET):
            #Fetch some dicom tags and rename the file to the tmp value.
            tmp, DateTime = f.fetchStudyID_dirscp(argPET, StudyUIDRT, SeriesInsUID, argForceRT, False)
            newname = f.dcm2mnc_dirscp(PET, argPET, PET, DateTime, tmp, argprint)
            f.rtx2mnc_dirscp(RT, newname, argRT, tmp + ".mnc", argprint)
            f.checkrtx2mnc(RT +  "/" + tmp + ".mnc")
            #Resamples, the flag --RevRes choses which direction it ersamples
            if argRevRes == False and f.checkrtx2mnc_dirscp(RT, tmp + ".mnc") == True:
                #Terminal command mincresample -nearest_neighbour OutRT/20150602_113952.mnc -like PETmnc/20150602_113952.mnc out_resamp.mnc
                f.Resample_dirscp(RTOut, RT + "/" + tmp + ".mnc" , newname + " ", RTOut + "/" + tmp + ".mnc", argprint)
            elif f.checkrtx2mnc_dirscp(RT, tmp + ".mnc") == True:
                f.Resample_dirscp(RTOut, newname, RT + "/" + tmp + ".mnc ", RTOut + "/" + tmp + ".mnc", argprint)

        elif argPET.endswith('.mnc'):
            #Fetch some dicom tags and rename the file to the tmp value.
            outtmp = f.verifymincfile_dirscp(argPET, StudyUIDRT, RT, argRT, SeriesInsUID, argprint, argForceRT)
            #Resamples, the flag --RevRes choses which direction it ersamples
            print "Test", outtmp + ".mnc"
            if argRevRes == False and f.checkrtx2mnc_dirscp(RT,  outtmp) == True:
                #Terminal command mincresample -nearest_neighbour OutRT/20150602_113952.mnc -like PETmnc/20150602_113952.mnc out_resamp.mnc
                f.Resample_dirscp(RTOut, RT + "/" + outtmp, argPET + " ", RTOut + "/" + outtmp, argprint)
            elif f.checkrtx2mnc_dirscp(RT, outtmp + ".mnc") == True:
                f.Resample_dirscp(RTOut, argPET, RT + "/" + outtmp + " ", RTOut + "/" + outtmp, argprint)
        else:
            print "Error: The PET argument is neither a directory nor a .mnc file"
            print "Exiting..\n"
            sys.exit()





    ################################### End handling for 1 image input #################################

if __name__ == "__main__":
    main()
