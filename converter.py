#from header import *
import json
import csv
import copy
#aaaaaaah
#import sys
#import os
#header_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#sys.path.append(header_dir)
#from header import *

#put these here to not deal w/ the commented out header
#VERSION="_JAN23"
#VERSION="_FEB18"
#VERSION="_MAR9"
#VERSION="_JULY6"
VERSION="_JUL21"
import warnings


PARALLEL_ALGO_FIELDS={
        "Old Family #": "family",
        "Looked at?": "looked at",
        "Subproblem": "problem",
        "Variation": "vars",
        "Algo ID": "id",
        "Algorithm Name": "auth",
        "Year": "year",
        "Span Encoding (T_1)": "span",
        "Work Encoding (T_inf)": "work",
        "Model Encoding": "model",
        "Randomized?": "randomized",
        "Approximate?": "approximate",
        "Heuristic-based?": "heuristic",
        "Parallel?": "parallel",
        "# of Proc Encoding": "par",
        "Quantum?": "quantum",
        "GPU-based?": "gpu",
        "Domains": "domains"
    }

SEQUENTIAL_ALGO_FIELDS={
        "Old Family #": "family",
        "Looked at?": "looked at",
        "Subproblem": "problem",
        #"Subproblem (currently only for Parallel Algo)": "problem",
        "Variation": "vars",
        "Algo ID": "id",
        "Algorithm Name": "auth",
        "Year": "year",
        "Time Encoding": "time",
        "Randomized?": "randomized",
        "Approximate?": "approximate",
        "Heuristic-based?": "heuristic",
        "Parallel?": "parallel",
        "Quantum?": "quantum",
        "GPU-based?": "gpu",
        "Domains": "domains"
    }

PARALLEL_DISCARABLE_FIELD_VALUES = {
        "problem": ("","#N/A"),
        "auth": "",
        "year": "",
        "span": ("","xxxx","xxx","yy"," "),
        "work": ("","xxxx","xxx","yy"," "),
        "model": (""," "),
        "approximate": "1",
        "heuristic": "1",
        "parallel": ("0",""," "),
        "par": "",
        "quantum": "1",
        "gpu": "1",
    }

SEQUENTIAL_DISCARABLE_FIELD_VALUES = {
        "problem": "", #i think this field is specified for parallel algos,
        # not necessarily specified for seq so uh, need to check its not filtering out things we want
        "auth": "",
        "year": ("",'-'),
        "time": "",
        "approximate": "1",
        "heuristic": "1",
        "parallel": "1",
        "quantum": "1",
        "gpu": "1",
    }

PARALLEL_ALLOWABLE_MODELS = {100, 110, 120, 130, 131, 132, 133, 135, 200, 210,
                             220, 300, 310, 320, 330, 400, 500, 510, 520}


def create_all_datasets():
    '''
    Creates the parallel dataset, sequential dataset (out of 2 sheets), and the
    auxiliary dataset (with one entry per problem)
    '''
    pass


