## Authors
Rigshospitalet - Klinik for Klinisk Fysiologi og Nuklearmedicin PET- og Cyklotronenheden
  - Joachim Hansen <joachim.pries.hansen@regionh.dk>

> Build upon Claes Ladefoged's repository https://github.com/claesnl/rtx2mnc

# rtxtool

Can convert RT structures from MIRADA in dicom format to a filled MINC label.
Can take directories of DICOM files aswell as single files as input.
Can also combine PNG files and create ADC(y), PET(x) point/histogram plots for directories of dicom files.

#

## Installation:
<pre><code>
# Install the dependencies (if needed see below)
# Run the install file if there are errors see manual install below
sudo python install.py
</code></pre>
The program is installed at /usr/local/bin as default.

## Usage:
<pre><code>
rtxtool < flags > < DICOM file > < RT file >
</code></pre>


##Flags(see --help for details)
-h, --help       show this help message and exit
-defon DEFON     Directory of directories containing dicom files, must be
                 the ones that the RT is defined on or no output
-yaxis YAXIS     Directory of directories containing dicom files,
-xaxis XAXIS     Directory of directories containing dicom files,
-rt RT           The directory containing rt directory/files
-re RE           The file the other files will be resampled as
-out OUT         Output directory
--revres         Reverses the resample so the PET is resampled as the RT
--mr MR          Input directory of Dicom files or a single mnc file, the
                 second input file will be resampled upon this file
--pet PET        Input directory of Dicom files or a single mnc file
--forcert        Forces the program to run even though the RT file and input
                 file does not match
--auto           Allow the input of directories, the scanning files should
                 be inside a directory etc. dir/dicom/file.dcm and rt file
                 rt/rtss.dcm
--rts RTS        Input rt file
---keepmnc       Keeps the intermediary files that are created during
                 runtime, e.g .nifti, .mnc, resampled.mnc,
                 beforeresampled.mnc
---verbose       Prints additional information of the programs progress
---totalscatter  Creates one big scatterplot with all the scans
---xdim XDIM     Scatterplot length of xaxis
---title TITLE   Title of the scatterplots
-p1 P1           Directory containing PNG's
-p2 P2           Directory containing PNG's
-p3 P3           Directory containing PNG's
-p4 P4           Directory containing PNG's
-pout POUT       Defines output directory of combined PNG's


## Requires/Dependencies:
 - MINC tools
 - DCMTK

## Manual install Dependencies
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
