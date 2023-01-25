import numpy as np
from matplotlib.pyplot import imshow, draw, ion, imsave, cm
import matplotlib.pyplot as plt
import matplotlib.axes as ax
from subprocess import check_call
import os
import shutil
from optparse import OptionParser
import sys
from scipy.special import expit
import subprocess
import tempfile
import contextlib


##### This demonstrates how to generate a 3x3 tiled video with an original .mp4 file and Trestles low-level data output.

####  *******It is DEPENDENT on FFMPEG & FFPROBE.*********

#### Necessary inputs are the original video file (e.g. mp4 extension), a macroblock data file, a dct integer coefficient file, and an output file name


@contextlib.contextmanager
def cd(newdir, cleanup=lambda: True):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)
        cleanup()

@contextlib.contextmanager
def tempdir():
    dirpath = tempfile.mkdtemp()
    def cleanup():
        shutil.rmtree(dirpath)
    with cd(dirpath, cleanup):
        yield dirpath



def convert_ffprobe_out(out_frmnum,out_height,out_width,out_frate):
    frate_vec = out_frate.split("/")
    frmnum = int(out_frmnum.split("\n")[-1])
    width = int(out_width.split("=")[1])
    height = int(out_height.split("=")[1])
    if(len(frate_vec)>1):
      frate = int(frate_vec[0])/int(frate_vec[1])
      frate_str = str(frate)
    else:
      frate = int(frate_vec[0])
      frate_str = str(frate)

    return([frmnum,height,width,frate_str,frate]);




# use ffmpeg to tile 2 videos side by side
def tile_side_by_side(ffmpeg, video_left, video_right, video_out):
    check_call([ffmpeg, '-y', '-i', video_left, '-i', video_right, '-filter_complex',  'hstack=inputs=2', '-q:v', '0', video_out])

# use ffmpeg to tile 2 videos side by side
def tile_side_by_side_equal(ffmpeg, video_left, video_right, video_out):
    os.system(ffmpeg + " -y -i %s -i %s -filter_complex \"[0:v]pad=iw*(2):ih:0:0[tempOut];[tempOut][1:v]overlay=W/(2):0[out]\" -map [out] -q:v 0 %s" %(video_left,video_right,video_out))

# use ffmpeg to tile 3 videos side by side
def tile_3_side_by_side(ffmpeg, video_left, video_middle, video_right, video_out):
    check_call([ffmpeg, '-y', '-i', video_left, '-i', video_middle, '-i', video_right, '-filter_complex',  'hstack=inputs=3', '-q:v', '0', video_out])

# use ffmpeg to tile 3 videos side by side
def tile_3_top_to_bottom(ffmpeg, video_top, video_middle, video_bottom, video_out):
    check_call([ffmpeg, '-y', '-i', video_top, '-i', video_middle, '-i', video_bottom, '-filter_complex',  'vstack=inputs=3', '-q:v', '0', video_out])

# use ffmpeg to tile 2 videos vertically
def tile_top_bottom(ffmpeg, video_top, video_bottom, video_out):
    os.system(ffmpeg + " -y -i %s -i %s -filter_complex \"[0:v]pad=iw:ih*2:0:0[tempOut];[tempOut][1:v]overlay=0:H/2[out]\" -map [out] -q:v 0 %s" %(video_top,video_bottom,video_out))
    check_call([ffmpeg, '-y', '-i', video_top, '-i', video_bottom, '-filter_complex',  'vstack=inputs=2', '-q:v', '0', video_out])

# modify the frame rate if necessary
def adjust_frame_rate(ffmpeg, frame_rate, input_video, output_video):
    check_call([ffmpeg, '-y', '-r', str(frame_rate), '-i', input_video, '-r', str(frame_rate), output_video])

def convert_to_annexb(ffmpeg, input_video):
    os.system(ffmpeg + " -y -i %s -vcodec copy -an -bsf:v h264_mp4toannexb input.264" % (input_video))

# shift video by a temporal offset
def offset_frame(ffmpeg, input_vid, offset, frame_rate, output_vid):
    time_offset = offset/frame_rate
    check_call([ffmpeg, '-y', '-i', input_vid, '-ss', ("00:00:0%f" % time_offset), '-async', '1', '-q:v', '0', output_vid])









# create a macroblock type map for a given frame
def mb_type_frame(dirpath, frame_number, mb_type_data):
    out_dir = os.path.join(dirpath, 'mb_' + '%06d' % (frame_number) + '.png')
    imsave(out_dir,(mb_type_data[frame_number,:,:]),vmin=0,vmax=15,cmap=cm.RdBu_r,format='png')

