import numpy as np
import pandas as pd
import itertools
from genea_numerical_evaluations.calk_jerk_or_acceleration import *
import argparse

# Reads a motion_coord_path with n frames and returns a dataframe with n-1 rows and 15 columns corresponding to the relevant joints
# provided by Jinhong. Each row corresponds to the euclidean distance of the joint between consecutive frames - e.g. row 0 corresponds to
# the euclidean distance between the first and second occuring frame of the studyseq.
def find_joint_distances_between_frames(motion_coord_path):
    df = pd.read_csv(motion_coord_path)
    df = df.diff().iloc[1:,:]
    data = []
    dataframe_cols = ['Spine_Distances', 'Spine1_Distances', 'Spine2_Distances', 'Spine3_Distances', 'LeftShoulder_Distances',
                        'LeftArm_Distances', 'LeftForeArm_Distances', 'LeftHand_Distances', 'RightShoulder_Distances', 'RightArm_Distances',
                        'RightForeArm_Distances', 'RightHand_Distances', 'Neck_Distances', 'Neck1_Distances', 'Head_Distances']
    for i in range(0, round(len(df.columns) / 3)):
        data = data + [np.sqrt((df.values[:,i]**2) + (df.values[:,i+1]**2) + (df.values[:,i+2] **2))] # Finds Straight Line Distance for each joint between consecutive frames
    
    new_df = pd.DataFrame(data[0], columns=[dataframe_cols[0]])
    for i in range(1,len(dataframe_cols)):
        new_df[dataframe_cols[i]] = data[i]
    
    return new_df

def find_mean_joint_positions():
    # TODO
    return null

def find_max_change_of_joint_positions():
    # TODO
    return null

def find_min_change_of_joint_positions():
    # TODO
    return null

def find_std_dev_of_joint_positions():
    # TODO
    return null

# Returns a tuple of 2 arrays with the mean pairwise joints for every combination of unique 3d joints in the bvh file as the first element of 
# the tuple and the pairwise distance label of each value of as the second element of the tuple. This is supposed to be used for the
# motion_coords csv files created. 
def find_mean_pairwise_joint_distances(motion_coord_path):
    df = pd.read_csv(motion_coord_path)
    num_of_joints = 15
    combinations = itertools.combinations([x for x in range(0,num_of_joints)], 2) # unique joint combinations
    joint_names = []
    mean_pairwise_joint_distances = []
    for combination in combinations:
        joint1_coords = df.iloc[:,(combination[0]*3):(combination[0]*3) + 3]
        joint2_coords = df.iloc[:,(combination[1]*3):(combination[1]*3) + 3]

        joint1 = df.columns[combination[0]*3]
        joint1_name = joint1[:joint1.index("_")]
        joint2 = df.columns[combination[1]*3]
        joint2_name = joint2[:joint2.index("_")]

        pairwise_joint_name = joint1_name + "_vs_" + joint2_name
        joint_names = joint_names + [pairwise_joint_name]

        mean_euclidean_distance = find_mean_euclidean_distance_between_joints(joint1_coords.to_numpy(), joint2_coords.to_numpy())
        mean_pairwise_joint_distances = mean_pairwise_joint_distances + [mean_euclidean_distance]

    return (mean_pairwise_joint_distances, joint_names)

