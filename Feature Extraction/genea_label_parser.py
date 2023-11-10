import json
import pandas as pd

# video has format COND/StudySeqX.mp4 (e.g. BA/StudySeq20.mp4)
def get_mean_score(json_file_path, video):
    file = open(json_file_path)
    test_data = json.load(file)

    total_score = 0
    counter = 0
    for i in test_data['trials']:
        for j in i['stimuli']:
            if (j['video'] == video and j['attention_check'] == False):
                total_score = total_score + j['score']
                counter = counter + 1
    mean_score = total_score/counter
    return mean_score

def get_total_participants(json_file_path, video):
    file = open(json_file_path)
    test_data = json.load(file)

    counter = 0
    for i in test_data['trials']:
        for j in i['stimuli']:
            if (j['video'] == video and j['attention_check'] == False):
                counter = counter + 1
    return counter

if __name__ == "__main__":
    json_file_path_appropriateness = "/home/cameron/ug4project-1/GENEA2020/GENEA2020SubjectiveResultsAnalyses/appropriateness_test_data.json"
    json_file_path_human_likeness = "/home/cameron/ug4project-1/GENEA2020/GENEA2020SubjectiveResultsAnalyses/human-likeness_test_data.json"

    appropriateness_conds = ['BA', 'BT', 'N', 'M', 'SA', 'SB', 'SC', 'SD', 'SE']
    human_likeness_conds = ['BA', 'BT', 'N', 'SA', 'SB', 'SC', 'SD', 'SE']

    scores = []
    dataframe_index = []
    for cond in appropriateness_conds:
        for n in range(1,41):
            mean_score = get_mean_score(json_file_path_appropriateness, cond + '/StudySeq' + str(n) + ".mp4")
            dataframe_index = dataframe_index + ['Cond_' + cond + '/StudySeq' + str(n)]
            scores = scores + [mean_score]
    df = pd.DataFrame(scores, columns = ['Mean_Appropriateness_Score'], index = dataframe_index)
    write_path = "~/ug4project-1/Dataset/Appropriateness_Labels/mean_opinion_scores.csv"
    df.to_csv(write_path)

    scores = []
    dataframe_index = []
    for cond in human_likeness_conds:
        for n in range(1,41):
            mean_score = get_mean_score(json_file_path_human_likeness, cond + '/StudySeq' + str(n) + ".mp4")
            dataframe_index = dataframe_index + ['Cond_' + cond + '/StudySeq' + str(n)]
            scores = scores + [mean_score]

    df = pd.DataFrame(scores, columns = ['Mean_Human_Likeness_Score'], index = dataframe_index)
    write_path = "~/ug4project-1/Dataset/Human_Likeness_Labels/mean_opinion_scores.csv"
    df.to_csv(write_path)

    # Participant Counting


    total_participants = []
    dataframe_index = []
    for cond in appropriateness_conds:
        for n in range(1,41):
            participants = get_total_participants(json_file_path_appropriateness, cond + '/StudySeq' + str(n) + ".mp4")
            dataframe_index = dataframe_index + ['Cond_' + cond + '/StudySeq' + str(n)]
            total_participants = total_participants + [participants]
    df = pd.DataFrame(total_participants, columns = ['Number of Participants'], index = dataframe_index)
    write_path = "~/ug4project-1/Dataset/Appropriateness_Labels/participants_counts.csv"
    df.to_csv(write_path)

    total_participants = []
    dataframe_index = []
    for cond in human_likeness_conds:
        for n in range(1,41):
            participants = get_total_participants(json_file_path_appropriateness, cond + '/StudySeq' + str(n) + ".mp4")
            dataframe_index = dataframe_index + ['Cond_' + cond + '/StudySeq' + str(n)]
            total_participants = total_participants + [participants]
    df = pd.DataFrame(total_participants, columns = ['Number of Participants'], index = dataframe_index)
    write_path = "~/ug4project-1/Dataset/Human_Likeness_Labels/participants_counts.csv"
    df.to_csv(write_path)
