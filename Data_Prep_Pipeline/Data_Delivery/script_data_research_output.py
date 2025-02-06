from pymongo import MongoClient
import pandas as pd
import os
import data_prep_helper as data_prep_helper

uri = os.getenv('MONGODB_TO_URI', "mongodb://localhost:27017")
color_mapper = {
    '31914156': 'hsl(333, 70%, 50%)',
    '40279283': 'hsl(333, 70%, 50%)',
    '40279478': 'hsl(333, 70%, 50%)',
    '40279541': 'hsl(333, 70%, 50%)',
    '40279157': 'hsl(333, 70%, 50%)',
    '40929832': 'hsl(333, 70%, 50%)',
    '31921637': 'hsl(333, 70%, 50%)',
    '40279346': 'hsl(333, 70%, 50%)',
    '40279220': 'hsl(333, 70%, 50%)',
    '31929974': 'hsl(333, 70%, 50%)',
    '31335106': 'hsl(333, 70%, 50%)',
    '40279415': 'hsl(333, 70%, 50%)',
    '31340112': 'hsl(333, 70%, 50%)',
    '59575309': 'hsl(333, 70%, 50%)',
    '55472869': 'hsl(333, 70%, 50%)',
    '79139069': 'hsl(333, 70%, 50%)',
    '77369668': 'hsl(333, 70%, 50%)'
}


def prepare_data(use_short_name):
    global df_merged_final, short_name_mapper
    # merge with python because mongo is too slow
    # first get publication_filled dataframa

    client = MongoClient(uri)
    result = client['FLK_Web']['publications'].find({})
    df_publications = pd.DataFrame.from_records(result)
    result_orga = client['FLK_Data_Lake']['organisation_publications'].find({})
    df_organisation_publications = pd.DataFrame.from_records(result_orga)
    organisations = data_prep_helper.get_children_organisation_ids(31923392)['children']
    organisation_ids = [str(organisation['id']) for organisation in organisations]
    df_organisation = pd.DataFrame.from_records(client['FLK_Data_Lake']['organisation'].find({'id': {'$in': organisation_ids}}))
    # left join pub df_publication_filled with df_organisation_publications on id=publication_id
    df_merged = pd.merge(df_publications, df_organisation_publications, how='left', left_on='id',
                         right_on='publication_id')
    df_merged_final = pd.merge(df_merged, df_organisation, how='left', left_on='organisation_id', right_on='id')
    df_merged_final = df_merged_final[['id_x', 'publYear', 'organisation_id', 'cfTitle', 'cfName']]
    df_merged_final.rename(columns={'id_x': 'id'}, inplace=True)
    # drop rows where cfName is Nan
    df_merged_final.dropna(subset=['cfName'], inplace=True)
    # define label names for different organisations
    short_name_mapper_old = {
        '31914156': 'Lehrstuhl für Wirtschaftsinformatik und Informationsmanagement (Prof. Becker)',
        '40279283': 'Lehrstuhl für Wirtschaftsinformatik und Interorganisationssysteme (Prof. Klein)',
        '40279478': 'Juniorprofessur für Wirtschaftsinformatik, insbesondere IT-Sicherheit (Prof. Böhme)',
        '40279541': 'Forschungsgruppe Quantitative Methoden in der Logistik',
        '40279157': 'Lehrstuhl für Praktische Informatik in der Wirtschaft (Prof. Kuchen)',
        '40929832': 'Juniorprofessur für Wirtschaftsinformatik, insb. IT-Sicherheit (Prof. Fischer)',
        '31921637': 'Lehrstuhl für Informatik (Prof. Vossen)',
        '40279346': 'Lehrstuhl für Wirtschaftsinformatik und Logistik (Prof. Hellingrath)',
        '40279220': 'Professur für Statistik und Optimierung (Prof. Trautmann)',
        '31929974': 'Forschungsgruppe Kommunikations- und Kollaborationsmanagement',
        '31335106': 'Quantitative Methoden der Wirtschaftsinformatik',
        '40279415': 'Institut für Wirtschaftsinformatik - Mathematik für Wirtschaftswissenschaftler',
        '31340112': 'Lehrstuhl für Wirtschaftsinformatik und Controlling',
        '59575309': 'Professur für Maschinelles Lernen und Data Engineering (Prof. Gieseke)',
        '55472869': 'Juniorprofessur für IT-Sicherheit (Prof. Hupperich)',
        '79139069': 'Juniorprofessur für Wirtschaftsinformatik, insbesondere Digitale Transformation und Gesellschaft (Prof. Berger)',
        '77369668': 'Professur für Digitale Innovation und der öffentliche Sektor (Prof. Brandt)'
    }
    short_name_mapper = {
        '31914156': 'Wirtschaftsinformatik und Informationsmanagement (Prof. Becker)',
        '40279283': 'Wirtschaftsinformatik und Interorganisationssysteme (Prof. Klein)',
        '40279478': 'Wirtschaftsinformatik, insbesondere IT-Sicherheit (Prof. Böhme)',
        '40279541': 'Quantitative Methoden in der Logistik (Dr. Meisel)',
        '40279157': 'Praktische Informatik in der Wirtschaft (Prof. Kuchen)',
        '40929832': 'Wirtschaftsinformatik, insb. IT-Sicherheit (Prof. Fischer)',
        '31921637': 'Informatik (Prof. Vossen)',
        '40279346': 'Wirtschaftsinformatik und Logistik (Prof. Hellingrath)',
        '40279220': 'Statistik und Optimierung (Prof. Trautmann)',
        '31929974': 'Forschungsgruppe Kommunikations- und Kollaborationsmanagement',
        '31335106': 'Quantitative Methoden der Wirtschaftsinformatik (Prof. Müller-Funk)',
        '40279415': 'Institut für Wirtschaftsinformatik - Mathematik für Wirtschaftswissenschaftler',
        '31340112': 'Lehrstuhl für Wirtschaftsinformatik und Controlling',
        '59575309': 'Professur für Maschinelles Lernen und Data Engineering (Prof. Gieseke)',
        '55472869': 'IT-Sicherheit (Prof. Hupperich)',
        '79139069': 'Digitale Transformation und Gesellschaft (Prof. Berger)',
        '77369668': 'Digitale Innovation und der öffentliche Sektor (Prof. Brandt)'
    }

    if use_short_name:
        df_merged_final['organisation_name'] = df_merged_final['organisation_id'].map(short_name_mapper)
    else:
        df_merged_final['organisation_name'] = df_merged_final['cfName']
    # publYear should be object like other columns
    df_merged_final['publYear'] = df_merged_final['publYear'].astype(str)