# create a video of macroblock maps for a given video
def mb_type_video(ffmpeg_path, mb_file, output_video, num_frames, width, height, frame_rate):
    tmp = 0
    mb_types = np.zeros((num_frames,height,width))
    with tempdir() as dirpath:
        temp_files = os.path.join(dirpath, "mb_%06d.png")
        f = open(mb_file,'r')
        for line in f:
            mb_data = list(map(int,line.rstrip().split(",")))
            x_l = mb_data[2]*4
            x_u = x_l + 15
            y_l = mb_data[3]*4
            y_u = y_l + 15
            mb_types[mb_data[4],y_l:y_u,x_l:x_u] = mb_data[0]
            if(mb_data[4]!=tmp):
                mb_type_frame(dirpath, tmp, mb_types)
                tmp = mb_data[4]
        mb_type_frame(dirpath, tmp, mb_types)
        f.close()
        check_call([ffmpeg_path, "-y", "-r", frame_rate, "-i", temp_files, "-pix_fmt",  "yuv420p", "-r", frame_rate, "-q:v", "0", output_video])

def histogram_frame_gen(dirpath, coefficients, prev_frame):
    out_dir = os.path.join(dirpath, 'hist_' + '%06d' % (prev_frame) + '.png')
    if(len(coefficients)!=0):
        plt.hist(coefficients,color='blue',range=(-10,10),bins=[-8,-6,-4,-3,-2,-1,0,1,2,3,4,6,8],density=True)
    plt.xlim(left = -6,right = 6)
    plt.ylim(bottom = 0, top = 1)
    plt.savefig(out_dir)
    plt.close()

def histogram_gen(ffmpeg_path, coef_file, output_video, width, height, frame_rate, number_frames):
    coeff_hist = [[] for i in range(number_frames)]
    prev_fn = 0
    with tempdir() as dirpath:
        temp_files = os.path.join(dirpath, "hist_%06d.png")
        # Parse coefficient file
        for line in open(coef_file,'r'):
            l = list(map(int,line.rstrip().split(",")))
            coeff_hist[prev_fn].append(l[5])
            if(l[0]!=prev_fn):
                prev_fn = l[0]

        for i in range(number_frames):
            fig = plt.figure()
            histogram_frame_gen(dirpath, coeff_hist[i], i)
        check_call([ffmpeg_path, "-y", "-r", frame_rate, "-i", temp_files, "-pix_fmt", "yuv420p", "-r", frame_rate, "-q:v", "0", "-s:v",str(width)+":"+str(height), output_video])

# create a macroblock type map for a given frame
def qp_type_frame(dirpath, frame_number, qp_type_data):
    out_dir = os.path.join(dirpath, 'qp_' + '%06d' % (frame_number) + '.png')
    imsave(out_dir,(qp_type_data[frame_number,:,:]),vmin=0,vmax=15,cmap=cm.RdBu_r,format='png')

# create a video of macroblock maps for a given video
def qp_type_video(ffmpeg_path, qp_file, output_video, num_frames, width, height, frame_rate):
    tmp = 0
    qp_types = np.zeros((num_frames,height,width))
    with tempdir() as dirpath:
        temp_files = os.path.join(dirpath, "qp_%06d.png")
        f = open(qp_file,'r')
        for line in f:
            qp_data = list(map(int,line.rstrip().split(",")))
            x_l = qp_data[2]*4
            x_u = x_l + 15
            y_l = qp_data[3]*4
            y_u = y_l + 15
            qp_types[qp_data[4],y_l:y_u,x_l:x_u] = qp_data[1]
            if(qp_data[4]!=tmp):
                qp_type_frame(dirpath, tmp, qp_types)
                tmp = qp_data[4]
        qp_type_frame(dirpath, tmp, qp_types)
        f.close()
        check_call([ffmpeg_path, "-y", "-r", frame_rate, "-i", temp_files, "-pix_fmt",  "yuv420p", "-r", frame_rate, "-q:v", "0", output_video])

# create a coefficient map for a given frame
def coef_type_frame(dirpath, frame_number, coef_type_data):
    out_dir = os.path.join(dirpath, 'coef_' + '%06d' % (frame_number) + '.png')
    imsave(out_dir,(coef_type_data[frame_number,:,:]),vmin=-2,vmax=2,cmap=cm.RdBu_r,format='png')

