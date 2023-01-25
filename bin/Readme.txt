JM Reference Software README
============================

The latest version of this software can be obtained from:

  http://iphome.hhi.de/suehring/tml

For reporting bugs please use the JM bug tracking system located at:

  https://ipbt.hhi.fraunhofer.de


Please send comments and additions to Karsten.Suehring (at) hhi.fraunhofer.de and alexis.tourapis@dolby.com

======================================================================================
NOTE: This file contains only a quick overview.

      More detailed information can be found the "JM Reference Software Manual" in the
      doc/ subdirectory of this package.
======================================================================================

1. Compilation
2. Command line parameters
3. Input/Output file format
4. Configuration files
5. Platform specific notes


1. Compilation
--------------

1.1 Windows
-----------
  
  Workspaces for MS Visual C++ 2003/2005/2008/2010 are provided with the names 

    jm_vc7.sln   - MS Visual C++ 2003
    jm_vc8.sln   - MS Visual C++ 2005
    jm_vc9.sln   - MS Visual C++ 2008
    jm_vc10.sln  - MS Visual C++ 2010

  These contain encoder and decoder projects.


1.2 Unix
--------

  Before compiling in a UNIX environment please run the "unixprep.sh" script which
  will remove the DOS LF characters from the files and create object directories.

  Makefiles for GNU make are provided at the top level and in the lencod and ldecod directories.


1.3 MacOS X
-----------

  A workspace for XCode can be found in the main directory. The project can also be build 
  using the UNIX build process (make).


2. Command line parameters
--------------------------

2.1 Encoder
-----------

    lencod.exe [-h] [-d default-file] [-f file] [-p parameter=value]

  All Parameters are initially taken from DEFAULTCONFIGFILENAME, defined in 
  configfile.h (typically: "encoder.cfg")

  -h
             Show help on parameters.

  -d default-file    
             Use the specified file as default configuration instead of the file in 
             DEFAULTCONFIGFILENAME.  

  -f file    
             If an -f parameter is present in the command line then 
             this file is used to update the defaults of DEFAULTCONFIGFILENAME.  
             There can be more than one -f parameters present.  

  -p parameter=value 

             If -p <ParameterName = ParameterValue> parameters are present then 
             these overide the default and the additional config file's settings, 
             and are themselfes overridden by future -p parameters.  There must 
             be whitespace between -f and -p commands and their respecitive 
             parameters.
  -v
             Show short version info.
  -V
             Show long version info.

2.2 Decoder
-----------

    ldecod.exe [-h] [-d default-file] [-f file] [-p parameter=value]

  All Parameters are initially taken from DEFAULTCONFIGFILENAME, defined in 
  configfile.h (typically: "encoder.cfg")

  -h
             Show help on parameters.

  -d default-file    
             Use the specified file as default configuration instead of the file in 
             DEFAULTCONFIGFILENAME.  

  -f file    
             If an -f parameter is present in the command line then 
             this file is used to update the defaults of DEFAULTCONFIGFILENAME.  
             There can be more than one -f parameters present.  

  -p parameter=value 

             If -p <ParameterName = ParameterValue> parameters are present then 
             these overide the default and the additional config file's settings, 
             and are themselfes overridden by future -p parameters.  There must 
             be whitespace between -f and -p commands and their respecitive 
             parameters.
  -v
             Show short version info.
  -V
             Show long version info.



3. Input/Output file format
---------------------------

  The source video material is read from raw YUV 4:2:0 data files.
  For output the same format is used.


4. Configuration files
----------------------

  Sample encoder and decode configuration files are provided in the bin/ directory.
  These contain explanatory comments for each parameter.
  
  The generic structure is explained here.

