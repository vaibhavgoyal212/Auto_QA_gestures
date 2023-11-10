import re
import pandas as pd

# Give start_time and end_time as floats, and bvh_file_path as string
# Creates a bvh file snippet starting at the start_time and finishing at the end_time of the original supplied bvh file.
# If the end time is longer than the duration of the motion in the original bvh_file then the final frame of motion in the original bvh file
# is duplicated to fill in remaining duration in the new bvh file.
def write_bvh_between(start_time, end_time, bvh_file_path, write_path):
    f = open(bvh_file_path)
    bvh_file = f.readlines()
    f.close()

    num_of_frames = int(re.findall('\d+', bvh_file[bvh_file.index("MOTION\n")+1])[0])

    frame_time = float(re.findall("\d+\.\d+", bvh_file[bvh_file.index("MOTION\n")+2])[0])

    bvh_frames = bvh_file[bvh_file.index("MOTION\n")+3:]

    start_frame = round(start_time/frame_time)
    end_frame = round(end_time/frame_time)

    # Note that we want end_frame, not end_frame+1
    bvh_frames_snippet = bvh_frames[start_frame:end_frame] 

    # Case addressing issue described on github
    if (end_frame > len(bvh_frames)):
        missing_frames = end_frame - len(bvh_frames)
        bvh_frames_snippet = bvh_frames_snippet + ([bvh_frames_snippet[-1]]*missing_frames)
    # Issue solved

    if (len(bvh_frames_snippet) != end_frame - start_frame):
        raise Exception("The number of frames in the file is incorrect")

    new_bvh_file = bvh_file[:bvh_file.index("MOTION\n")+3] + bvh_frames_snippet

    new_bvh_file[new_bvh_file.index("MOTION\n")+1] = "Frames: " + str(end_frame - start_frame) + "\n" # Update the "Frames: ???" field to specify the correct number of frames

    f = open(write_path, "x")
    for line in new_bvh_file:
        f.write(line)
    f.close()

# Duplicates last frame of a bvh file n times
def duplicate_last_frame(bvh_file_path, write_path, n):
    f = open(bvh_file_path)
    bvh_file = f.readlines()
    f.close()

    num_of_frames = int(re.findall('\d+', bvh_file[bvh_file.index("MOTION\n")+1])[0])
    new_num_of_frames = num_of_frames + n

    # duplicate the frames
    new_bvh_file = bvh_file + [bvh_file[-1]] * n

    # Update the "Frames: ???" field to specify the correct number of frames
    new_bvh_file[new_bvh_file.index("MOTION\n")+1] = "Frames: " + str(new_num_of_frames) + "\n"

    f = open(write_path, "x")
    for line in new_bvh_file:
        f.write(line)
    f.close()

# Creates the studyseq files from testseq files
def extract_studyseqs(studyseq_info_path):
    f = open(studyseq_info_path)
    study_seq_info = f.readlines()
    study_seq_info = study_seq_info[study_seq_info.index("START:\n")+1:]

    study_seq_times = [x[x.index("/")+1:x.index("/", x.index("/")+1)] for x in study_seq_info]

    study_seq_start_times = [float(x[:x.index("-")]) for x in study_seq_times]
    study_seq_end_times = [float(x[x.index("-")+1:]) for x in study_seq_times]

    bvh_test_seqs = [x[x.index(":")+2:x.index(".json")]+".bvh" for x in study_seq_info] # TestSeq bvh file corresponding to the TestSeq transcript for each StudySeq
    
    #Uncomment the code below and comment code above to deal with the inconsistent TestSeq names in Cond_BT
    #bvh_test_seqs = [x[x.index(":")+2:x.index(".json")]+"_generated.bvh" for x in study_seq_info] 

    study_seq_names = [x[:x.index(":")]+".bvh" for x in study_seq_info] # StudySeq numbers from 1-40
    
    for i in range(0,len(study_seq_names)):
        write_bvh_between(study_seq_start_times[i], study_seq_end_times[i], bvh_test_seqs[i], study_seq_names[i])

# Should be called while in the directory with testseqs for cond/N
def extract_mismatched_studyseqs(studyseq_info_path, mismatched_studyseq_info_path):
    # Get the start times of the Cond/M studyseqs by finding the start times of their corresponding Cond/N studyseqs
    f1 = open(studyseq_info_path)
    N_study_seq_info = f1.readlines()
    N_study_seq_info = N_study_seq_info[N_study_seq_info.index("START:\n")+1:]

    N_study_seq_times = [x[x.index("/")+1:x.index("/", x.index("/")+1)] for x in N_study_seq_info]

    study_seq_start_times = [float(x[:x.index("-")]) for x in N_study_seq_times]
    bvh_test_seqs = [x[x.index(":")+2:x.index(".json")]+".bvh" for x in N_study_seq_info] # TestSeq bvh file corresponding to the TestSeq transcript for each StudySeq
    
    M_info = pd.read_csv(mismatched_studyseq_info_path)

    for i in M_info.iloc[:,0]:
        write_path = "Mismatched/pre_StudySeq" + str(i) + ".bvh" # you should delete these bvh files afterwards - these files are just saved as an intermediate step
        N_idx = i % 40
        test_seq = bvh_test_seqs[N_idx]
        start_time = study_seq_start_times[N_idx]
        end_time = round(start_time + M_info.iloc[i-1,2], 1)
        write_bvh_between(start_time, end_time, test_seq, write_path)

        frames_to_duplicate = M_info.iloc[i-1, 3] * 3 # Multiplied by 3 since testseq files for Cond/N are in 60 fps

        duplicate_write_path = "Mismatched/StudySeq" + str(i) + ".bvh"
        duplicate_last_frame(write_path, duplicate_write_path, frames_to_duplicate)


if __name__ == "__main__":
    # Execute python file in directory of the desired cond for the studyseq bvh files
    studyseq_info_path = "/home/cameron/ug4project-1/GENEA_studyseq_info.txt"
    #extract_studyseqs(studyseq_info_path)
    mismatched_studyseq_info_path = "/home/cameron/ug4project-1/GENEA_studyseq_mismatched_info.csv"
    extract_mismatched_studyseqs(studyseq_info_path, mismatched_studyseq_info_path)