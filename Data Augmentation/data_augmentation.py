import pandas as pd
import numpy as np
import argparse
from scipy.stats import truncnorm
from pymo.parsers import BVHParser
from pymo.preprocessing import *

# Swaps the left and right joint coordinates of the Studyseq held at the read_path and creates a new Studyseq at the write_path
def swap_left_right(read_path, write_path):
    df = pd.read_csv(read_path)
    original_columns = ['Spine_Xposition', 'Spine_Yposition', 'Spine_Zposition', 
                        'Spine1_Xposition','Spine1_Yposition', 'Spine1_Zposition', 
                        'Spine2_Xposition', 'Spine2_Yposition','Spine2_Zposition', 
                        'Spine3_Xposition', 'Spine3_Yposition', 'Spine3_Zposition',
                        'LeftShoulder_Xposition','LeftShoulder_Yposition','LeftShoulder_Zposition',
                        'LeftArm_Xposition', 'LeftArm_Yposition', 'LeftArm_Zposition', 
                        'LeftForeArm_Xposition','LeftForeArm_Yposition', 'LeftForeArm_Zposition', 
                        'LeftHand_Xposition', 'LeftHand_Yposition', 'LeftHand_Zposition', 
                        'RightShoulder_Xposition','RightShoulder_Yposition','RightShoulder_Zposition', 
                        'RightArm_Xposition', 'RightArm_Yposition', 'RightArm_Zposition',
                        'RightForeArm_Xposition', 'RightForeArm_Yposition', 'RightForeArm_Zposition',
                        'RightHand_Xposition', 'RightHand_Yposition', 'RightHand_Zposition', 
                        'Neck_Xposition', 'Neck_Yposition', 'Neck_Zposition', 
                        'Neck1_Xposition', 'Neck1_Yposition', 'Neck1_Zposition',
                        'Head_Xposition', 'Head_Yposition', 'Head_Zposition']
       
    swapped_columns = ['Spine_Xposition', 'Spine_Yposition', 'Spine_Zposition', 
                        'Spine1_Xposition','Spine1_Yposition', 'Spine1_Zposition', 
                        'Spine2_Xposition', 'Spine2_Yposition','Spine2_Zposition', 
                        'Spine3_Xposition', 'Spine3_Yposition', 'Spine3_Zposition',
                        'RightShoulder_Xposition','RightShoulder_Yposition','RightShoulder_Zposition',
                        'RightArm_Xposition', 'RightArm_Yposition', 'RightArm_Zposition', 
                        'RightForeArm_Xposition','RightForeArm_Yposition', 'RightForeArm_Zposition', 
                        'RightHand_Xposition', 'RightHand_Yposition', 'RightHand_Zposition', 
                        'LeftShoulder_Xposition','LeftShoulder_Yposition','LeftShoulder_Zposition', 
                        'LeftArm_Xposition', 'LeftArm_Yposition', 'LeftArm_Zposition',
                        'LeftForeArm_Xposition', 'LeftForeArm_Yposition', 'LeftForeArm_Zposition',
                        'LeftHand_Xposition', 'LeftHand_Yposition', 'LeftHand_Zposition', 
                        'Neck_Xposition', 'Neck_Yposition', 'Neck_Zposition', 
                        'Neck1_Xposition', 'Neck1_Yposition', 'Neck1_Zposition',
                        'Head_Xposition', 'Head_Yposition', 'Head_Zposition']

    reordered_df = df[swapped_columns]
    rename_dict = dict(zip(swapped_columns, original_columns))
    renamed_reordered_df = reordered_df.rename(columns=rename_dict) # Reordering the dataframe and then renaming the columns results in the left and right joint coordinates being swapped
    renamed_reordered_df.to_csv(write_path, index=False)

# adds noise to joint coordinate files
def add_noise(read_path, write_path, sigma=0.05):
    df = pd.read_csv(read_path)
    lower, upper, mu = -0.05, 0.05, 0
    X = truncnorm((lower-mu)/sigma, (upper-mu)/sigma, loc=mu, scale=sigma)
    df = df + X.rvs(df.shape) # adding random gaussian noise with limits [lower, upper]
    df.to_csv(write_path, index=False)

