import os, sys, shutil
#Name of the command to write in terminal
commandname = 'rtxtool'

def addexecutable(text):
    try:
        with open('Functions/main.py', 'r') as file:
            # read a list of lines into data
            data = file.readlines()

        #Copy rtx2mnc to the executable location
        os.system("cp Functions/rtx2mnc.py " + text + "/pyrtx2mnc")
        #Path to command
        path = text + "/" + commandname
        #Change the path to the Functions folder so we can import from it
        data[4] = "sys.path.insert(0," + '"' + os.getcwd() + "/" + "Functions" + '"' + ")\n"
        #Write the line to the file.
        with open(path, 'w') as file:
            file.writelines( data )


        #Give execution right to pyrtx2mnc and rtxtool
        os.system("chmod +x  " + text + "/pyrtx2mnc")
        os.system("chmod +x " + path)
    except:
        print "I can't place the file at that path Exiting..."
        sys.exit()

#Should probably filter some input here to make the program more secure and error prone
if os.path.isdir("/opt/bin"):
    text = raw_input("I detect the path of bin in /opt/bin Can i place the executable command here?(y/n)\n")
    if(text == "y" or text == "Y"):
        addexecutable("/opt/bin")
    else:
        # text = raw_input("I can't find the bin folder for executable files where can i put rtxtool? Format e.g. /usr/local/bin")
        text = raw_input("Then where can i put the executable? Format are e.g. /usr/local/bin\n")
        if text:
            addexecutable(text)

elif os.path.isdir("/usr/local/bin"):
    text = raw_input("I detect the path of bin in /usr/local/bin Can i place the executable command here?(y/n)\n")
    if(text == "y" or text == "Y"):
        print "hej"
        addexecutable("/usr/local/bin")
    else:
        # text = raw_input("I can't find the bin folder for executable files where can i put rtxtool? Format e.g. /usr/local/bin")
        text = raw_input("Then where can i put the executable? Format are e.g. /usr/local/bin\n")
        if text:
            addexecutable(text)
else:
    text = raw_input("I can't find the bin folder for executable files where can i put rtxtool? Format e.g. /usr/local/bin\n")
    if text:
        addexecutable(text)



# now change the 2nd line, note that you have to add a newline






text = raw_input("Should i install the newest version of DCMTK?(y/n)Takes a while(20 min+)\n")  # Python 2
if(text == "y" or text == "Y"):
    os.system("git clone https://github.com/DCMTK/dcmtk")
    os.system("./dcmtk/configure")
    os.system("make all")
    os.system("sudo make install-all")

text = raw_input("Should i install MINC toolkit 1.9.16 from 20170529?(y/n)Takes around 5-10 min\n")
if(text == "y" or text == "Y"):
    os.system("wget http://packages.bic.mni.mcgill.ca/minc-toolkit/Debian/minc-toolkit-1.9.16-20170529-Ubuntu_16.04-x86_64.deb")
    os.system("echo 'export PATH=$PATH:/opt/minc/bin' >> ~/.bash_profile")
    os.system("echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/minc/lib' >> ~/.bash_profile")
    os.system("source ~/.bash_profile")
    os.remove("minc-toolkit-1.9.16-20170529-Ubuntu_16.04-x86_64.deb")


# if(os.path.isdir("rtx2mnc/build")):
#     shutil.rmtree("rtx2mnc/build")
# os.system("mkdir rtx2mnc/build")
# os.chdir(cwd + "/rtx2mnc/build")
# os.system("cmake ..")
# os.system("make && make install")

print("Install finished\nTo use the command write '" + commandname + "' to get help write '" + commandname + " --help'")
