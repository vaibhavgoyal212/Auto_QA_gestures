import os
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

def compute_velocity_of_hands_moving_towards_each_other(coord_info):
    #the velocity of Left hand in reference to another joint right hand in the direction of the segment from left hand to right hand using differentials
    left_hand = coord_info[:, 21:24]
    right_hand = coord_info[:, 33:36]
    left_hand_to_right_hand = right_hand - left_hand
    left_hand_to_right_hand = left_hand_to_right_hand / np.linalg.norm(left_hand_to_right_hand, axis=1)[:, np.newaxis]
    left_hand_velocity = np.diff(left_hand, axis=0)
    velocity_of_hands_moving_towards_each_other = np.sum(left_hand_velocity * left_hand_to_right_hand[:-1], axis=1)
    #scale the velocity to the range of 0 to 1
    velocity_of_hands_moving_towards_each_other = (velocity_of_hands_moving_towards_each_other - np.min(velocity_of_hands_moving_towards_each_other)) / (np.max(velocity_of_hands_moving_towards_each_other) - np.min(velocity_of_hands_moving_towards_each_other))
    # print(velocity_of_hands_moving_towards_each_other, velocity_of_hands_moving_towards_each_other.shape)
    return velocity_of_hands_moving_towards_each_other

def compute_elbow_angle_from_shoulder_arm_forearm(coord_info):
    #the angle between the shoulder, arm and forearm
    left_shoulder = coord_info[:, 12:15]
    left_arm = coord_info[:, 15:18]
    left_forearm = coord_info[:, 18:21]
    left_shoulder_to_arm = left_arm - left_shoulder
    left_shoulder_to_arm = left_shoulder_to_arm / np.linalg.norm(left_shoulder_to_arm, axis=1)[:, np.newaxis]
    left_arm_to_forearm = left_forearm - left_arm
    left_arm_to_forearm = left_arm_to_forearm / np.linalg.norm(left_arm_to_forearm, axis=1)[:, np.newaxis]
    left_elbow_angle = np.arccos(np.clip(np.sum(left_shoulder_to_arm * left_arm_to_forearm, axis=1), -1.0, 1.0))
    #do the same for the right side
    right_shoulder = coord_info[:, 24:27]
    right_arm = coord_info[:, 27:30]
    right_forearm = coord_info[:, 30:33]
    right_shoulder_to_arm = right_arm - right_shoulder
    right_shoulder_to_arm = right_shoulder_to_arm / np.linalg.norm(right_shoulder_to_arm, axis=1)[:, np.newaxis]
    right_arm_to_forearm = right_forearm - right_arm
    right_arm_to_forearm = right_arm_to_forearm / np.linalg.norm(right_arm_to_forearm, axis=1)[:, np.newaxis]
    right_elbow_angle = np.arccos(np.clip(np.sum(right_shoulder_to_arm * right_arm_to_forearm, axis=1), -1.0, 1.0))
    return left_elbow_angle, right_elbow_angle