# adds noise to the bvh files
def add_noise_to_bvh(bvh_file_path, write_path, sigma=0.05):
    f = open(bvh_file_path)
    bvh_file = f.readlines()
    f.close()

    bvh_frames = bvh_file[bvh_file.index("MOTION\n")+3:]
    for i in range(0,len(bvh_frames)):
        bvh_frames[i] = [float(val) for val in bvh_frames[i].split()]
    bvh_frames = np.array(bvh_frames)

    lower, upper, mu = -0.05, 0.05, 0
    X = truncnorm((lower-mu)/sigma, (upper-mu)/sigma, loc=mu, scale=sigma)
    bvh_frames = bvh_frames + X.rvs(np.shape(bvh_frames))

    bvh_header = bvh_file[:bvh_file.index("MOTION\n")+3]
    

    f = open(write_path, "x")
    for line in bvh_header:
        f.write(line)
    for frame in bvh_frames:
        for val in frame:
            f.write(str(val))
            f.write(' ')
        f.write('\n')
    f.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--augmentation", '-a', help='Type of data augmentation to perform, look at info for more info (options are the studyseq numbers e.g. 41-80 for left-right swaps)')
    parser.add_argument("--noise_space", '-n', help='Specify whether to add noise to the bvh files or to the 3d Joint coordinates (they are roughly equal)')
    args = parser.parse_args()

    if (args.noise_space == 'joint_coords'):
        if (args.augmentation == '41-80'):
            Conds = ['Cond_BA', 'Cond_BT', 'Cond_N', 'Cond_M', 'Cond_SA', 'Cond_SB', 'Cond_SC', 'Cond_SD', 'Cond_SE']
            Studyseqs = range(1,41)
            for cond in Conds:
                for i in Studyseqs:
                    read_path = cond + '/motion_coords/StudySeq' + str(i) + '_joint_coords.csv'
                    write_path = cond + '/motion_coords/StudySeq' + str(i+40) + '_joint_coords.csv'
                    swap_left_right(read_path, write_path)

        if (args.augmentation == '81-6400'):
            Conds = ['Cond_BA', 'Cond_BT', 'Cond_N', 'Cond_M', 'Cond_SA', 'Cond_SB', 'Cond_SC', 'Cond_SD', 'Cond_SE']
            Studyseqs = range(1,81)

            n = 9 # number of times to generate a synthesised studyseq by adding random noise to the same studyseq
            for k in range(1,n+1):
                for cond in Conds:
                    for i in Studyseqs:
                        read_path = cond + '/motion_coords/StudySeq' + str(i) + '_joint_coords.csv'
                        write_path = cond + '/motion_coords/StudySeq' + str(i+(80*k)) + '_joint_coords.csv'
                        add_noise(read_path, write_path)
    
    # This file must be placed in the pymo directory for the bvh arg to work
    if (args.noise_space == 'bvh'):
        if (args.augmentation == '41-3200'): # add noise to the bvh files first
            Conds = ['Cond_BA', 'Cond_BT', 'Cond_N_60fps', 'Cond_M_60fps', 'Cond_SA', 'Cond_SB', 'Cond_SC', 'Cond_SD', 'Cond_SE']
            Studyseqs = range(1,41)

            n = 9 # number of times to generate a synthesised studyseq by adding random noise to the same studyseq
            for k in range(1,n+1):
                for cond in Conds:
                    for i in Studyseqs:
                        read_path = '../Synthesised_Dataset/' + cond + '/bvh_files/StudySeq' + str(i) + '.bvh'
                        write_path = '../Synthesised_Dataset/' + cond + '/bvh_files/StudySeq' + str(i+(40*k)) + '.bvh'
                        add_noise_to_bvh(read_path, write_path)

        if (args.augmentation == '3200-6400'): # then swap left and right joints in the joint coordinate files
            Conds = ['Cond_BA', 'Cond_BT', 'Cond_N', 'Cond_M', 'Cond_SA', 'Cond_SB', 'Cond_SC', 'Cond_SD', 'Cond_SE']
            Studyseqs = range(1,401)
            for cond in Conds:
                for i in Studyseqs:
                    read_path = '../Synthesised_Dataset/' + cond + '/motion_coords/StudySeq' + str(i) + '_joint_coords.csv'
                    write_path = '../Synthesised_Dataset/' + cond + '/motion_coords/StudySeq' + str(i+400) + '_joint_coords.csv'
                    swap_left_right(read_path, write_path)