# create a video of coefficient maps for a given video
def coef_type_video(ffmpeg_path, coef_file, output_video, num_frames, width, height, frame_rate):
    tmp = 0
    if(width%16!=0):
        width = width + (16 - width%16)
    if(height%16!=0):
        height = height + (16 - height%16)
    coef_types = np.zeros((num_frames,height,width))
    with tempdir() as dirpath:
        temp_files = os.path.join(dirpath, "coef_%06d.png")
        for line in open(coef_file,'r'):
            coef_data = list(map(int,line.rstrip().split(",")))
            x = coef_data[1]*4+coef_data[3]
            y = coef_data[2]*4+coef_data[4]
            coef_types[coef_data[0],y,x] = coef_data[5]
            if(coef_data[0]!=tmp):
                tmp = coef_data[0]

        for i in range(num_frames):
            coef_type_frame(dirpath, i, coef_types)
        check_call([ffmpeg_path, "-y", "-r", frame_rate, "-i", temp_files, "-pix_fmt",  "yuv420p", "-r", frame_rate, "-q:v", "0", output_video])

# create vpf frame
def vpf_type_frame(dirpath, width, height, time, frame_types, VPF, frame_display):
    out_dir = os.path.join(dirpath, 'vpf_' + '%06d' % (frame_display[time]) + '.png')
    fig = plt.figure()
    plt.plot(frame_display,VPF,color='black')
    plt.ylim(bottom = 0, top = 1)
    #plt.set_ylabel('VPF',size=16)
    plt.axvline(x=frame_display[time],color='r',linestyle='--')
    #plt.xlabel('Frame Number',size=16)
    plt.title(frame_types[time],fontsize=24)
    plt.savefig(out_dir)
    plt.close()

# generate vpf video
def vpf_video_gen(ffmpeg_path, vpf_file, tau, beta, output_video, width, height, frame_rate):
    f = open(vpf_file,'r')
    I, S, frame_num_vec,VPF_score,frame_type_vec = ([] for i in range(5))
    delta_i_left, delta_s_left =  (0 for i in range(2))
    sigma_S, sigma_I = (1 for i in range(2))
    cnter = 0
    tau = int(tau)
    beta = int(beta)
    for line in f:
        vpf_data = list(map(int,line.rstrip().split(",")[0:4]))
        I.append(vpf_data[0])
        S.append(vpf_data[1])
        frame_num_vec.append(vpf_data[3])
        frame_type_vec.append(line.rstrip().split(",")[4])
    f.close()
    VPF_score.append(0)
    for k in range(len(I)):
        cnter = cnter + 1
        if(cnter>1):
            if(cnter< (len(I)-tau -1) and cnter> (tau+1)):
                sigma_I = (np.std(I[(cnter-tau):(cnter+tau)]))
                sigma_S = (np.std(S[(cnter-tau):(cnter+tau)]))
            else:
                sigma_I = (np.std(I))
                sigma_S = (np.std(S))

            # compute the 'right' side deltas for I and S MB
            delta_i_right = -I[k]+i_left
            delta_s_right = S[k]-s_left
            # evaluate min functions and check for inflection points for I and S respectively, if no max, min, then set to zero
            sig_arg_i = (((min(delta_i_right,delta_i_left))))  / sigma_I - beta
            if(sig_arg_i<0):
                sig_arg_i = 0
            sig_arg_s = (((min(delta_s_right,delta_s_left)))) / sigma_S  - beta
            if(sig_arg_s<0):
                sig_arg_s = 0

            # computation of 'Sigmoid VPF Score'
            energy_sigmoid =  expit(sig_arg_i) + expit(sig_arg_s)-1

            # Update the 'left' delta for the next iteration to be the current 'right' delta by changing sign
            delta_i_left = -delta_i_right
            delta_s_left = -delta_s_right

            VPF_score.append(energy_sigmoid)
        i_left = I[k]
        s_left = S[k]

    with tempdir() as dirpath:
        temp_files = os.path.join(dirpath, "vpf_%06d.png")
        for t in range(len(frame_num_vec)):
            vpf_type_frame(dirpath, width, height, t, frame_type_vec, VPF_score, frame_num_vec)
        check_call([ffmpeg_path, "-y", "-r", frame_rate, "-i", temp_files, "-pix_fmt",  "yuv420p", "-r", frame_rate, "-q:v", "0", "-s:v",str(2*width)+":"+str(height), output_video])
