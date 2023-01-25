from subprocess import call
import sys 
import os
import time
import math
import getopt


##### ******* This is only intended to be an example and further development is encouraged.************

##### Input is a path to video files (e.g. .mp4).  FFMPEG is used to generate .264 from .mp4, etc. 

##### Outputs to current directory: both .264 and the MB Type Data files.

options, args = getopt.getopt(sys.argv[1:], 'hp:q:i:c:d:m:o:e:f:')

quant = "1"
chroma = "1"
i_frames = "0"
details = "1"
motion_vector = "1"
output_path = ""
executable = "../ldecod.exe"
config_file = "../decoder.cfg"

for opt, arg in options:
	if(opt == "-h"):
		print("batch_extract_data.py -p <full_path_to_input_directory> -o <path_to_output_directory> -e <path_to_ldecod.exe_file> -f <path_to_decoder.cfg_file> -q <quantization flag: 0/1> -c <chroma-channel flag: 0/1> -i <i-frames only flag: 0/1 > -d <details flag: 0/1> -m <motion vector flag: 0/1>")
		sys.exit()
	elif(opt == "-o"):
		output_path = arg
	elif (opt == "-p"):
		filepath = arg
	elif (opt == "-q"):
		quant = arg 
	elif (opt == "-c"):
		chroma = arg			
	elif (opt== "-i"):
		i_frames = arg
	elif (opt == "-d"):
		details = arg
	elif (opt == "-m"):
		motion_vector = arg
	elif (opt == "-e"):
		executable = arg
	elif (opt == "-f:"):
		config_file = arg

if(not os.path.exists(output_path + "coefficient_files")):
	os.mkdir(output_path + "coefficient_files")
if(not os.path.exists(output_path + "264_files")):
	os.mkdir(output_path +"264_files")
if(not os.path.exists(output_path + "mb_data")):
	os.mkdir(output_path + "vpf_data")
if(not os.path.exists(output_path + "mb_info")):
	os.mkdir(output_path + "macroblock_data")
if(not os.path.exists(output_path + "chroma_b")):
	os.mkdir(output_path + "chroma_b")
if(not os.path.exists(output_path + "chroma_r")):
	os.mkdir(output_path + "chroma_r")
if(not os.path.exists(output_path + "motion_vec_data")):
	os.mkdir(output_path + "motion_vec_data")


	   

for filename in os.listdir(filepath):
	path_mp4_ = filepath + filename
	vid_id = filename.split(".")[0]
	path_264_ = output_path + "264_files/" + vid_id + ".264"
	vpf_path =  output_path + "vpf_data/" + vid_id + "_vpf_sequence_data.csv"
	coef_path = output_path + "coefficient_files/" + vid_id + "_coef_data.csv"
	macroblock_type_path = output_path + "macroblock_data/" + vid_id + "_macroblock_type_data.csv"	
	motion_path = output_path + "motion_vec_data/" + vid_id + "_mv_data.csv"
	chroma_b_path = output_path + "chroma_b/" + vid_id + "_chroma_b.csv"
	chroma_r_path = output_path + "chroma_r/" + vid_id + "_chroma_r.csv"
	call(["ffmpeg","-i",path_mp4_,"-vcodec","copy","-bsf","h264_mp4toannexb","-an","-f","h264",path_264_])		
	call([executable,"-d",config_file,"-p","InputFile=" + path_264_,"-p","OutputFile=" + "output.yuv","-p","DCT_quant="+quant,"-p","Chroma="+chroma,"-p","IFrames="+i_frames,"-p","Details="+details,"-p","VPf_data=" + vpf_path,"-p","RefFile = "" ","-p","CoefFile =" + coef_path,"-p","MB_data =" + macroblock_type_path,"-p","MV_flag=", motion_vector,"-p","MV_file =" + motion_path,"-p","CoefFile_b =" + chroma_b_path,"-p","CoefFile_r =" + chroma_r_path])