def aggregate_data():
    global df_merged_final_grouped
    # group year and organisation name
    df_merged_final_grouped = df_merged_final.groupby(['publYear', 'organisation_id']).count().reset_index()
    df_merged_final_grouped.rename(columns={'id': 'count'}, inplace=True)
    df_merged_final_grouped = df_merged_final_grouped[['publYear', 'organisation_id', 'count']]
    df_merged_final_grouped['organisation_label'] = df_merged_final_grouped['organisation_id'].map(short_name_mapper)


# help functions:

def get_pubs_from_year(df, year):
    # filter publYear to be == year
    return df[df['publYear'] == year]


# get list of label names from mapper
def get_label_list(mapper):
    return list(mapper.values())


def get_label_for_orga(mapper, orga_id):
    return mapper[orga_id]


# change if needed


def get_color_for_orga(mapper, orga_id):
    return mapper[orga_id]


# get count for orga id and year
def get_count(df, orga_id, year):
    # search the row where publYear = year and orga_id = organisation_id
    row = df[(df['publYear'] == year) & (df['organisation_id'] == orga_id)]
    if len(row) == 0:
        return '0'
    else:
        return str(row['count'].values[0])


def get_year_list(df_grouped):
    year_list = list(df_grouped['publYear'].unique())
    # sort asc
    year_list.sort()
    return year_list


# get orga-ids list
def get_orgas(df_grouped, use_short_name=True):
    # if short name mode remove keys that are not in mappe
    if use_short_name:
        # get keyd from short_name_mapper
        keys = list(short_name_mapper.keys())
        return keys
    else:
        # get all unique orga ids
        return list(df_grouped['organisation_id'].unique())


def construct_data_dict(use_short_name=True):
    year_list = get_year_list(df_merged_final_grouped)
    label_list = get_label_list(short_name_mapper)
    orga_id_list = get_orgas(df_merged_final_grouped, use_short_name=True)
    json_year_list = []
    for year in year_list:
        current_year_dict = {}
        current_year_dict['Jahr'] = year

        # iterate over orgas
        for orga_id in orga_id_list:
            # label
            label = get_label_for_orga(short_name_mapper, orga_id)
            # color
            color_key_string = label + 'Color'
            color_value = get_color_for_orga(color_mapper, orga_id)
            # count
            count_key_string = 'Jahr'
            count_value = get_count(df_merged_final_grouped, orga_id, year)

            # write to dict
            current_year_dict[label] = count_value
            current_year_dict[color_key_string] = color_value

        # append year to list
        json_year_list.append(current_year_dict)

    return json_year_list


def psuh_results(result_dict):
    # save in the mongodb
    MONGODB_TO_DB = "FLK_Web"
    mongo_client = MongoClient(uri)
    to_db = mongo_client[MONGODB_TO_DB]
    target_collection = to_db["data_bar_chart_research_output"]
    target_collection.delete_many({})
    target_collection.insert_many(result_dict)
    print('Inserted data into collection: ' + 'FLK WEB: ' + 'data_bar_chart_research_output')


def create_data_and_push():
    prepare_data(use_short_name=True)
    # aggregate data
    aggregate_data()
    research_output_result = construct_data_dict(use_short_name=True)
    psuh_results(result_dict=research_output_result)


# main
if __name__ == '__main__':
    create_data_and_push()
