import numpy as np
import pandas as pd
from pymo.parsers import BVHParser
from pymo.preprocessing import *
import re
from scipy.stats import truncnorm

# Place this file in PyMO to make it work

def add_noise_to_bvh(bvh_file_path, write_path):
    f = open(bvh_file_path)
    bvh_file = f.readlines()
    f.close()

    bvh_frames = bvh_file[bvh_file.index("MOTION\n")+3:]
    for i in range(0,len(bvh_frames)):
        bvh_frames[i] = [float(val) for val in bvh_frames[i].split()]
    bvh_frames = np.array(bvh_frames)

    lower, upper, mu, sigma = -0.05, 0.05, 0, 0.05
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

def bvh_to_coords_for_joints(bvh_file_path, write_path, joints):
    parser = BVHParser()

    parsed_data = parser.parse(bvh_file_path)

    mp = MocapParameterizer('position')

    # Positions gives us the positions of all the joints. We want to exclude the joints which do not move.
    positions = mp.fit_transform([parsed_data])

    joint_positions = positions[0].values
    relevant_joint_positions = joint_positions.loc[:, joint_positions.columns.isin(joints)]
    relevant_joint_positions.to_csv(write_path, index = False)

if __name__ == "__main__":
    bvh_file_path = '../GENEA2020/BVH_evaluation/Cond_BA/bvh/StudySeq1.bvh'
    write_path = '../GENEA2020/BVH_evaluation/Cond_BA/bvh/StudySeq1_noisy_gauss2.bvh'
    add_noise_to_bvh(bvh_file_path, write_path)

    joints = ['Spine_Xposition', 'Spine_Yposition', 'Spine_Zposition', 
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

    read_path = '../GENEA2020/BVH_evaluation/Cond_BA/bvh/StudySeq1_noisy_gauss2.bvh'
    write_path = '../GENEA2020/BVH_evaluation/Cond_BA/bvh/StudySeq1_noisy_gauss2.csv'
    bvh_to_coords_for_joints(read_path, write_path, joints)