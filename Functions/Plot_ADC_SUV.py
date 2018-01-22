# coding=utf-8
import sys, os, shutil, dicom, magic, argparse, commands
import functions as f
import subprocess

#############################################################################################################
##### Rigshospitalet - Department of Clinical Physiology and Nuclear Medicine PET- and Cyclotron unit   #####
##### Author: Joachim Hansen                                                                            #####
##### Mail: Joachim.Pries.Hansen@regionh.dk                                                             #####
##### Phone: +45 60632283                                                                               #####
##### Supervisor: Flemming Littrup Andersen                                                             #####
#############################################################################################################

FNULL = open(os.devnull, 'w')

def main(argdeon, argrt, argyaxis, argxaxis, argre, argkeepmnc, argprint, argtotalscatter, dim, argtitle, argout):
    argtitle = f.replace_withspace(argtitle)
    #Tmpfoldernames
    if(argout):
        mnc = str(argout)
    else:
        mnc = "MNCfiles"
    deon = mnc + "/defmnc"
    file1 = mnc + "/yaxis"
    file2 = mnc + "/xaxis"
    re = mnc + "/resampledas"
    rt = mnc + "/rt"
    rtOut = mnc + "/RTOut"
    Resampled1 = mnc + "/Resampled_Defmnc"
    Resampled2 = mnc + "/Resampled_yaxis"
    Resampled3 = mnc + "/Resampled_xaxis"
    Resampled4 = mnc + "/Resampled_rt"
    niftiY = mnc + "/nifti_yaxis"
    niftiX = mnc + "/nifti_xaxis"
    niftiRT = mnc + "/nifti_rt"
    scatterpng = mnc + "/ScatterPlots_PNG"
    func_out = mnc + "/functions_table.txt"
    outbig = mnc + "/ScatterPlots_PNG/poolPlot.png"
    outjoint = mnc + "/ScatterPlots_PNG/"

    cwd = os.getcwd()
    #Erase the folders we wanna make
    os.system("rm -r -f " + mnc)

    #create outdir
    os.system("mkdir " + cwd + "/" + mnc)
    os.system("mkdir " + cwd + "/" + scatterpng)


    deflist = f.dirRename(argdeon)
    f.dirRename(argyaxis)
    f.dirRename(argxaxis)
    f.dirRename(argrt)
    f.dirRename(argre)
    rtlist = f.dirRename(argrt)


    iterator = f.dcm2mnc(deon, argdeon, argprint, 0)
    iterator = f.dcm2mnc(file1, argyaxis, argprint, iterator)
    iterator = f.dcm2mnc(file2, argxaxis, argprint, iterator)
    iterator = f.dcm2mnc(re, argre, argprint, iterator)


    f.checkrt(rt, rtlist, argrt, argprint)
    f.renameMNCtoStudyUID(cwd + "/" + deon, argprint)
    f.rtx2mnc(deon, rtOut, rt, argprint)
    print "Renaming files as patientID"
    f.renamepatientid(cwd + "/" + deon, False)
    f.renamepatientid(cwd + "/" + file1, False)
    f.renamepatientid(cwd + "/" + file2, False)
    f.renamepatientid(cwd + "/" + rtOut, True)
    f.renamepatientid(cwd + "/" + re, False)

    # os.system("rm -r -f " + rt)
    f.Resampling(re, deon, file1, file2, rtOut, Resampled1, Resampled2, Resampled3, Resampled4, argprint)
    print "Converting .minc to nifti format..."
    f.convertToNifti(Resampled2, niftiY, argprint)
    f.convertToNifti(Resampled3, niftiX, argprint)
    f.convertToNifti(Resampled4, niftiRT, argprint)

    print "Calculating SUV values..."
    liste = f.getsuvvalues(cwd + "/" + argxaxis)
    print "Creating scatterplots in R..."
    suv = ""
    once = 0
    for i in range(len(liste)):
        name = liste[i][0]
        value = liste[i][1]
        newpath = cwd + "/" + scatterpng + "/" + name
        print "Creating plot number: ", i+1, "/", len(liste)
        if(argprint == True):
            subprocess.call("./Rscripts/import.R -a " + niftiY + "/" + name + ".nii -p " + niftiX + "/" + name + ".nii -r " + niftiRT + "/" + name + ".nii -d " + str(value) + " -x " + str(dim) + " -t " + '"' + argtitle + '"' + " -n " + newpath + ".png", shell=True)

        else:
            subprocess.call("./Rscripts/import.R -a " + niftiY + "/" + name + ".nii -p " + niftiX + "/" + name + ".nii -r " + niftiRT + "/" + name + ".nii -d " + str(value) + " -x " + str(dim) + " -t " + '"' + argtitle + '"' + " -n " + newpath + ".png", shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        #Create a path to be executed and call the function_output with arguments so we create a file functions_table.txt that contains relevant function on files
        path = "./Rscripts/functions.R -p " + niftiX + "/" + name + ".nii -r " + niftiRT + "/" + name + ".nii -n " + func_out + " -c " + name
        f.function_output(path, argprint, once, func_out)
        once = 1

        if(argtotalscatter == True):
            #create suv valuestring for huge scatterplot
            suv += str(value) + ","

    suv = suv[:-1]
    if(argtotalscatter == True):
        f.bigplots(suv, mnc, niftiY, niftiX, niftiRT, dim, argtitle, argprint)
    if(argkeepmnc == False and argtotalscatter == False):
        os.system("rm -r -f " + deon + " " + file1 + " " + file2 + " " + re + " " + rt + " " + rtOut + " " + Resampled1 + " " + Resampled2 + " " + Resampled3 + " " + Resampled4 + " " + niftiX + " " +niftiY + " " + niftiRT)


if __name__ == "__main__":
    main()
