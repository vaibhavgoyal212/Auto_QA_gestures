import numpy as np
import pandas as pd
from pymo.parsers import BVHParser
from pymo.preprocessing import *
import re

# This needs to be placed into the PyMO folder to work

# IMPORTANT!
# Relevant joint refers to the joints which are used for the numerical evaluation in the genea paper mentioned in section 5.5.
# These do NOT refer to the joints which move to act out gestures (for this information see relevant_joints_info.txt).

def bvh_to_coords(bvh_file_path,write_path):
    parser = BVHParser()

    parsed_data = parser.parse(bvh_file_path)

    mp = MocapParameterizer('position')

    # Positions gives us the positions of all the joints. We want to exclude the joints which do not move.
    positions = mp.fit_transform([parsed_data])

    joint_positions = positions[0].values
    joint_positions.to_csv(write_path, index = False)

def bvh_to_coords_for_joints(bvh_file_path, write_path, joints):
    parser = BVHParser()

    parsed_data = parser.parse(bvh_file_path)

    mp = MocapParameterizer('position')

    # Positions gives us the positions of all the joints. We want to exclude the joints which do not move.
    positions = mp.fit_transform([parsed_data])

    joint_positions = positions[0].values
    relevant_joint_positions = joint_positions.loc[:, joint_positions.columns.isin(joints)]
    relevant_joint_positions.to_csv(write_path, index = False)

def find_relevant_joints(csv_file_path, coord_file_path):
    df = pd.read_csv(csv_file_path)
    num_of_columns = df.shape[1]
    num_of_rows = df.shape[0]
    does_column_change = [False] * num_of_columns

    coords_from_genea_file = np.load(coord_file_path)

    relevant_joints = []
    for column in range(0,int(num_of_columns/3)):
        for i in range(0,coords_from_genea_file.shape[1]):
                if (np.abs(df.iat[0,(column*3)] - coords_from_genea_file[0,i,0]) < 0.000001):
                    if (np.abs(df.iat[0,(column*3) + 1] - coords_from_genea_file[0,i,1]) < 0.000001):
                        if (np.abs(df.iat[0,(column*3) + 2] - coords_from_genea_file[0,i,2]) < 0.000001):
                            relevant_joints = relevant_joints + [df.columns[column*3]] + [df.columns[(column*3)+1]] + [df.columns[(column*3)+2]]

    print(len(relevant_joints))
    expected_joints = ['Hips_Xposition', 'Hips_Yposition', 'Hips_Zposition',
     'Spine_Xposition', 'Spine_Yposition', 'Spine_Zposition', 'Spine1_Xposition',
      'Spine1_Yposition', 'Spine1_Zposition', 'Spine2_Xposition', 'Spine2_Yposition',
       'Spine2_Zposition', 'Spine3_Xposition', 'Spine3_Yposition', 'Spine3_Zposition',
        'LeftArm_Xposition', 'LeftArm_Yposition', 'LeftArm_Zposition', 'LeftForeArm_Xposition',
         'LeftForeArm_Yposition', 'LeftForeArm_Zposition', 'LeftHand_Xposition', 'LeftHand_Yposition',
          'LeftHand_Zposition', 'RightArm_Xposition', 'RightArm_Yposition', 'RightArm_Zposition',
           'RightForeArm_Xposition', 'RightForeArm_Yposition', 'RightForeArm_Zposition',
            'RightHand_Xposition', 'RightHand_Yposition', 'RightHand_Zposition', 'Neck_Xposition',
             'Neck_Yposition', 'Neck_Zposition', 'Neck1_Xposition', 'Neck1_Yposition', 'Neck1_Zposition',
              'Head_Xposition', 'Head_Yposition', 'Head_Zposition', 'Head_Nub_Xposition',
               'Head_Nub_Yposition', 'Head_Nub_Zposition']

    if (relevant_joints != expected_joints):
        raise Exception("The relevant joints are different to the expected ones for csv_file_path: " + csv_file_path + " and coord_file_path" + coord_file_path)
 
    if ((df.at[0,relevant_joints[-6]] - df.at[0,relevant_joints[-3]] > 0.000001) or (df.at[0,relevant_joints[-5]] - df.at[0,relevant_joints[-2]] > 0.000001) or
        (df.at[0,relevant_joints[-4]] - df.at[0,relevant_joints[-1]] > 0.000001)):
        raise Exception("The Head Nub positions are different to the Head positions for csv_file_path: " + csv_file_path + " and coord_file_path" + coord_file_path)

