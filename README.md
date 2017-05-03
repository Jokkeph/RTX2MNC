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
  - git clone https://github.com/commontk/DCMTK.git
  - cd DCMTK
  - ./configure
  - make all
  - sudo make install-all
### Minc
  - wget http://packages.bic.mni.mcgill.ca/minc-toolkit/RPM/minc-toolkit-1.0.08-20160205-CentOS_6.7-x86_64.rpm
  - sudo rpm -Uvh minc-toolkit-1.0.08-20160205-CentOS_6.7-x86_64.rpm

  - echo 'export PATH=$PATH:/opt/minc/bin' >> ~/.bash_profile
  - echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/minc/lib' >> ~/.bash_profile
  - echo 'export PERL5LIB=$PERL5LIB:/opt/minc/perl' >> ~/.bash_profile
  - source ~/.bash_profile