def create_seq_data(name1,name2):
    values = []
    for name in [name1,name2]:
        csvFilePath = r'./'+name+r'.csv'
        with open(csvFilePath, encoding='utf-8') as csvf:
            csvReader = csv.DictReader(csvf)
            for row in csvReader:
                values.append(row)

    # jsonFilePath = r'./'+name1+r'_raw.json'
    # with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
    #     jsonString = json.dumps(values, indent=4)
    #     jsonf.write(jsonString)

    print(values[0].keys())
    print(values[-1].keys())

    print(len(values))
    wanted_fields_only_values = filter_unwanted_fields_json(values,
                        wanted_fields=SEQUENTIAL_ALGO_FIELDS)
    print(len(wanted_fields_only_values))
    print(wanted_fields_only_values[0].keys())
    print(wanted_fields_only_values[-1].keys())

    discarded_bad_algos_values = filter_unwanted_algos(wanted_fields_only_values,
                        unwanted_values=SEQUENTIAL_DISCARABLE_FIELD_VALUES)
    print(len(discarded_bad_algos_values))
    algos_with_subproblems = consolidate_subproblems(discarded_bad_algos_values)
    print(len(algos_with_subproblems))
    algos_with_names = add_name_field(algos_with_subproblems)
    final_values = type_cast_data(algos_with_names)

    print(str(len(final_values))+" algorithms in the sequential dataset")
    newJsonFilePath = r'./data/seq_data'+VERSION+r'.json'
    with open(newJsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonString = json.dumps(final_values, indent=4)
        jsonf.write(jsonString)


    pass

def create_par_data(name):
    convert_csv_to_json(name)
    apply_various_operations_to_change_the_json_file_so_its_usable(name,
                    wanted_fields=PARALLEL_ALGO_FIELDS,
                    unwanted_values=PARALLEL_DISCARABLE_FIELD_VALUES,
                    allowed_model_list=PARALLEL_ALLOWABLE_MODELS)


def convert_csv_to_json(name):
    jsonArray = []
    csvFilePath = r'./'+name+r'.csv'
    jsonFilePath = r'./'+name+r'_raw.json'
    with open(csvFilePath, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        for row in csvReader:
            jsonArray.append(row)
            # if "Cole & Gooddrich" in row['Algorithm Name']:
            #     print("======================================")
            #     print(row)
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonString = json.dumps(jsonArray, indent=4)
        jsonf.write(jsonString)
    print("Successfuly wrote "+str(len(jsonArray))+" items")

def apply_various_operations_to_change_the_json_file_so_its_usable(name,wanted_fields,unwanted_values,allowed_model_list):
    '''
    Creates the datasets in their analyzable form
    '''
    jsonFilePath = r'./'+name+r'_raw.json'
    jsonFile = open(jsonFilePath, 'r')
    values = json.load(jsonFile)

    wanted_fields_only_values = filter_unwanted_fields_json(values, wanted_fields)
    print("FILTER UNDWANTED FIELDS ONLY VALUES DONE")

    discarded_bad_algos_values = filter_unwanted_algos(wanted_fields_only_values, unwanted_values)
    print("FILTER UNDWANTED ALGOS DONE")

    # one_var_per_algo_values, vars = separate_variations(discarded_bad_algos_values)
    algos_with_final_subproblems = consolidate_subproblems(discarded_bad_algos_values)
    print("ALGOS WITH FINAL SUBPROBLEMS DONE")

    algos_with_names = add_name_field(algos_with_final_subproblems)
    final_values = type_cast_data(algos_with_names)
    print("TYPE CAST DATA DONE")

    # make the "original" dataset with only meaningful models (no other or distributed memory)
    meaningful_models_values = remove_nonspecific_models(final_values,allowed_model_list)
    print(str(len(meaningful_models_values))+" algorithms in the original dataset")
    newJsonFilePath = './data/par_algos_original'+VERSION+'.json'
    print("file path: ",newJsonFilePath)
    with open(newJsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonString = json.dumps(meaningful_models_values, indent=4)
        jsonf.write(jsonString)

    # make the "simulated" dataset with all algorithms simulated onto the main model
    simulated_algorithms_values = simulate_models(final_values)
    print(str(len(simulated_algorithms_values))+" algorithms in the simulated dataset")
    newJsonFilePath = './data/par_algos_simulated'+VERSION+'.json'
    with open(newJsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonString = json.dumps(simulated_algorithms_values, indent=4)
        jsonf.write(jsonString)


def filter_unwanted_fields_json(values, wanted_fields):
    '''
    discards any field not in wanted_fields, and renames the fields according
    to the their value

    name: name of the csv file
    wanted_fields: dictionary mapping wanted fields to their preferred name
    '''
    # jsonFilePath = r'./'+name+r'_raw.json'
    # jsonFile = open(jsonFilePath, 'r')
    # values = json.load(jsonFile)
    new_values = []
    for element in values:
        # if element["Algo ID"]=='9':
        #     print(element)
        new_element = {}
        for key in element:
            if key in wanted_fields:
                new_element[wanted_fields[key]] = element[key]
        new_values.append(new_element)

    return new_values
    # newJsonFilePath = r'./fields_'+name+r'.json'
    # with open(newJsonFilePath, 'w', encoding='utf-8') as jsonf:
    #     jsonString = json.dumps(new_values, indent=4)
    #     jsonf.write(jsonString)

def filter_unwanted_algos(values, unwanted_values):
    '''
    discards any algorithm with one or more unvalid fields (as specified by the
    unwanted_values input dictionary)
    '''
    # jsonFilePath = r'./fields_'+name+r'.json'
    # jsonFile = open(jsonFilePath, 'r')
    # values = json.load(jsonFile)

    new_values = copy.deepcopy(values)

    removed_stats = {}
    for field in unwanted_values:
        removed_stats[field] = 0
    for i in reversed(range(len(values))):
        element = values[i]
        for field in unwanted_values:
            print("element ",element)
            #its taking "values" as just the name of the csv :(
            print("unwanted values ", unwanted_values)
            print("field", field)

            if element[field] in unwanted_values[field]:
                new_values.pop(i)
                removed_stats[field] += 1

            # if element[field] == unwanted_values[field]:
            #     new_values.pop(i)
            #     removed_stats[field] += 1
            # #deal w/ xxx xxxx and yy (and also an error where they are "")
            # elif (element["span"] == "xxxx" or element["span"] == "xxx" or element["span"] == "yy" or element["span"] == "" or element["span"] == " "):
            #     new_values.pop(i)
            #     removed_stats["span"] += 1
            # elif (element["work"] == "xxxx" or element["work"] == "xxx" or element["work"] == "yy"):
            #     new_values.pop(i)
            #     removed_stats["work"] += 1
            # #checking if these will fix an error im getting :(
            # elif (element["model"] == "" or element["model"] == " "):
            #     new_values.pop(i)
            #     removed_stats["model"] += 1
            # elif (element["par"] == "" or element["par"] == " "):
            #     new_values.pop(i)
            #     removed_stats["par"] += 1
            # #removing double encoded models for now
            # elif (";" in element["model"]):
            #     new_values.pop(i)
            #     removed_stats["model"] += 1
            # elif (element["problem"]=="#N/A"):
            #     new_values.pop(i)
            #     removed_stats["problem"] += 1
                break

    return new_values

def consolidate_subproblems(values):
    '''
    TODO
    '''
    warnings.warn("Warning...........Subproblems not consolidated!") #what was the thought process here?
    problem_set = set()
    for val in values:
        problem_set.add(val["problem"])
    # print("LIST OF CURRENT PROBLEMS ("+str(len(values))+")")
    # for prob in problem_set:
    #     print(prob)
    return values



def separate_variations(values):
    '''
    For each problem, chooses the most frequent variation as its canonical one
    Discards algorithms not solving their canonical variation, sets "vars" to it 
    '''
    # jsonFilePath = r'./analyzable_'+name+r'.json'
    # jsonFile = open(jsonFilePath, 'r')
    # values = json.load(jsonFile)
    new_values = []

    problems = {}
    for element in values:
        problems[element["problem"]] = None

    for problem in problems:
        # getting the most frequent variation
        var_dict = {}
        for element in values:
            if element["problem"] == problem:
                # get the variations and update counts
                vars = element["vars"].replace(" ", "").split(";")
                for var in set(vars):
                    if var in var_dict:
                        var_dict[var] += 1
                    else:
                        var_dict[var] = 1
        freq_var = max(var_dict, key=var_dict.get)
        problems[element["problem"]] = freq_var

        # including algorithms for the most frequent variation
        for element in values:
            if element["problem"] == problem and freq_var in element["vars"]:
                new_values.append(copy.deepcopy(element))
                new_values[-1]["vars"] = freq_var

    return new_values, problems

def type_cast_data(values):
    '''
    type casting should be the last operation performed during data cleanup
    '''
    new_values = copy.deepcopy(values)
    # print(type(new_values))
    # print(len(new_values))
    # print(new_values[1])
    # print(new_values[0][0])

    for i in reversed(range(len(new_values))):
        element = new_values[i]
        deleted=False
        for field in ["year","model"]:
            if field in element:
                # print("field in element")
                if element[field] == '-':
                    # print("dash")
                    del new_values[i]
                    deleted=True
                    break
                else:
                    print("element[field] ",element[field])
                    print("field: ",field)
                    #tripping over model="" which is weird since it should be filtered out i think??
                    #seems ti be fixed by specifically filtering out models that are "" and " " ??
                    element[field] = int(element[field])
        if deleted==True: break
        for field in ["span","work","par","time"]:
            if field in element:
                if element[field] == '-':
                    # print("dash")
                    del new_values[i]
                    break
                print("element[field] ",element[field])
                print("field: ",field)
                #same issues of "" values :( (did specific filtering above)
                #also oh no there are models with value; value. need to fix
                element[field] = float(element[field])

    return new_values

def add_name_field(values):
    new_values = []
    for element in values:
        new_values.append(copy.deepcopy(element))
        # if "family" not in element:
        #     print(element)
        new_name = element["family"]+element["id"]+element["auth"]+" ("+str(element["year"])+")"
        new_values[-1]["name"] = new_name
    return new_values


def remove_nonspecific_models(values,allowed_model_list):
    '''
    removes models we don't care about
    '''
    new_values = []
    for element in values:
        if element["model"] in allowed_model_list:
            new_values.append(copy.deepcopy(element))
    return new_values

def simulate_models(values):
    new_allowable_models = PARALLEL_ALLOWABLE_MODELS.copy()
    new_allowable_models.add(700)
    return remove_nonspecific_models(values,new_allowable_models)

    return
    SIM_TABLE = {
    100: "PRAM",
    110: "PRAM-EREW",
    120: "PRAM-CREW",
    130: "PRAM-CRCW",
    131: "PRAM-CRCW-ARBITRARY",
    132: "PRAM-CRCW-COMMON",
    133: "PRAM-CRCW-PRIORITY",
    135: "Probabilistic PRAM-CRCW",
    200: "SIMD-SM",
    210: "SIMD-SM-R",
    220: "SIMD-SM-RW",
    300: "MIMD-TC",
    310: "MIMD-TC EREW",
    320: "MIMD-TC CREW",
    330: "MIMD-TC CRCW",
    400: "BSP",
    500: "Comparator Circuits",
    510: "Sorting Network",
    520: "Hardware Sorter",
    700: "Distributed Memory"
    } # this should be in the header doc, along with MAIN_MODEL

    # message passing

    new_values = []
    for element in values:
        if element["model"] == MAIN_MODEL:
            new_values.append(copy.deepcopy(element))
            new_values[-1]["sim"] = 0
            new_name = element["vars"]+element["id"]+element["auth"]+" ("+str(element["year"])+")"
            new_values[-1]["name"] = new_name
        else:
            old_model = element["model"]
            if old_model in SIM_TABLE:
                new_values.append(copy.deepcopy(element))

                new_values[-1]["span"] = element["span"]
                new_values[-1]["work"] = element["work"]
                new_values[-1]["par"] = element["par"]

                # new_values[-1]["span"] = SIM_TABLE[old_model]["span"](element["span"])
                # new_values[-1]["work"] = SIM_TABLE[old_model]["work"](element["work"])
                # new_values[-1]["par"] = SIM_TABLE[old_model]["par"](element["par"])

                new_values[-1]["sim"] = 1
                new_values[-1]["model"] = MAIN_MODEL
                new_name = element["vars"]+element["id"]+element["auth"]+" ("+str(element["year"])+")"
                new_values[-1]["name"] = new_name

    return new_values



def make_full_dataset(parallel_data_name, sequential_data):
    jsonFilePath = r'./'+parallel_data_name+r'_raw.json'
    jsonFile = open(jsonFilePath, 'r')
    values = json.load(jsonFile)
    new_values=copy.deepcopy(values)




    newJsonFilePath = './data/full_algos_(simulated)'+VERSION+'.json'
    with open(newJsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonString = json.dumps(new_values, indent=4)
        jsonf.write(jsonString)
    pass


if __name__ == '__main__':
    # convert_csv_to_json("Parallel_Algos_MAY1")
    # filter_unwanted_fields_json("Parallel_Algos_MAY1",PARALLEL_ALGO_FIELDS)
    # filter_unwanted_algos("Parallel_Algos_MAY1",PARALLEL_DISCARABLE_FIELD_VALUES)

    #wut?^^^^

    create_par_data("Parallel_Algos_JUL21")
    print("DONE WITH PARALLEL")
    #technically should probably use this one but im just copying the old ones and changing the version name
    create_seq_data("Sheet1_JUL21","Sheet1_New_Entries_JUL21")

    pass