# Used to confirm that the relevant joints are consistent across every sample of motion available
def verify_relevant_joints():
    conds = ['Cond_BA', 'Cond_BT', 'Cond_SA', 'Cond_SB', 'Cond_SC', 'Cond_SD', 'Cond_SE']
    bvh_cond_paths = ['Cond_BA/bvh', 'Cond_BT', 'Cond_SA/Edinburgh_CGVU_results', 'Cond_SB/Submission', 'Cond_SC', 'Cond_SD', 'Cond_SE/BVH_NECTEC']
    coord_file_nums = ['001', '002', '003', '004', '005', '006', '007', '008', '009', '010']
    for path in bvh_cond_paths:
        for n in range(1,11):
            bvh_file_path = "/home/cameron/ug4project-1/GENEA2020/BVH_evaluation/" + path + "/TestSeq" + coord_file_nums[n-1] + ".bvh"
            original_coord_file_path = "/home/cameron/ug4project-1/3D_Coords/All_the_3d_coords/" + conds[bvh_cond_paths.index(path)] + "/TestSeq" + coord_file_nums[n-1] + ".bvh_3d.npy"
            if (path == 'Cond_BT'):
                bvh_file_path = "/home/cameron/ug4project-1/GENEA2020/BVH_evaluation/" + path + "/TestSeq" + coord_file_nums[n-1] + "_generated.bvh"
                original_coord_file_path = "/home/cameron/ug4project-1/3D_Coords/All_the_3d_coords/" + conds[bvh_cond_paths.index(path)] + "/TestSeq" + coord_file_nums[n-1] + "_generated.bvh_3d.npy"
            write_path = "csv_files/" + conds[bvh_cond_paths.index(path)] + "/TestSeq" + str(n) + "_joint_coords.csv"
            bvh_to_coords(bvh_file_path, write_path)
            find_relevant_joints(write_path, original_coord_file_path)

# Creates all the 3d coord files for the relevant joints (for numerical evaluation) from bvh files
def create_all_3d_coord_files1():
    conds = ['Cond_BA', 'Cond_BT', 'Cond_SA', 'Cond_SB', 'Cond_SC', 'Cond_SD', 'Cond_SE']
    bvh_cond_paths = ['Cond_BA/bvh', 'Cond_BT', 'Cond_SA/Edinburgh_CGVU_results', 'Cond_SB/Submission', 'Cond_SC', 'Cond_SD', 'Cond_SE/BVH_NECTEC']
    relevant_joints = ['Hips_Xposition', 'Hips_Yposition', 'Hips_Zposition',
     'Spine_Xposition', 'Spine_Yposition', 'Spine_Zposition', 'Spine1_Xposition',
      'Spine1_Yposition', 'Spine1_Zposition', 'Spine2_Xposition', 'Spine2_Yposition',
       'Spine2_Zposition', 'Spine3_Xposition', 'Spine3_Yposition', 'Spine3_Zposition',
        'LeftArm_Xposition', 'LeftArm_Yposition', 'LeftArm_Zposition', 'LeftForeArm_Xposition',
         'LeftForeArm_Yposition', 'LeftForeArm_Zposition', 'LeftHand_Xposition', 'LeftHand_Yposition',
          'LeftHand_Zposition', 'RightArm_Xposition', 'RightArm_Yposition', 'RightArm_Zposition',
           'RightForeArm_Xposition', 'RightForeArm_Yposition', 'RightForeArm_Zposition',
            'RightHand_Xposition', 'RightHand_Yposition', 'RightHand_Zposition', 'Neck_Xposition',
             'Neck_Yposition', 'Neck_Zposition', 'Neck1_Xposition', 'Neck1_Yposition', 'Neck1_Zposition',
              'Head_Xposition', 'Head_Yposition', 'Head_Zposition'] # Head nub excluded as it is the same as Head for all positions

    # Synthesised Motion
    for path in bvh_cond_paths:
        for n in range(1,41):
            bvh_file_path = "/home/cameron/ug4project-1/GENEA2020/BVH_evaluation/" + path + "/StudySeq" + str(n) + ".bvh"
            write_path = "/home/cameron/ug4project-1/Dataset/" + conds[bvh_cond_paths.index(path)] + "/numerical_eval_coords/StudySeq" + str(n) + "_joint_coords.csv"
            bvh_to_coords_for_joints(bvh_file_path, write_path, relevant_joints)

    # Ground Truth Motion
    for n in range(1,41):
        bvh_file_path = "/home/cameron/ug4project-1/GENEA2020/Test_data/Motion/StudySeq" + str(n) + ".bvh"
        write_path = "/home/cameron/ug4project-1/Dataset/Cond_N_60fps/numerical_eval_coords/StudySeq" + str(n) + "_joint_coords.csv"
        bvh_to_coords_for_joints(bvh_file_path, write_path, relevant_joints)

