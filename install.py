import os, sys, shutil


with open('Functions/main.py', 'r') as file:
    # read a list of lines into data
    data = file.readlines()



# now change the 2nd line, note that you have to add a newline
cwd = os.getcwd()
tmp = cwd + "/" + "Functions"
data[4] = "sys.path.insert(0," + '"' + tmp + '"' + ")\n"

# and write everything back
with open('/usr/local/bin/universal', 'w') as file:
    file.writelines( data )

os.system("chmod +x /usr/local/bin/universal")
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

if(os.path.isdir("rtx2mnc/build")):
    shutil.rmtree("rtx2mnc/build")
os.system("mkdir rtx2mnc/build")
os.chdir(cwd + "/rtx2mnc/build")
os.system("cmake ..")
os.system("make && sudo make install")

print("Install finished\nTo use the command write 'universal' to get help write 'universal --help'")
