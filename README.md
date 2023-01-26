# INTRODUCTION #

**Trestles** is a modified H.264 decoder that allows you to output the uncompressed  transformed residual pixel and motion vector values that are contained (in compressed form) in the H.264 NAL units (a.k.a. video bitstream or file).  A bit more detail on these data elements:

 - Coefficients:  These are the coefficients computed by the encoder after subtracting predicted 16x16 macroblocks from actual (raw pixel) macroblocks and computing the H.264 integer transform (a close approximation to the DCT), typically on 4x4 sub-blocks of the residual information.
 - Motion Vectors:  These are the standard H.264 motion vectors (also available via ffmpeg), but in addition to that we return the motion vector difference, which is the residual computed by the encoder after subtracting the predicted motion vector from the actual motion vector.  Only the motion vector difference is actually encoded in the bitstream.

Trestles is built on the ITU-T Standards Committee Reference Decoder known as JM Software (version JM 19.0) freely available [here](https://iphome.hhi.de/suehring/tml/).  This is not the most efficient decoder around, but it has reasonably accessible source code.

The residual data element outputs are controlled by the ldecod configuration file, which is described in the JM `Readme.txt`.  Specifically, we added sections 4.2.1 and 4.2.2 to that Readme, and reproduce them here:


### 4.2.1 Integer Transform Coefficients ##

The current setting for extracting Integer Transform (i.e. DCT) coefficients from the Committee decoder is to set a handful of flags in the decoder configuration file (e.g. `decoder.cfg` in `/JM/bin/`).  In general the output will only be for non-zero coefficients.  This means that entire Macroblock(s) or Frame(s) will be ignored when writing to output text files if values are entirely 0 for the region being considered.  This is important to consider if you intend to use the output to construct a visualization of these residual coefficients (e.g. via a python script).  Let's take a look at the default settings in the configuration file:

`DCT_quant	       = 1		 # 1: Quantized Coefficients (0: Dequantized coefficients) (-dct)`

`Chroma                 = 1               # Output Chroma B and Chroma R coefficients (0: Luma only) (-c)`

`IFrames                = 0		 # 1: I-frames only, 0: All-frames (-if)`

`Details                = 1	         # 1: Frame Number, Frame Type, Pixel Indices, Dimensions, etc. (0: Just Coefficients/"Bag of Coefficients")(-det)`



 - `DCT_quant` specifies whether or not the user wants the coefficients to be quantized or dequantized.  During encoding, coefficients are quantized using a QP parameter.  During decoding, the coefficients are mapped back to the original scale using a "dequantization" step.  By default, this variable is set to 1, indicating this dequantizing step will be ignored when outputting the coefficients.  If you set it to 0, the coefficients will be dequantized and will typically be at least a few orders of magnitude larger than when `DCT_quant` = 1.
 - `Chroma` allows the user to output the coefficients corresponding to the Blue and Red Chroma channels (into files `CoefFile_b` and `CoefFile_r` respectively).
 - If the user only wants information for I frames (key-frames), then set `IFrames` to 1, indicating that only I and IDR frames should be considered when extracting the integer coefficients of the residuals.
 - `Details` is set to 1 by default, thus detailed information will be provided for each coefficient.  It has the form:
 -- Global Frame Number (this is according to displayed order)
 -- Corresponding Macroblock indices: (X,Y)
 -- Corresponding offset indices (X,Y) (0-15 valued)
 -- Integer Transform Coefficient (int value)
 
 If the user would rather just have a quick dump of a "bag of coefficients" for exploratory analysis of the distributions, feel free to change Details = 0 and the output file will only include the non-zero coefficients.
 

There are 3 lines in the decoder configuration file to specify the file names preferred for the output for each respective channel:

`CoefFile              = "luma_coef.csv"     # Output file for DCT coefficients (Luma channel)`
`CoefFile_b            = "chr_b_coef.csv"    # Output file for DCT coefficients (Chroma B channel)`
`CoefFile_r            = "chr_r_coef.csv"    # Output file for DCT coefficients (Chroma R channel)`


### 4.2.2  Motion Vectors and corresponding residuals ##

Currently a very basic utility is provided to extract motion vectors and their respective residuals during the decoding process. If the `MV_flag` is set to 1 in the configuration file, data will be output to the `MV_file` set there in the following comma separated format:

`display order frame number, macroblock type, block x index, block y index, sub-block x index, sub-block y index, motion vector x, motion vector y, motion vector residual x, motion vector residual y`

Some comments on these output fields:

 1. The decoder does not necessarily decode in display order, so the first field is not always in the order as you view the rendered output, (e.g. frame 7 may be decoded before frame 4).
 2. The Macroblock type corresponds to how it is partitioned.  These codes correspond to the following partitions: (1: 16x16 (full MB), 2: (two 16x8), 3: (two 8x16), 8: (four 8x8)).  If the macroblock is partitioned into four 8x8 partitions, it can (but not necessarily) have further macroblock partitioning (sub-macroblock partitions).  It is noticeable that the block x and block y indices are 1/4 that of the pixel resolution and this is consistent with the Luma MVs being 1/4 the resolution of the video (Chapter 6 of [Iain Richardson's H.264: Advanced Compression Standard](https://www.wiley.com/en-us/The+H+264+Advanced+Video+Compression+Standard,+2nd+Edition-p-9780470516928) has detailed discussion about MVs).
 3. The sub-block indices correspond to the location within each respective macroblock.  Much consideration should be placed on these values in relation to the Macroblock type in field 2 (discussed above).  For example if the MB type is 1, the sub block indices will be 0,0.  If the MB type is 3, the sub block indices will be 0,0 for the first MV pair and 8,0 for the second MV pair (the second of the two 8x16), etc....
 4. The sub macroblock structure for 8x8 MB partitions can be inferred from the combination of this output, if more explicit pattern information is desired it is recommended the user look at function `read_P8x8_macroblock` within `/ldecod/src/mb_read.c`.

The remaining four fields include the MV information: one (x,y) pair for vectors and a corresponding pair for the residuals.

The extraction of this information is in a preliminary state and there is more that could be done, such as extracting reference frame(s).

### 4.2.3 Macroblock Data Extraction  ######

There are two new output options included in the /bin/decoder.cfg file:  VPF_data and MB_data.  VPF_data outputs three integer values per frame in decode order in a comma separated format: The number of: I Macroblocks, S Macroblocks, P Macroblocks, Frame Number.  VPF stands for Variation of Prediction Footprint and is a forensic technique used to detect if multiple compression has occurred.  This data file may be used as input into a VPF algorithm (i.e. notebook/python script).  These values are simply a summary of the entire frame, the value of each line should sum to the same value (the total number of MB per frame = Resolution/16^2).
The `MB_data` file output option includes more specific information including spatial location, QP delta (quantization parameter change), and display frame number.  The `MB_data` is also in a comma separated format with the following output:  MB Type, MB QP Delta, X Index, Y Index, Frame Number.  There is a slight redundancy as the Motion Vector file, if used, which will provide Macroblock Types, but only for the subset of Frames/Blocks (those containing motion vectors).  The integer value of parameter 'MB Type' indicates the following block type:

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

---
### Example Python Scripts ###

Please see the newer README_scripts in the /bin/scripts sub-directory for information on data extraction and a jupyter notebook example.

:warning: **Important Caveats:** FMPEG software is required in a few of the calls made by the scripts. This utility provides necessary stream extraction/conversion for certain file types into a JM software-compatible form.

---

### Release ##

LLNL-CODE-844142


