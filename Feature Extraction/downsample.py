import pandas as pd
import numpy as np

# Takes a csv referring to joint coordinates of 60 fps motion and returns a pandas dataframe referring to the same
# motion but in 20 fps.
def from_60_to_20_fps(coord_csv_file_path):
    df = pd.read_csv(coord_csv_file_path)
    downsampled_df = df.iloc[::3, :]
    return downsampled_df

if __name__ == "__main__":
    #Cond = "Cond_N_60fps"
    #Cond = "Cond_M_60fps"
    #path_to_cond = "/home/cameron/ug4project-1/Dataset/" + Cond
    #num_of_study_seqs = 40
    #motion_coords
    #for i in range (1, num_of_study_seqs + 1):
        #path_to_study_seq = path_to_cond + "/motion_coords/StudySeq" + str(i) + "_joint_coords.csv"
        # write path for Cond_N
        #write_path = "/home/cameron/ug4project-1/Dataset/Cond_N/motion_coords/StudySeq" + str(i) + "_joint_coords.csv"
        # write path for Cond_M
        #write_path = "/home/cameron/ug4project-1/Dataset/Cond_M/motion_coords/StudySeq" + str(i) + "_joint_coords.csv"
        #from_60_to_20_fps(path_to_study_seq).to_csv(write_path, index=False)

    #numerical_eval_coords - commented out for mismatched motion downsampling
    #for i in range (1, num_of_study_seqs + 1):
    #    path_to_study_seq = path_to_cond + "/numerical_eval_coords/StudySeq" + str(i) + "_joint_coords.csv"
    #    write_path = "/home/cameron/ug4project-1/Dataset/Cond_N/numerical_eval_coords/StudySeq" + str(i) + "_joint_coords.csv"
    #    from_60_to_20_fps(path_to_study_seq).to_csv(write_path, index=False)

    #synthesised data set motion coords downsampling
    Conds = ['Cond_N_60fps', 'Cond_M_60fps']
    num_of_study_seqs = 400
    for cond in Conds:
        for i in range(1, num_of_study_seqs + 1):
            path_to_study_seq = '/home/cameron/ug4project-1/Synthesised_Dataset/' + cond + '/motion_coords/StudySeq' + str(i) + '_joint_coords.csv'
            if (cond == 'Cond_N_60fps'):
                write_path = '/home/cameron/ug4project-1/Synthesised_Dataset/Cond_N/motion_coords/StudySeq' + str(i) + '_joint_coords.csv'
            else:
                write_path = '/home/cameron/ug4project-1/Synthesised_Dataset/Cond_M/motion_coords/StudySeq' + str(i) + '_joint_coords.csv'
            from_60_to_20_fps(path_to_study_seq).to_csv(write_path, index=False)