# Creates all the 3d coord files for the motion (moving joints) from bvh files
# The difference between create_all_3d_coord_files1 and 2 is that the csv files produced select different joints.
def create_all_3d_coord_files2():
    conds = ['Cond_BA', 'Cond_BT', 'Cond_SA', 'Cond_SB', 'Cond_SC', 'Cond_SD', 'Cond_SE']
    bvh_cond_paths = ['Cond_BA/bvh', 'Cond_BT', 'Cond_SA/Edinburgh_CGVU_results', 'Cond_SB/Submission', 'Cond_SC', 'Cond_SD', 'Cond_SE/BVH_NECTEC']
    moving_joints = ['Spine_Xposition', 'Spine_Yposition', 'Spine_Zposition', 
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

    # Synthesised Motion
    for path in bvh_cond_paths:
        for n in range(1,41):
            bvh_file_path = "/home/cameron/ug4project-1/GENEA2020/BVH_evaluation/" + path + "/StudySeq" + str(n) + ".bvh"
            write_path = "/home/cameron/ug4project-1/Dataset/" + conds[bvh_cond_paths.index(path)] + "/motion_coords/StudySeq" + str(n) + "_joint_coords.csv"
            bvh_to_coords_for_joints(bvh_file_path, write_path, moving_joints)

    # Ground Truth Motion
    for n in range(1,41):
        bvh_file_path = "/home/cameron/ug4project-1/GENEA2020/Test_data/Motion/StudySeq" + str(n) + ".bvh"
        write_path = "/home/cameron/ug4project-1/Dataset/Cond_N_60fps/motion_coords/StudySeq" + str(n) + "_joint_coords.csv"
        bvh_to_coords_for_joints(bvh_file_path, write_path, moving_joints)

# Uses the motion for moving joints which are the same as those used in create_all_3d_coord_files2()
def create_mismatched_3d_coords_files():
    moving_joints = ['Spine_Xposition', 'Spine_Yposition', 'Spine_Zposition', 
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

    for n in range(1,41):
        bvh_file_path = "/home/cameron/ug4project-1/GENEA2020/Test_data/Motion/Mismatched/StudySeq" + str(n) + ".bvh"
        write_path = "/home/cameron/ug4project-1/Dataset/Cond_M_60fps/motion_coords/StudySeq" + str(n) + "_joint_coords.csv"
        bvh_to_coords_for_joints(bvh_file_path, write_path, moving_joints)

# Creates all the augmented 3d coord files from the noisy bvh files
def create_all_augmented_3d_coord_files():
    Conds = ['Cond_BA', 'Cond_BT', 'Cond_N_60fps', 'Cond_M_60fps', 'Cond_SA', 'Cond_SB', 'Cond_SC', 'Cond_SD', 'Cond_SE']
    moving_joints = ['Spine_Xposition', 'Spine_Yposition', 'Spine_Zposition', 
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
    for cond in Conds:
        for n in range(1,401):
            bvh_file_path = '/home/cameron/ug4project-1/Synthesised_Dataset/' + cond + '/bvh_files/StudySeq' + str(n) + '.bvh'
            write_path = '/home/cameron/ug4project-1/Synthesised_Dataset/' + cond + '/motion_coords/StudySeq' + str(n) + '_joint_coords.csv'
            bvh_to_coords_for_joints(bvh_file_path, write_path, moving_joints)

if __name__ == "__main__":
    #create_all_3d_coord_files1() # the resulting csv files from this are not used
    #create_all_3d_coord_files2() # the resulting csv files from this are used
    #create_mismatched_3d_coords_files() # the resulting csv files from this are used
    create_all_augmented_3d_coord_files() # the resulting csv files from this are used