def compute_speed_of_hand_perpendicular_to_spine(coord_info):
    #the speed of the hand perpendicular to the spine using differentials
    spine = coord_info[:, 0:3]
    left_hand = coord_info[:, 21:24]
    right_hand = coord_info[:, 33:36]
    spine_to_left_hand = left_hand - spine
    spine_to_right_hand = right_hand - spine
    spine_to_left_hand = spine_to_left_hand / np.linalg.norm(spine_to_left_hand, axis=1)[:, np.newaxis]
    spine_to_right_hand = spine_to_right_hand / np.linalg.norm(spine_to_right_hand, axis=1)[:, np.newaxis]
    left_hand_speed = np.diff(left_hand, axis=0)
    right_hand_speed = np.diff(right_hand, axis=0)
    speed_of_right_hand_perpendicular_to_spine = np.sum(right_hand_speed * spine_to_right_hand[:-1], axis=1)
    speed_of_left_hand_perpendicular_to_spine = np.sum(left_hand_speed * spine_to_left_hand[:-1], axis=1)
    #scale the speed to the range of 0 to 1
    speed_of_right_hand_perpendicular_to_spine = (speed_of_right_hand_perpendicular_to_spine - np.min(speed_of_right_hand_perpendicular_to_spine)) / (np.max(speed_of_right_hand_perpendicular_to_spine) - np.min(speed_of_right_hand_perpendicular_to_spine))
    speed_of_left_hand_perpendicular_to_spine = (speed_of_left_hand_perpendicular_to_spine - np.min(speed_of_left_hand_perpendicular_to_spine)) / (np.max(speed_of_left_hand_perpendicular_to_spine) - np.min(speed_of_left_hand_perpendicular_to_spine))
    return speed_of_left_hand_perpendicular_to_spine, speed_of_right_hand_perpendicular_to_spine


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
    parser.add_argument("--feature", "-f", help='mean_jerk_values or mean_pairwise_euclidean_distances or mean_acceleration_values or joint_distances_between_frames', required=True)
    parser.add_argument("--study", "-s", help='appropriateness (includes Cond_M) or human_likeness (doesnt matter for joint_distances_between_frames)', default="human_likeness")
    parser.add_argument("--augmented", "-a", help='set to True if this is for the augmented dataset, False otherwise', default="False")
    args = parser.parse_args()
    main_dir = 'D:/Year 4/HONS/Auto_QA_gestures/'

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

    if (args.feature == "velocity_of_hands_moving_towards_each_other"):
        print("Computing Velocity of Hands Moving Towards Each Other...")
        data = []
        dataframe_index = []
        for cond in Conds:
            for i in range(1,Studyseqs):
                dataframe_index = dataframe_index + [cond + "/StudySeq" + str(i)]
                studyseq_motion_coord_path = main_dir + dataset_path + "/" + cond + "/motion_coords/StudySeq" + str(i) + "_joint_coords.csv"
                coord_info = pd.read_csv(studyseq_motion_coord_path)
                coord_info = coord_info.to_numpy()
                velocity_of_hands_moving_towards_each_other = compute_velocity_of_hands_moving_towards_each_other(coord_info)
                #calculate the mean of the velocity of hands moving towards each other
                velocity_of_hands_moving_towards_each_other = np.mean(velocity_of_hands_moving_towards_each_other)
                data = data + [velocity_of_hands_moving_towards_each_other]

        feature_df = pd.DataFrame(data, columns = ['Velocity_of_Hands_Moving_Towards_Each_Other'], index = dataframe_index)
        print(feature_df)
        write_path = main_dir + dataset_path + "/" + feature_path + "/velocity_of_hands_moving_towards_each_other.csv"
        feature_df.to_csv(write_path)

    if (args.feature == "elbow_angle"):
        print("Computing Elbow Angle...")
        left_data = []
        right_data = []
        dataframe_index = []
        for cond in Conds:
            for i in range(1,Studyseqs):
                dataframe_index = dataframe_index + [cond + "/StudySeq" + str(i)]
                studyseq_motion_coord_path = main_dir + dataset_path + "/" + cond + "/motion_coords/StudySeq" + str(i) + "_joint_coords.csv"
                coord_info = pd.read_csv(studyseq_motion_coord_path)
                coord_info = coord_info.to_numpy()
                left_elbow_angle, right_elbow_angle = compute_elbow_angle_from_shoulder_arm_forearm(coord_info)
                #calculate the mean of the elbow angle
                left_elbow_angle_mean = np.mean(left_elbow_angle)
                right_elbow_angle_mean = np.mean(right_elbow_angle)
                left_elbow_angle_max = np.max(left_elbow_angle)
                right_elbow_angle_max = np.max(right_elbow_angle)
                left_elbow_angle_min = np.min(left_elbow_angle)
                right_elbow_angle_min = np.min(right_elbow_angle)
                left_data = left_data + [(left_elbow_angle_mean, left_elbow_angle_max, left_elbow_angle_min)]
                right_data = right_data + [(right_elbow_angle_mean, right_elbow_angle_max, right_elbow_angle_min)]

        feature_df_left = pd.DataFrame(left_data, columns = ['Left_Elbow_Angle_mean','Left_Elbow_Angle_max','Left_Elbow_Angle_min' ], index = dataframe_index)
        feature_df_right = pd.DataFrame(right_data, columns = ['Right_Elbow_Angle_mean','Right_Elbow_Angle_max','Right_Elbow_Angle_min' ], index = dataframe_index)
        feature_df = pd.concat([feature_df_left, feature_df_right], axis=1)
        write_path = main_dir + dataset_path + "/" + feature_path + "/elbow_angle_props.csv"
        feature_df.to_csv(write_path)

    if (args.feature == "speed_of_hand_perpendicular_to_spine"):
        print("Computing Speed of Hand Perpendicular to Spine...")
        left_data = []
        right_data = []
        dataframe_index = []
        for cond in Conds:
            for i in range(1,Studyseqs):
                dataframe_index = dataframe_index + [cond + "/StudySeq" + str(i)]
                studyseq_motion_coord_path = main_dir + dataset_path + "/" + cond + "/motion_coords/StudySeq" + str(i) + "_joint_coords.csv"
                coord_info = pd.read_csv(studyseq_motion_coord_path)
                coord_info = coord_info.to_numpy()
                speed_of_left_hand_perpendicular_to_spine, speed_of_right_hand_perpendicular_to_spine = compute_speed_of_hand_perpendicular_to_spine(coord_info)
                #calculate the mean of the speed of hand perpendicular to the spine
                speed_of_left_hand_perpendicular_to_spine = np.mean(speed_of_left_hand_perpendicular_to_spine)
                speed_of_right_hand_perpendicular_to_spine = np.mean(speed_of_right_hand_perpendicular_to_spine)
                left_data = left_data + [speed_of_left_hand_perpendicular_to_spine]
                right_data = right_data + [speed_of_right_hand_perpendicular_to_spine]

        feature_df = pd.DataFrame(left_data, columns = ['Speed_of_Left_Hand_Perpendicular_to_Spine'], index = dataframe_index)
        feature_df['Speed_of_Right_Hand_Perpendicular_to_Spine'] = right_data
        write_path = main_dir + dataset_path + "/" + feature_path + "/speed_of_hand_perpendicular_to_spine.csv"
        feature_df.to_csv(write_path)

    if (args.feature == "mean_jerk_values"):
        print("Computing Mean Jerk Values...")
        columns = ['Spine', 'Spine1', 'Spine2', 'Spine3', 'LeftShoulder', 'LeftArm', 'LeftForearm', 'LeftHand', 
                            'RightShoulder', 'RightArm', 'RightForearm', 'RightHand', 'Neck', 'Neck1', 'Head']
        data = []
        dataframe_index = []

        for cond in Conds:
            for i in range(1,Studyseqs):
                dataframe_index = dataframe_index + [cond + "/StudySeq" + str(i)]
                studyseq_motion_coord_path = main_dir + dataset_path + "/" + cond + "/motion_coords/StudySeq" + str(i) + "_joint_coords.csv"
                coord_info = pd.read_csv(studyseq_motion_coord_path)
                coord_info = coord_info.to_numpy()
                mean_jerk_values = compute_jerks(coord_info)
                data = data + [mean_jerk_values]

        feature_df = pd.DataFrame(data, columns = columns, index = dataframe_index)
        write_path = main_dir + dataset_path + "/" + feature_path + "/mean_jerk_values.csv"
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
                studyseq_motion_coord_path =  main_dir + dataset_path + "/" + cond + "/motion_coords/StudySeq" + str(i) + "_joint_coords.csv"
                coord_info = pd.read_csv(studyseq_motion_coord_path)
                coord_info = coord_info.to_numpy()
                mean_accel_values = compute_acceleration(coord_info)
                data = data + [mean_accel_values]

        feature_df = pd.DataFrame(data, columns = columns, index = dataframe_index)
        write_path = main_dir + dataset_path + "/" +feature_path + "/mean_acceleration_values.csv"
        feature_df.to_csv(write_path)

    # Create file for mean pairwise euclidean distances

    if (args.feature == "mean_pairwise_euclidean_distances"):
        print("Computing Mean Pairwise Euclidean Distances...")
        data = []
        dataframe_index = []
        for cond in Conds:
            for i in range(1,Studyseqs): # range(1,41) to cover all StudySeqs from StudySeq1 to StudySeq40
                dataframe_index = dataframe_index + [cond + "/StudySeq" + str(i)]
                studyseq_motion_coord_path = main_dir + dataset_path + "/" + cond + "/motion_coords/StudySeq" + str(i) + "_joint_coords.csv"
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
        write_path = main_dir + dataset_path + "/" +feature_path + "/mean_pairwise_joint_distances.csv"
        feature_df.to_csv(write_path)

    if (args.feature == "joint_distances_between_frames"):
        print("Computing Joint Distances Between Frames...")

        Conds = ['Cond_BA', 'Cond_BT', 'Cond_N', 'Cond_M', 'Cond_SA', 'Cond_SB', 'Cond_SC', 'Cond_SD', 'Cond_SE']

        for cond in Conds:
            for i in range(1,Studyseqs): # range(1,41) to cover all StudySeqs from StudySeq1 to StudySeq40
                studyseq_motion_coord_path = main_dir + dataset_path + "/" + cond + "/motion_coords/StudySeq" + str(i) + "_joint_coords.csv"
                df = find_joint_distances_between_frames(studyseq_motion_coord_path)
                write_path = main_dir + dataset_path + "/" + cond + '/joint_distances_between_frames/StudySeq' + str(i) + '.csv'
                df.to_csv(write_path)

