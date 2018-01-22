import os

# with is like your try .. finally block in this case
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

os.system("mkdir build && cd build")
os.system("cmake ..")
os.system("make && sudo make install")