4.1 Encoder
-----------
  <ParameterName> = <ParameterValue> # Comments

  Whitespace is space and \t

  <ParameterName>  are the predefined names for Parameters and are case sensitive.
                   See configfile.h for the definition of those names and their 
                   mapping to configinput->values.

 <ParameterValue> are either integers [0..9]* or strings.
                  Integers must fit into the wordlengths, signed values are generally 
                  assumed. Strings containing no whitespace characters can be used directly.
                  Strings containing whitespace characters are to be inclosed in double 
                  quotes ("string with whitespace")
                  The double quote character is forbidden (may want to implement something 
                  smarter here).

  Any Parameters whose ParameterName is undefined lead to the termination of the program
  with an error message.

  Known bug/Shortcoming:  zero-length strings (i.e. to signal an non-existing file
                          have to be coded as "".
 
4.2 Decoder
-----------
  Beginning with JM 17.0 the decoder uses the same config file style like the encoder.

4.2.1 Integer Transform Coefficients
------------------------------------

The current setting for extracting Integer Transform (i.e. DCT) coefficients from the Committee decoder is to set a handful of flags in the decoder configuration file (e.g. decoder.cfg in /JM/bin/).  In general the output will only be for non-zero coefficients.  This means that entire Macroblock(s) or Frame(s) will be ignored when writing to output text files if values are entirely 0 for the region being considered.  This is important to consider if you intend to use the output to construct a visualization of these residual coefficients (e.g. via a python script).  Let's take a look at the default settings in the configuration file:

DCT_quant	       = 1		 # 1: Quantized Coefficients (0: Dequantized coefficients) (-dct)
Chroma                 = 0               # Output Chroma B and Chroma R coefficients (0: Luma only) (-c)
IFrames                = 1		 # 1: I-frames only, 0: All-frames (-if)
Details                = 0	         # 1: Frame Number, Frame Type, Pixel Indices, Dimensions, etc. (0: Just Coefficients/"Bag of Coefficients")(-det)
CoefFile              = "test_luma.txt"    # Output file for DCT coefficients   (Luma channel)
CoefFile_b              = "chr_b_coef.txt"    # Output file for DCT coefficients (Chroma B channel)
CoefFile_r              = "chr_r_coef.txt"    # Output file for DCT coefficients (Chroma R channel)

DCT_quant specifies whether or not the user wants the coefficients to be quantized or dequantized.  During encoding, coefficients are quantized using a QP parameter.  During decoding, the coefficients are mapped back to the original scale using a "dequantization" step.  By default, this variable is set to 1, indicating this dequantizing step will be ignored when outputting the coefficients.  If you set it to 0, the coefficients will be dequantized and will typically be at least a few orders of magnitude larger than when DCT_quant = 1.

Chroma allows the user to output the coefficients corresponding to the Blue and Red Chroma channels (into files CoefFile_b and CoefFile_r respectively).  By defualt, it is set to 0 meaning that only the Luma channel coefficients will be output (into CoefFile). 

IFrames is set to 1 by default, meaning only I and IDR frames will be considering when extracting the Integer coefficients of the residuals.  If you set this to 0, it will consider all frames (again, please keep in mind frames with all zero values will be skipped regardless to whether they are I/P/B type).

In each file, the first line will provide the YUV format (YUV format (0=4:0:0, 1=4:2:0, 2=4:2:2, 3=4:4:4)) and source/video resolutions.  

Details is set to 0.  Thus by default, the output is just a bunch of coefficients (as ints) being dumped into a text file.  If you set this value to 1, detailed information will be provided for each coefficient.  It has the form:

Global Frame Number (this is the displayed order)	Frame Type (I/P/B)	(Once per frame)
X_index,Y_index,Integer Transform Coefficient 					(Once per each non-zero integer transform coefficient)


Please note that the default settings can be thought of as a "bag of coefficients".  It allows to the user to get a quick assessment of the video in question by pooling all the coefficients spanning the frames of the video into a single file.  From there, one can easily make a histogram and perform exploratory data analysis on each video.  By changing the default settings (specifically by setting Details=1), the user has the capability to further interpret and visualize patterns in the coefficients data.  

The last 3 lines in the decoder configuration file specify the file names you would like for the output for each respecitve channel.  


4.2.2  Motion Vectors and corresponding residuals
------------------------------------------------

Currently a basic utility is added to allow the user to extract motion vectors and their respective residuals during the decoding process. If the MV_flag is set to 1 in the configuration file, data will be output to the MV_file set there in the following comma separated format:


display order frame number, macroblock type, block x index, block y index, sub-block x index, sub-block y index, motion vector x, motion vector y, motion vector residual x, motion vector residual y  

Some comments on these output:  The decoder does not necessarily decode in display order, so the first field is not always in the order as you look at the output, (e.g. frame 7 may be decoded before frame 4).  The Macroblock type corresponds to how it is partitioned.  I have encountered theses codes correspond to the following partitions: (1: 16x16 (full MB), 2: (two 16x8), 3: (two 8x16), 8: (four 8x8)).  If the macroblock is partitioned into four 8x8 partitions, it can (but not necessarily) have further macroblock partitioning (sub-macroblock partitions).  It is noticiable that the block x and block y indices are 1/4 that of the pixel resolution and this is consistent with the Luma MVs being 1/4 the resolution of the video (Chapter 6 of Iain Richardson's H.264: Advanced Compression Standard has detailed discussion about MVs).  The sub-block indices correspond to the location within each respective macroblock.  Much consideration should be placed on these values in relation to the Macroblock type in field 2 (discussed above).  For example if the MB type is 1, the sub block indices will be 0,0.  If the MB type is 3, the sub block indices will be 0,0 for the first MV pair and 8,0 for the second MV pair (the second of the two 8x16), etc....

The sub macroblock structure for 8x8 MB partitions can be inferred from the combination of this output, if more explicit pattern information is desired it is recommended the user looks at function read_P8x8_macroblock within /ldecod/src/mb_read.c.
   
The remaining four fields include the MV information: one (x,y) pair for vectors and a corresponding pair for the residuals.  

The extraction of this information is in a preliminary state and there is more that could be done such as extracting reference frame(s).

### 4.2.3 Macroblock Data Extraction  ######

There are two new output options included in the /bin/decoder.cfg file:  MB_file and MB_info.  MB_file outputs three integer values per frame in decode order in a comma separated format: The number of: I Macroblocks, S Macroblocks, P Macroblocks.  This values are simply a summary of the entire frame.  The value of each line should sum to the same value (the total number of MB per frame = Resolution/16^2).
The second new MB file output option includes more specific information including spatial location, QP delta (quantization parameter change), and GOP (group of picture) frame number.  The MB_info is also in a comma separated format with the following output:  MB Type, MB QP Delta, X Index, Y Index, GOP Frame Number.  There is a slight redundancy as the Motion Vector file, if used, will provide Macroblock Types, but only for the subset of Frames/Blocks (those containing motion vectors).  The integer value of parameter 'MB Type' indicates the following block type:

Skip  MB    			0
P MB  16x16  			1
P MB  16x8   			2
P MB  8x16   			3
P MB  Sub-MB 8x8      		4
P MB  Sub-MB  8x4       	5
P MB  Sub-MB 4x8        	6
P MB  Sub-MB  4x4               7
P MB  8x8           		8
I4MB           			9
I16MB         			10
IBLOCK      			11
SI4MB         			12
I8MB          			13
IPCM        			14
MAXMODE    			15  


5. Platform specific notes
--------------------------
  This section contains hints for compiling and running the JM software on different 
  operating systems.

5.1 MacOS X
-----------
  MacOs X has a UNIX core so most of the UNIX compile process will work. You might need 
  the following modifications:

  a) Before Leopard (MacOS 10.5): in Makefile change "CC = $(shell which gcc)" to "CC = gcc"
     (it seems "which" doesn't work)

  b) MacOS "Tiger" (MacOS 10.4) doesn't come with ftime. We suggest using a third party ftime 
     implementation, e.g. from:

     http://darwinsource.opendarwin.org/10.3.4/OpenSSL096-3/openssl/crypto/ftime.c

5.2 FreeBSD
-----------
  You might need to add "-lcompat" to LIBS in the Makefiles for correct linking.

