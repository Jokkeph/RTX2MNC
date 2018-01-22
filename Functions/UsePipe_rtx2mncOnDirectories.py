# coding=utf-8
import Pipe_rtx2mnc
import sys, os, shutil, dicom, magic
import functions as f

#############################################################################################################
##### Rigshospitalet - Department of Clinical Physiology and Nuclear Medicine PET- and Cyclotron unit   #####
##### Author: Joachim Hansen                                                                            #####
##### Mail: Joachim.Pries.Hansen@regionh.dk                                                             #####
##### Phone: +45 60632283                                                                               #####
##### Supervisor: Flemming Littrup Andersen                                                             #####
#############################################################################################################

def main(argmr, argpet, argrt, argrevres, argforcert, argauto, argkeepmnc, argprint):
    #Tmpfoldernames
    PET = "PETmnc"
    MR = "MRmnc"
    RT = "RT"
    RTOut = "Resampled"
    cwd = os.getcwd()
    #Erase the folders we wanna make
    os.system("rm -r -f " + PET + " " + MR + " " + RT)

    #Check if all three args are directories
    if argauto == True and argmr:
        MRlist = f.handleInput_dirscp(True, argmr, argrt, argpet)[0]
        PETlist = f.handleInput_dirscp(True, argmr, argrt, argpet)[1]
        RTlist = f.handleInput_dirscp(True, argmr, argrt, argpet)[2]
        #call the Pipe_rtx2mnc on the different files
        for i in range(0,len(MRlist)):
            for k in range(0,len(RTlist)):
                rest = RTlist[k].split('_', 1)[0].split(argrt + "/", 1)[1]
                rtlistpath = RTlist[k].split(argrt + "/", 1)[1]
                if (MRlist[i] == rest):
                    Pipe_rtx2mnc.main(argpet + "/" + PETlist[i], argrt + "/" + rtlistpath, argrevres, argmr + "/" + MRlist[i], argforcert, argprint)


    #Check if both arguments are directories
    elif argauto == True:
        PETlist = f.handleInput_dirscp(False, argmr, argrt, argpet)[0]
        RTlist = f.handleInput_dirscp(False, argmr, argrt, argpet)[1]
        #call the Pipe_rtx2mnc on the different files
        for i in range(0,len(PETlist)):
            for k in range(0,len(RTlist)):
                rest = RTlist[k].split('_', 1)[0].split(argrt + "/", 1)[1]
                rtlistpath = RTlist[k].split(argrt + "/", 1)[1]
                if (PETlist[i] == rest):
                    Pipe_rtx2mnc.main(argpet + "/" + PETlist[i], argrt + "/" + rtlistpath, argrevres, argmr, argforcert, argprint)


    else:
        if os.path.isdir(argrt) == False:
            Pipe_rtx2mnc.main(argpet, argrt, argrevres, argmr, argforcert, argprint)# do whatever is in Pipe_rtx2mnc
        else:
            print "RT input is a directory please consider using the --Auto option or change the input"

    #Erase the folders we used in the process
    if argkeepmnc == False:
        os.system("rm -r -f " + PET + " " + MR + " " + RT)

if __name__ == "__main__":
    main()
