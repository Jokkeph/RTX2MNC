## Authors
Rigshospitalet - Klinik for Klinisk Fysiologi og Nuklearmedicin PET- og Cyklotronenheden 
  - Joachim Hansen <joachim.pries.hansen@regionh.dk>
  
> Build upon Claes Ladefoged's repository https://github.com/claesnl/rtx2mnc

# RTX2MNC  

Converts a RT-structure from MIRADA to a MNC label file with the filled contours set to 1. 
The program takes as input the volume file used to create the RTx struct, e.g. a PET image, in MNC format as well. The output label file will match the input volumes image dimensions.

## Installation:
<pre><code>
# Install the dependencies
# cd to project folder
mkdir build && cd build
cmake ..
make && sudo make install
</code></pre>
The program is installed at /usr/local/bin as default.

## Usage:
<pre><code>
rtx2mnc < VOLUME.mnc > < RTx > < out_label.mnc >
      	
      	< VOLUME.mnc > is the file which the RTx was defined on.
      	< RTx > is the RT struct in DICOM format.
      	< out_label.mnc > is the resulting MINC file with the contours in the RT file set to 1.
</code></pre>

## Requires/Dependencies:
 - MINC tools
 - DCMTK

## Installing Dependencies
### DCMTK
<pre><code>
git clone https://github.com/commontk/DCMTK.git
cd DCMTK
./configure
make all
sudo make install-all
</code></pre>
### Minc
<pre><code>
wget http://packages.bic.mni.mcgill.ca/minc-toolkit/RPM/minc-toolkit-1.0.08-20160205-CentOS_6.7-x86_64.rpm
sudo rpm -Uvh minc-toolkit-1.0.08-20160205-CentOS_6.7-x86_64.rpm

echo 'export PATH=$PATH:/opt/minc/bin' >> ~/.bash_profile
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/minc/lib' >> ~/.bash_profile
echo 'export PERL5LIB=$PERL5LIB:/opt/minc/perl' >> ~/.bash_profile
source ~/.bash_profile
</code></pre>
## Troubleshooting
If you run into library problems during the 
<pre><code>cmake ..</code></pre> 
command then run 
<pre><code>ccmake ..
t</code></pre> 
Now scroll down to either DCMTK_DIR and set the right path(/usr/DCMTK) or scroll down to MIND_INCLUDE_DIR(/opt/minc/include) and  MINC_minc3_LIBRARY(/opt/minc/lib/libminc2.so) and set the right path for the files. My path is the one in parentheses.
When finished press:
<pre><code>
c
g
</code></pre>
## Error loading shared libraries

<pre><code>

Error: rtx2mnc: error while loading shared libraries: libminc2.so.5.0.1: cannot open shared object file: No such file or directory
</code></pre>

Solution:
(1 ) Find where the library is placed if you don't know it.
<pre><code>
cd /
sudo find ./ | grep the_name_of_the_file.so
</code></pre>
(2) Check for the existence of the dynamic library path environnement variable(LD_LIBRARY_PATH)
<pre><code>
echo $LD_LIBRARY_PATH
</code></pre>
if there is nothing to be display we need to add the default path value
<pre><code>
LD_LIBRARY_PATH=/usr/local/lib
</code></pre>
(3) We now add the desire path and export it and try the application
<pre><code>
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/my_library/path.so.something
export LD_LIBRARY_PATH
</code></pre>
In my case the commands were
<pre><code>
LD_LIBRARY_PATH=/opt/minc/lib/
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/minc/lib/libminc2.so
export LD_LIBRARY_PATH
</code></pre>