# Helper function for find_mean_pairwise_joint_distances
# Takes two Nx3 arrays where the the three columns correspond to the x, y, and z coordinates of the joint at the N-th frame.
# Returns an Nx1 array where each row corresponds to the distance between the two joints given to the function at the N-th frame.
def find_mean_euclidean_distance_between_joints(joint1_coords, joint2_coords):
    square_differences = np.square(joint1_coords - joint2_coords)
    square_distances = np.sum(square_differences, axis=1)
    euclidean_distances = np.sqrt(square_distances)
    mean_euclidean_distance = np.mean(euclidean_distances)
    return mean_euclidean_distance

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--feature", "-f", help='mean_jerk_values or mean_pairwise_euclidean_distances or mean_acceleration_values or joint_distances_between_frames')
    parser.add_argument("--study", "-s", help='appropriateness (includes Cond_M) or human_likeness (doesnt matter for joint_distances_between_frames)')
    parser.add_argument("--augmented", "-a", help='set to True if this is for the augmented dataset, False otherwise')
    args = parser.parse_args()

    if (args.augmented == 'True'):
        Studyseqs = 801
        dataset_path = 'Synthesised_Dataset'
    if (args.augmented == 'False'):
        Studyseqs = 41
        dataset_path = 'Dataset'

    # Create file for mean jerk values
    if (args.study == "appropriateness"):
        Conds = ['Cond_BA', 'Cond_BT', 'Cond_N', 'Cond_M', 'Cond_SA', 'Cond_SB', 'Cond_SC', 'Cond_SD', 'Cond_SE']
        feature_path = "Appropriateness_Features"
    if (args.study == "human_likeness"):
        Conds = ['Cond_BA', 'Cond_BT', 'Cond_N', 'Cond_SA', 'Cond_SB', 'Cond_SC', 'Cond_SD', 'Cond_SE']
        feature_path = "Human_Likeness_Features"

    if (args.feature == "mean_jerk_values"):
        print("Computing Mean Jerk Values...")
        columns = ['Spine', 'Spine1', 'Spine2', 'Spine3', 'LeftShoulder', 'LeftArm', 'LeftForearm', 'LeftHand', 
                            'RightShoulder', 'RightArm', 'RightForearm', 'RightHand', 'Neck', 'Neck1', 'Head']
        data = []
        dataframe_index = []

        for cond in Conds:
            for i in range(1,Studyseqs):
                dataframe_index = dataframe_index + [cond + "/StudySeq" + str(i)]
                studyseq_motion_coord_path = "/home/cameron/ug4project-1/" + dataset_path + "/" + cond + "/motion_coords/StudySeq" + str(i) + "_joint_coords.csv"
                coord_info = pd.read_csv(studyseq_motion_coord_path)
                coord_info = coord_info.to_numpy()
                mean_jerk_values = compute_jerks(coord_info)
                data = data + [mean_jerk_values]

        feature_df = pd.DataFrame(data, columns = columns, index = dataframe_index)
        write_path = "/home/cameron/ug4project-1/" + dataset_path + "/" + feature_path + "/mean_jerk_values.csv"
        feature_df.to_csv(write_path)

    # Create file for mean acceleration values

    if (args.feature == "mean_acceleration_values"):
        print("Computing Mean Acceleration Values...")
        columns = ['Spine', 'Spine1', 'Spine2', 'Spine3', 'LeftShoulder', 'LeftArm', 'LeftForearm', 'LeftHand', 
                            'RightShoulder', 'RightArm', 'RightForearm', 'RightHand', 'Neck', 'Neck1', 'Head']
        data = []
        dataframe_index = []

        for cond in Conds:
            for i in range(1,Studyseqs):
                dataframe_index = dataframe_index + [cond + "/StudySeq" + str(i)]
                studyseq_motion_coord_path =  "/home/cameron/ug4project-1/" + dataset_path + "/" + cond + "/motion_coords/StudySeq" + str(i) + "_joint_coords.csv"
                coord_info = pd.read_csv(studyseq_motion_coord_path)
                coord_info = coord_info.to_numpy()
                mean_accel_values = compute_acceleration(coord_info)
                data = data + [mean_accel_values]

        feature_df = pd.DataFrame(data, columns = columns, index = dataframe_index)
        write_path = "/home/cameron/ug4project-1/" + dataset_path + "/" +feature_path + "/mean_acceleration_values.csv"
        feature_df.to_csv(write_path)

    # Create file for mean pairwise euclidean distances

    if (args.feature == "mean_pairwise_euclidean_distances"):
        print("Computing Mean Pairwise Euclidean Distances...")
        data = []
        dataframe_index = []
        for cond in Conds:
            for i in range(1,Studyseqs): # range(1,41) to cover all StudySeqs from StudySeq1 to StudySeq40
                dataframe_index = dataframe_index + [cond + "/StudySeq" + str(i)]
                studyseq_motion_coord_path = "/home/cameron/ug4project-1/" + dataset_path + "/" + cond + "/motion_coords/StudySeq" + str(i) + "_joint_coords.csv"
                mean_pairwise_joint_distances = find_mean_pairwise_joint_distances(studyseq_motion_coord_path)[0]
                data = data + [mean_pairwise_joint_distances]
                current_label = find_mean_pairwise_joint_distances(studyseq_motion_coord_path)[1]
                # Below are some commented out checks for sanity
                #if (cond != 'Cond_BA' and i != 1):
                    #if (current_label != last_label):
                        #raise Exception("Last label is not equal to current label - this needs to be checked")
                #last_label = current_label
        #print("Length should be 320 and it is: ", len(data))

        feature_df = pd.DataFrame(data, columns = current_label, index = dataframe_index)
        write_path = "/home/cameron/ug4project-1/" + dataset_path + "/" +feature_path + "/mean_pairwise_joint_distances.csv"
        feature_df.to_csv(write_path)

    if (args.feature == "joint_distances_between_frames"):
        print("Computing Joint Distances Between Frames...")

        Conds = ['Cond_BA', 'Cond_BT', 'Cond_N', 'Cond_M', 'Cond_SA', 'Cond_SB', 'Cond_SC', 'Cond_SD', 'Cond_SE']

        for cond in Conds:
            for i in range(1,Studyseqs): # range(1,41) to cover all StudySeqs from StudySeq1 to StudySeq40
                studyseq_motion_coord_path = "/home/cameron/ug4project-1/" + dataset_path + "/" + cond + "/motion_coords/StudySeq" + str(i) + "_joint_coords.csv"
                df = find_joint_distances_between_frames(studyseq_motion_coord_path)
                write_path = "/home/cameron/ug4project-1/" + dataset_path + "/" + cond + '/joint_distances_between_frames/StudySeq' + str(i) + '.csv'
                df.to_csv(write_path)

