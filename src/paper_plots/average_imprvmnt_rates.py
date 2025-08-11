from header import *
from src.thesis_plots.relative_speedup import *
import seaborn as sns
import matplotlib.cm as cm
import numpy as np
from matplotlib.patches import FancyArrowPatch
import math
import copy
import bisect
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# dataset: main model simulation


################################################################################
########### Average yearly improvement rate ####################################
################################################################################

# Distribution of average yearly improvement rates (original paper figure 3)



def yearly_impr_rate_histo_grid(data,raw_buckets,n_values=[10**3,10**6,10**9],
                                p_values=[8,10**3,10**6],measure="rt"):
    fig, ax = plt.subplots(len(p_values),len(n_values),figsize=(7,7),dpi=200,layout='tight',sharey='all')

    for i in range(len(p_values)):
        p = p_values[i]
        for j in range(len(n_values)):
            n = n_values[j]
            yearly_impr_rate_histo_helper(ax[i,j],data,raw_buckets,n,p,measure=measure)
            # ax[i,j].set_title("$n="+get_nice_n(n)+"$ \# processors = "+get_nice_n(p)+"$")

    labels = [raw_buckets[i]["label"] for i in range(len(raw_buckets))]
    for j in range(len(n_values)):
        ax[len(p_values)-1,j].set_xticks(list(range(len(labels))),labels=labels, rotation=90)
        for i in range(len(p_values)-1):
            ax[i,j].get_xaxis().set_visible(False)

    # max_y_lim = max(ax[i,k].get_ylim() for i in range(len(p_values)) for k in range(len(n_values)))
    # print(max_y_lim)
    for i in range(len(p_values)):
        ax[i,0].yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0f%%'))
        for j in range(1,len(n_values)):
            # ax[i,j].set_ylim(max_y_lim)
            ax[i,j].get_yaxis().set_visible(False)


    ax[0,0].set_title("Problem size ($n$) =\n"+long_human_format(n_values[0]))
    ax[0,1].set_title("Problem size ($n$) =\n"+long_human_format(n_values[1]))
    ax[0,2].set_title("Problem size ($n$) =\n"+long_human_format(n_values[2]))
    ax[0,0].set_ylabel("# processors = \n"+long_human_format(p_values[0]))
    ax[1,0].set_ylabel("# processors = \n"+long_human_format(p_values[1]))
    ax[2,0].set_ylabel("# processors = \n"+long_human_format(p_values[2]))

    fig.suptitle("Algorithm Problem Average Yearly Improvement Rate\n(Sequential and Parallel)")
    fig.supxlabel("Average Yearly Improvement Rate")
    fig.supylabel("Number of Problems")

    plt.savefig(SAVE_LOC+'average_improvement_rate.png')
    # plt.show()

# requires at least 2 buckets
# used_measure can be either "rt" (running time) or "sp" (span)
def yearly_impr_rate_histo(data, raw_buckets, n,p, measure="rt"):

    fig, axis = plt.subplots(1,1)
    yearly_impr_rate_histo_helper(axis,data, raw_buckets, n,p, measure=measure)

    labels = [raw_buckets[i]["label"] for i in range(len(raw_buckets))]
    axis.set_xticks(list(range(len(labels))),labels=labels, rotation=90)
    # nice_n = "$10^"+str(int(math.log(n,10)+1))+"$"
    # ax.set_title("Distribution of average yearly improvement rates\nfor n = "+nice_n+" and p = "+str(p))
    axis.set_title("Distribution of average yearly improvement rates\nfor n = "+str(n))
    plt.show()


# requires at least 2 buckets
# measure can be either "rt" (running time) or "sp" (span)
def yearly_impr_rate_histo_helper(ax,data, raw_buckets, n, p, measure="rt"):
    assert measure == "sp" or measure == "rt"
    def get_measure_value(measure,work,span,n,p):
        '''
        returns running time (if measure is "rt") or span
        :measure: either "sp" for span or "rt" for runtime
        TODO
        '''
        if measure == "sp":
            return get_comp_fn(span)(n)
        elif measure == "rt":
            return get_runtime(work,span,n,p)

    # sort the algos based on increasing year, then based on decreasing span
    names = list(data.keys())
    # if measure == "rt":
    #     names.sort(key= lambda name: (data[name]["year"], -1*data[name]["work"]))
    #     # names.sort(key= lambda name: (data[name]["year"], -1*get_runtime(data[name]["work"],data[name]["span"],n,p)))
    # else:
    names.sort(key= lambda name: (data[name]["year"], -1*data[name]["span"]))
    print("finished sorting")

    worst_algs = {} # dict of problems started and their worst alg found
    all_rates = []
    for name in names:
        algo = data[name]
        if algo["problem"] not in worst_algs:
            worst_algs[algo["problem"]] = name
        else:
            worst = data[worst_algs[algo["problem"]]]
            algo_rt = get_measure_value(measure, algo["work"], algo["span"],n,p)
            worst_rt = get_measure_value(measure, worst["work"], worst["span"],n,p)
            # only consider legal algorithms (with a valid rate of improvement)
            if algo["year"] > worst["year"] and algo_rt <= worst_rt:
                impr_ratio = worst_rt / algo_rt
                yearly_impr_rate = impr_ratio ** (1/(algo["year"]-worst["year"]))-1
                all_rates.append(yearly_impr_rate)

    print("finished finding worst algos")

    # find the distribution values to be plotted
    buckets = copy.deepcopy(raw_buckets)
    assert len(buckets) >= 2
    all_rates.sort()
    # print(all_rates) # (11x0.0) 14, 9, 6, 2, 3, 3, 2, 1, 1, 1, 4, 0
    buckets[0]["index"] = bisect.bisect_left(all_rates, buckets[0]["max"])
    buckets[0]["count"] = buckets[0]["index"]
    for i in range(1,len(buckets)-1):
        max_val = buckets[i]["max"]
        buckets[i]["index"] = bisect.bisect_left(all_rates, max_val)
        buckets[i]["count"] = buckets[i]["index"] - buckets[i-1]["index"]
    buckets[-1]["count"] = len(all_rates) - buckets[-2]["index"]
    for i in range(len(buckets)):
        buckets[i]["share"] = buckets[i]["count"] / len(all_rates)

    print("finished finding the distribution")

    # drawing the distribution histogram
    values = [buckets[i]["share"]*100 for i in range(len(buckets))]
    ax.bar(list(range(len(buckets))), values, align='center')


g_buckets = [{"max": 0.1, "label": "0-10%"},
            {"max": 0.2, "label": "10-20%"},
            {"max": 0.3, "label": "20-30%"},
            {"max": math.inf, "label": ">30%"},]

many_g_buckets = [{"max": 0.1, "label": "0-10%"},
            {"max": 0.2, "label": "10-20%"},
            {"max": 0.3, "label": "20-30%"},
            {"max": 0.4, "label": "30-40%"},
            {"max": 0.5, "label": "40-50%"},
            {"max": 0.6, "label": "50-60%"},
            {"max": 0.7, "label": "60-70%"},
            {"max": 0.8, "label": "70-80%"},
            {"max": 0.9, "label": "80-90%"},
            {"max": 1, "label": "90-100%"},
            {"max": 10, "label": "100-1000%"},
            {"max": math.inf, "label": ">1000%"},]

# yearly_impr_rate_histo(full_data, g_buckets, 10**3)

def improvements(data, n=10**3,p=8,lower=False):
    """
    Finds the best algorithms for every year for each aspect out of span, work,
    and runtime. If there are ties, an arbitrary algorithm is returned.

    :data: dataset to be used (*simulated* parallel)
    :n: problem size for runtime calculation
    :p: number of processors for runtime calculation
    :returns: best_stats - dict by problem of dict by year of {"bs alg": name, 
                            "bw alg": name, "br alg": name}
                            (bs = span, bw = work, br = running time)
    """
    # Initialize best_stats with empty dictionaries
    best_stats = {}
    for prob in set(alg["problem"] for alg in data.values()):
        best_stats[prob] = {}
        for year in range(CUR_YEAR + 1):
            best_stats[prob][year] = {
                "bs alg": None,
                "bw alg": None,
                "br alg": None
            }
    """
    Finds the best algorithms for every year for each aspect out of span, work,
    and runtime. If there are ties, an arbitrary algorithm is returned.

    :data: dataset to be used (*simulated* parallel)
    :n: problem size for runtime calculation
    :p: number of processors for runtime calculation
    :returns: best_stats - dict by problem of dict by year of {"bs alg": name, 
                            "bw alg": name, "br alg": name}
                            (bs = span, bw = work, br = running time)
              first_stats - dict mapping problem to name of its first algorithm
    """
    # sort the algos based on increasing year, then based on decreasing span
    names = list(data.keys())
    names.sort(key= lambda name: (data[name]["year"], -1*data[name]["span"]))

    first_year = data[names[0]]["year"]

    probs = get_problems(data)
    best_stats = {}
    for prob in probs:
        best_stats[prob] = {}
        for year in range(first_year,CUR_YEAR+1):
            best_stats[prob][year] = {"bs alg": None, "bw alg": None, "br alg": None}
    first_stats = {} # for every problem, keeps track of its first algo

    y = first_year
    alg_i = 0
    while y <= CUR_YEAR+1 and alg_i <= len(names):
        if alg_i < len(names):
            name = names[alg_i]
            year = data[name]["year"]
        else:
            year = CUR_YEAR+1
        while y < year:
            # update all remaining problems
            for prob in probs:
                if best_stats[prob][y]["bs alg"] is None and y>first_year:
                    best_stats[prob][y]["bs alg"] = best_stats[prob][y-1]["bs alg"]
                if best_stats[prob][y]["bw alg"] is None and y>first_year:
                    best_stats[prob][y]["bw alg"] = best_stats[prob][y-1]["bw alg"]
                if best_stats[prob][y]["br alg"] is None and y>first_year:
                    best_stats[prob][y]["br alg"] = best_stats[prob][y-1]["br alg"]
            y += 1
        assert y == year
        if y == CUR_YEAR+1:
            break

        prob = data[name]["problem"]
        # initialize if it's the first algorithm
        if year == first_year or best_stats[prob][year-1]["bs alg"] is None:
            best_stats[prob][year]["bs alg"] = name
            best_stats[prob][year]["bw alg"] = name
            best_stats[prob][year]["br alg"] = name
            first_stats[prob] = name

        # update the best span algorithm if necessary
        #this is using best asymptotic span :(
        # if best_stats[prob][year]["bs alg"] is None:
        #     best_span = data[best_stats[prob][year-1]["bs alg"]]["span"]
        # else:
        #     best_span = data[best_stats[prob][year]["bs alg"]]["span"]
        # if data[name]["span"] < best_span:
        #     best_stats[prob][year]["bs alg"] = name
        #this takes best span according to n
        if best_stats[prob][year]["bs alg"] is None:
            best_span = get_seq_runtime(data[best_stats[prob][year-1]["bs alg"]]["span"],n)
        else:
            best_span = get_seq_runtime(data[best_stats[prob][year]["bs alg"]]["span"],n)
        if get_seq_runtime(data[name]["span"],n) < best_span:
            best_stats[prob][year]["bs alg"] = name


        # update the best work algorithm if necessary
        # takes best work asymptotically and uh, not what we want!!! (i think)
        # if best_stats[prob][year]["bw alg"] is None:
        #     best_work = data[best_stats[prob][year-1]["bw alg"]]["work"]
        # else:
        #     best_work = data[best_stats[prob][year]["bw alg"]]["work"]
        # if data[name]["work"] < best_work:
        #     best_stats[prob][year]["bw alg"] = name
        #now does it with the numbers we plug in
        if best_stats[prob][year]["bw alg"] is None:
            best_work = get_seq_runtime(data[best_stats[prob][year-1]["bw alg"]]["work"],n)
        else:
            best_work = get_seq_runtime(data[best_stats[prob][year]["bw alg"]]["work"],n)
        if get_seq_runtime(data[name]["work"],n) < best_work:
            best_stats[prob][year]["bw alg"] = name

        # update the best running time algorithm if necessary
        try:
            if best_stats[prob][year]["br alg"] is None:
                old_name = best_stats[prob][year-1]["br alg"]
                if old_name is None:
                    print(f"Warning: No previous algorithm found for {prob} in year {year}")
                    continue
                if old_name not in data:
                    print(f"Warning: Algorithm {old_name} not found in data")
                    continue
                wk = data[old_name]["work"]
                sp = data[old_name]["span"]
                best_runtime = get_runtime(wk, sp, n, p, lower=lower)
            else:
                old_name = best_stats[prob][year]["br alg"]
                if old_name not in data:
                    print(f"Warning: Algorithm {old_name} not found in data")
                    continue
                if "parallel" not in data[old_name]:
                    print(f"Missing parallel field for algorithm: {old_name}")
                    print(f"Available fields: {list(data[old_name].keys())}")
                wk = data[old_name]["work"]
                sp = data[old_name]["span"]
                best_runtime = get_runtime(wk, sp, n, p, lower=lower)
        except KeyError as e:
            print(f"KeyError in improvements: {e}")
            print(f"Algorithm causing error: {old_name}")
            print(f"Available fields: {list(data[old_name].keys()) if old_name in data else 'Not found'}")
            continue
        except Exception as e:
            print(f"Unexpected error in improvements: {e}")
            continue

        try:
            wk = data[name]["work"]
            sp = data[name]["span"]
            if "parallel" not in data[name]:
                print(f"Missing parallel field for algorithm: {name}")
                print(f"Available fields: {list(data[name].keys())}")
            cur_runtime = get_runtime(wk,sp,n,p,lower=lower)
            if cur_runtime < best_runtime:
                best_stats[prob][year]["br alg"] = name
        except KeyError as e:
            print(f"KeyError in improvements: {e}")
            print(f"Algorithm causing error: {name}")
            print(f"Available fields: {list(data[name].keys())}")

        alg_i += 1

    return best_stats, first_stats


def first_seq_names(data):
    '''returns: first_algos: dictionary by problem of algorithm names for the 1st algo of that problem'''
    #sort em
    #going to assume that first algo is the worst one, if multiple in one year
    names = list(data.keys())
    names.sort(key= lambda name: (data[name]["year"], -1*data[name]["time"]))
    first_algos={}
    #go through all, if no algo for problem yet, add it
    for algo in names:
        prob=data[algo]["problem"]
        if prob not in first_algos.keys():
            first_algos[prob]=algo
    return first_algos

def best_seq_names(data):
    '''returns: best_algos: dictionary by problem of algorithm names for the first best algo (by runtime) of that problem'''
    #sort em
    names = list(data.keys())
    #names.sort(key= lambda name: 1*data[name]["time"])
    #changing it so that if multiple best algos then we take the earliest one
    names.sort(key= lambda name: (data[name]["time"],data[name]["year"]))
    best_algos={}
    #go through all, if no algo for problem yet, add it
    # saveable={} #this was to test stuff
    for algo in names:
        prob=data[algo]["problem"]
        if prob not in best_algos.keys():
            best_algos[prob]=algo
    #         saveable[algo]=("BEST",prob,data[algo]["time"],data[algo]["year"])
    #     else:
    #         saveable[algo]=(prob,data[algo]["time"],data[algo]["year"])
    # with open("best_seq.json", "w") as json_file:
    #     json.dump(saveable, json_file, indent=4)
    return best_algos



#new improvement rate graph function
def NEW_yearly_impr_rate_histo_grid(par_data, seq_data, raw_buckets,n_values=[10**3,10**6,10**9],
                                p_values=[8,10**3,10**6],measure="rt",start_from="first_seq"):
    fig, ax = plt.subplots(len(p_values),len(n_values),figsize=(7,7),dpi=200,layout='tight',sharey='all')
    #got mad about argument "layout"
    #fig, ax = plt.subplots(len(p_values),len(n_values),figsize=(7,7),dpi=200, sharey='all')

    for i in range(len(p_values)):
        p = p_values[i]
        for j in range(len(n_values)):
            n = n_values[j]
            if (start_from=="stacked"):
                stacked_impr_rate_histo_helper(ax[i,j],par_data,seq_data,raw_buckets,n,p,measure=measure)
            elif(measure=="work"):
                WORK_impr_rate_histo_helper(ax[i,j],par_data,seq_data,raw_buckets,n,p)
            else:
                NEW_yearly_impr_rate_histo_helper(ax[i,j],par_data,seq_data,raw_buckets,n,p,measure=measure,start_from=start_from)
            # ax[i,j].set_title("$n="+get_nice_n(n)+"$ \# processors = "+get_nice_n(p)+"$")

    labels = [raw_buckets[i]["label"] for i in range(len(raw_buckets))]
    for j in range(len(n_values)):
        ax[len(p_values)-1,j].set_xticks(list(range(len(labels))),labels=labels, rotation=90)
        #ax[len(p_values)-1,j].set_xticks(list(range(len(labels))), rotation=90)

        for i in range(len(p_values)-1):
            ax[i,j].get_xaxis().set_visible(False)

    # max_y_lim = max(ax[i,k].get_ylim() for i in range(len(p_values)) for k in range(len(n_values)))
    # print(max_y_lim)
    for i in range(len(p_values)):
        ax[i,0].yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0f%%'))
        for j in range(1,len(n_values)):
            # ax[i,j].set_ylim(max_y_lim)
            ax[i,j].get_yaxis().set_visible(False)


    ax[0,0].set_title("Problem size ($n$) =\n"+long_human_format(n_values[0]))
    ax[0,1].set_title("Problem size ($n$) =\n"+long_human_format(n_values[1]))
    ax[0,2].set_title("Problem size ($n$) =\n"+long_human_format(n_values[2]))
    # ax[0,0].set_ylabel("# processors = \n"+long_human_format(p_values[0]))
    # ax[1,0].set_ylabel("# processors = \n"+long_human_format(p_values[1]))
    # ax[2,0].set_ylabel("# processors = \n"+long_human_format(p_values[2]))
    ax[0,0].set_ylabel(long_human_format(p_values[0])+" processors")
    ax[1,0].set_ylabel(long_human_format(p_values[1])+" processors")
    ax[2,0].set_ylabel(long_human_format(p_values[2])+" processors")

    fig.suptitle("Algorithm Problem Average Yearly Improvement Rate\n(Sequential and Parallel)\n"+start_from)

    plt.savefig(SAVE_LOC+start_from+'_NEW_average_improvement_rate.png')
    # plt.show()

#requires at least 2 buckets
# measure can be either "rt" (running time) or "sp" (span)
#well, actually rn it's expecting runtime
def NEW_yearly_impr_rate_histo_helper(ax,par_data,seq_data, raw_buckets, n, p, measure="rt",start_from="first_seq"):
    assert measure == "sp" or measure == "rt"
    def get_measure_value(measure,work,span,n,p):
        '''
        returns running time (if measure is "rt") or span
        :measure: either "sp" for span or "rt" for runtime
        TODO
        '''
        if measure == "sp":
            return get_comp_fn(span)(n)
        elif measure == "rt":
            return get_runtime(work,span,n,p)

    # sort the algos based on increasing year, then based on decreasing span
    #we do a bunch of sorting elsewhere, idt this is needed
    # names = list(par_data.keys())
    # names.sort(key= lambda name: (par_data[name]["year"], -1*par_data[name]["span"]))
    # print("finished sorting")

    #best=smallest run time for the problem size and processor number

    all_rates = []
    problems=get_problems(par_data) #takes problems from parallel data, do we want ALL problems instead?
    best_stats, first_stats=improvements(par_data,n,p)
    #get best sequential algos
    best_seq=best_seq_names(seq_data)
    if (start_from=="first_seq"):
        #get first sequential algos
        start_algos=first_seq_names(seq_data)
        start_data=seq_data
    elif (start_from=="best_seq"):
        #use best sequential algos
        start_algos=best_seq
        start_data=seq_data
    else:
        #use first parallel
        start_algos=first_stats
        start_data=par_data
    print("n= ",n," p= ",p)
    for problem in problems:

        if problem in start_algos.keys():
            #take 1st chronological algo
            first=start_algos[problem]
            #^format example is "44658Narayanaswami (1996)"
            first_algo=start_data[first]
            if (start_from=="first_par"):
                first_rt = get_measure_value(measure, first_algo["work"], first_algo["span"],n,p)
            else:
                first_algo_time=first_algo["time"]
                first_rt = get_seq_runtime(first_algo_time,n)
        else:
            first=first_stats[problem]
            #^format example is "44658Narayanaswami (1996)"
            first_algo=par_data[first]
            first_rt = get_measure_value(measure, first_algo["work"], first_algo["span"],n,p)
        #take best algo
        best=best_stats[problem][2024]["br alg"] #taking br here insetad of bs
        best_algo=par_data[best]
        best_rt = get_measure_value(measure, best_algo["work"], best_algo["span"],n,p)
        #print("problem: ",problem)
        #print("best rate: ", best_rt, " first rate: ", first_rt)
        #i guess sometimes the parallel algos are worse than the sequential ones (nash equillibria you bastard)
        #should probably take the best sequential improvement then
        #honestly, do i have a dataset with everything in it? that would make all this simpler - something to think about
        # if (first_rt<best_rt):
        #     impr_ratio=1
        # else:
        #     impr_ratio = first_rt / best_rt
        if (first_rt<best_rt):
            if problem not in best_seq.keys():
                #idk how this scenario would happen
                #HELP
                print("PROBLEM NOT IN SEQ ALGOS BUT BEST RT WORSE THAN FIRST RT")
                best_rt=first_rt
            else:
                best=best_seq[problem]
                best_algo=seq_data[best]
                best_algo_time=best_algo["time"]
                best_rt=get_seq_runtime(best_algo_time,n)
        impr_ratio = first_rt / best_rt
        #print("improvement ratio: ", impr_ratio)
        #delta t is from first seq to now (2025)
        #print(first_algo["year"])
        #print(impr_ratio)
        #print(impr_ratio ** (1/(2025-first_algo["year"])))

        if (first_algo["year"]>best_algo["year"]):
            print("first algo year: ",first_algo["year"], "best algo year: ", best_algo["year"])
            print("problem: ", problem)
        #double check formula!!
        yearly_impr_rate = impr_ratio ** (1/(2025-first_algo["year"]))-1
        all_rates.append(yearly_impr_rate)

    print("finished finding improvement rates")

    # find the distribution values to be plotted
    buckets = copy.deepcopy(raw_buckets)
    assert len(buckets) >= 2
    all_rates.sort()
    # print(all_rates) # (11x0.0) 14, 9, 6, 2, 3, 3, 2, 1, 1, 1, 4, 0

    buckets[0]["index"] = bisect.bisect_left(all_rates, buckets[0]["max"])
    buckets[0]["count"] = buckets[0]["index"]
    for i in range(1,len(buckets)-1):
        max_val = buckets[i]["max"]
        buckets[i]["index"] = bisect.bisect_left(all_rates, max_val)
        buckets[i]["count"] = buckets[i]["index"] - buckets[i-1]["index"]
    buckets[-1]["count"] = len(all_rates) - buckets[-2]["index"]
    for i in range(len(buckets)):
        buckets[i]["share"] = buckets[i]["count"] / len(all_rates)

    print("finished finding the distribution")
    #this section will make orange bar of 0s
    # zero_count = all_rates.count(0)  #how many 0s
    # first_bucket_count = buckets[0]["count"] #how many in 1st bucket
    # proportion_of_zero = zero_count / first_bucket_count #proportion


    # zero_share = proportion_of_zero * buckets[0]["share"]*100  #percentage of 0 values
    # non_zero_share = 100*buckets[0]["share"] - zero_share  #remaining portion of the bucket

    # # drawing the distribution histogram

    # #plot 1st bar
    # ax.bar(0, non_zero_share,  color='tab:blue', align='center')
    # ax.bar(0, zero_share, bottom=non_zero_share, color='tab:orange', label="0s", align='center')
    # #plot the others
    # for i in range(1, len(buckets)):
    #     values = buckets[i]["share"] * 100
    #     ax.bar(i, values, color='tab:blue', align='center')
    # ax.legend()

    #this makes buckets w/o the 1st one highlighting 0s
    values = [buckets[i]["share"]*100 for i in range(len(buckets))]
    ax.bar(list(range(len(buckets))), values, align='center')


def stacked_impr_rate_histo_helper(ax,par_data,seq_data, raw_buckets, n, p, measure="rt"):
    assert measure == "sp" or measure == "rt"
    def get_measure_value(measure,work,span,n,p):
        '''
        returns running time (if measure is "rt") or span
        :measure: either "sp" for span or "rt" for runtime
        TODO
        '''
        if measure == "sp":
            return get_comp_fn(span)(n)
        elif measure == "rt":
            return get_runtime(work,span,n,p)

    # sort the algos based on increasing year, then based on decreasing span
    names = list(par_data.keys())
    names.sort(key= lambda name: (par_data[name]["year"], -1*par_data[name]["span"]))
    print("finished sorting")


    par_rates = []
    seq_rates =[]
    problems=get_problems(par_data) #takes problems from parallel data, do we want ALL problems instead?
    best_stats, first_stats=improvements(par_data,n,p)
    best_seq=best_seq_names(seq_data)
    first_seq=first_seq_names(seq_data)

    for problem in problems:
        #take 1st chronological seq algo if it exists for problem
        if problem in first_seq.keys():
            first=first_seq[problem]
            first_algo=seq_data[first]
            first_algo_time=first_algo["time"]
            first_rt = get_seq_runtime(first_algo_time,n)
        else:
            first_rt=-1
            # first=first_stats[problem]
            # #^format example is "44658Narayanaswami (1996)"
            # first_algo=par_data[first]
            # first_rt = get_measure_value(measure, first_algo["work"], first_algo["span"],n,p)
        #take best seq algo
        if (first_rt!=-1):
            best_seq_algo_name=best_seq[problem]
            best_seq_algo=seq_data[best_seq_algo_name]
            best_seq_time=best_seq_algo["time"]
            best_seq_rt = get_seq_runtime(best_seq_time,n)
            seq_impr_ratio=first_rt/best_seq_rt
            #seq_yearly_impr_rate = seq_impr_ratio ** (1/(best_seq_algo["year"]-first_algo["year"]))-1
            seq_yearly_impr_rate = seq_impr_ratio ** (1/(2025-first_algo["year"]))-1
        else:
            #idk how to deal w/ otherwise
            seq_yearly_impr_rate=0
        seq_rates.append(seq_yearly_impr_rate)

        #now do from best seq or first par to best par
        if (first_rt==-1):
            #take 1st parallel
            first_par_algo_name=first_stats[problem]
            first_par_algo=par_data[first_par_algo_name]
            first_par_rt=get_measure_value(measure, first_par_algo["work"], first_par_algo["span"],n,p)

            best_seq_algo=first_par_algo
            best_seq_rt=first_par_rt
            first_algo=first_par_algo
        best=best_stats[problem][2024]["br alg"]
        best_algo=par_data[best]
        best_rt = get_measure_value(measure, best_algo["work"], best_algo["span"],n,p)

        par_impr_ratio=best_seq_rt/best_rt
        if (par_impr_ratio<1):
            #idk how to fix this :(((((
            par_impr_ratio=1

        #par_yearly_impr_rate = par_impr_ratio ** (1/(2025-best_seq_algo["year"]))-1
        par_yearly_impr_rate = par_impr_ratio ** (1/(2025-first_algo["year"]))-1
        par_rates.append(par_yearly_impr_rate)

    print("finished finding improvement rates")

    # find the distribution values to be plotted
    buckets = copy.deepcopy(raw_buckets)
    assert len(buckets) >= 2

    # Sort the rates
    par_rates.sort()
    seq_rates.sort()

    # Compute bucket counts for both par_rates and seq_rates
    for rates, key in [(par_rates, "par_count"), (seq_rates, "seq_count")]:
        buckets[0]["index"] = bisect.bisect_left(rates, buckets[0]["max"])
        buckets[0][key] = buckets[0]["index"]

        for i in range(1, len(buckets) - 1):
            max_val = buckets[i]["max"]
            buckets[i]["index"] = bisect.bisect_left(rates, max_val)
            buckets[i][key] = buckets[i]["index"] - buckets[i - 1]["index"]

        buckets[-1][key] = len(rates) - buckets[-2]["index"]

    # Compute shares
    for i in range(len(buckets)):
        buckets[i]["par_share"] = buckets[i]["par_count"] / len(par_rates)
        buckets[i]["seq_share"] = buckets[i]["seq_count"] / len(seq_rates)

    print("Finished finding the distribution")

    # Prepare data for plotting
    x = list(range(len(buckets)))
    par_values = [buckets[i]["par_share"] * 100 for i in range(len(buckets))]
    seq_values = [buckets[i]["seq_share"] * 100 for i in range(len(buckets))]
    # Draw histogram with two bars per bucket
    ax.bar(x, seq_values, width=0.4, align='center', label="Seq Rates", alpha=0.7)
    ax.bar([i + 0.4 for i in x], par_values, width=0.4, align='center', label="Par Rates", alpha=0.7)
    ax.legend()


def WORK_impr_rate_histo_helper(ax,par_data,seq_data, raw_buckets, n, p):
    '''NOT FINISHED, NOT EVEN PROPERLY STARTED
    '''
    pass
#get_runtime(work,span,n,p)

#pseudocode
#for each problem
    #take first seq algo
    #what is problem size m if runtime is n?
    #take parallel algo with best span
    #what is runtime with problem size m and processors p
    #get improvement rate



    # sort the algos based on increasing year, then based on decreasing span
    names = list(par_data.keys())
    names.sort(key= lambda name: (par_data[name]["year"], -1*par_data[name]["span"]))
    print("finished sorting")

    #for each problem, takes 1st sequential algo and best parallel algo
    #best=smallest run time for the problem size and processor number

    all_rates = []
    problems=get_problems(par_data) #takes problems from parallel data, do we want ALL problems instead?
    best_stats, first_stats=improvements(par_data,n,p)
    best_seq=best_seq_names(seq_data)
    if (start_from=="first_seq"):
        #get first sequential algos
        start_algos=first_seq_names(seq_data)
        start_data=seq_data
    elif (start_from=="best_seq"):
        #get best sequential algos
        start_algos=best_seq
        start_data=seq_data
    else:
        #use first parallel
        start_algos=first_stats
        start_data=par_data
    for problem in problems:

        if problem in start_algos.keys():
            #take 1st chronological algo
            first=start_algos[problem]
            #^format example is "44658Narayanaswami (1996)"
            first_algo=start_data[first]
            if (start_from=="first_par"):
                first_rt = get_measure_value(measure, first_algo["work"], first_algo["span"],n,p)
            else:
                first_algo_time=first_algo["time"]
                first_rt = get_seq_runtime(first_algo_time,n)
        else:
            first=first_stats[problem]
            #^format example is "44658Narayanaswami (1996)"
            first_algo=par_data[first]
            first_rt = get_measure_value(measure, first_algo["work"], first_algo["span"],n,p)
        #take best algo
        best=best_stats[problem][2024]["bs alg"]
        best_algo=par_data[best]
        best_rt = get_measure_value(measure, best_algo["work"], best_algo["span"],n,p)
        print("problem: ",problem)
        print("best rate: ", best_rt, " first rate: ", first_rt)
        #i guess sometimes the parallel algos are worse than the sequential ones (nash equillibria you bastard)
        #should probably take the best sequential improvement then
        #honestly, do i have a dataset with everything in it? that would make all this simpler - something to think about
        # if (first_rt<best_rt):
        #     impr_ratio=1
        # else:
        #     impr_ratio = first_rt / best_rt
        if (first_rt<best_rt):
            if problem not in best_seq.keys():
                #idk how this scenario would happen
                #HELP
                print("PROBLEM NOT IN SEQ ALGOS BUT BEST RT WORSE THAN FIRST RT")
                best_rt=first_rt
            else:
                best=best_seq[problem]
                best_algo=seq_data[best]
                best_algo_time=best_algo["time"]
                best_rt=get_seq_runtime(best_algo_time,n)
        impr_ratio = first_rt / best_rt
        #print("improvement ratio: ", impr_ratio)
        #delta t is from first seq to now (2025)
        print(first_algo["year"])
        print(impr_ratio)
        print(impr_ratio ** (1/(2025-first_algo["year"])))
        #double check formula!!
        yearly_impr_rate = impr_ratio ** (1/(2025-first_algo["year"]))-1
        all_rates.append(yearly_impr_rate)

    print("finished finding improvement rates")

    # find the distribution values to be plotted
    buckets = copy.deepcopy(raw_buckets)
    assert len(buckets) >= 2
    all_rates.sort()
    # print(all_rates) # (11x0.0) 14, 9, 6, 2, 3, 3, 2, 1, 1, 1, 4, 0
    buckets[0]["index"] = bisect.bisect_left(all_rates, buckets[0]["max"])
    buckets[0]["count"] = buckets[0]["index"]
    for i in range(1,len(buckets)-1):
        max_val = buckets[i]["max"]
        buckets[i]["index"] = bisect.bisect_left(all_rates, max_val)
        buckets[i]["count"] = buckets[i]["index"] - buckets[i-1]["index"]
    buckets[-1]["count"] = len(all_rates) - buckets[-2]["index"]
    for i in range(len(buckets)):
        buckets[i]["share"] = buckets[i]["count"] / len(all_rates)

    print("finished finding the distribution")

    # drawing the distribution histogram
    values = [buckets[i]["share"]*100 for i in range(len(buckets))]
    ax.bar(list(range(len(buckets))), values, align='center')



def EVERYTHING_yearly_impr_rate_histo_helper(ax,full_data, raw_buckets, n, p, measure="rt"):
    assert measure == "sp" or measure == "rt"
    def get_measure_value(measure,work,span,n,p):
        '''
        returns running time (if measure is "rt") or span
        :measure: either "sp" for span or "rt" for runtime
        TODO
        '''
        if measure == "sp":
            return get_comp_fn(span)(n)
        elif measure == "rt":
            return get_runtime(work,span,n,p)

    #best=smallest run time for the problem size and processor number

    all_rates = []
    problems=get_problems(full_data) #takes all problems
    best_stats, first_stats=improvements(full_data,n,p)
    for problem in problems:
        #first algorithm
        first_algo= first_stats[problem]
        #either sequential or force it to be sequential by p=1
        first_rt = get_measure_value(measure, full_data[first_algo]["work"], full_data[first_algo]["span"],n,1)
        first_year=full_data[first_algo]["year"]

        best_seq_algo = best_stats[problem][2024]["bw alg"]
        best_seq_rt = get_measure_value(measure, full_data[best_seq_algo]["work"],
                                      full_data[best_seq_algo]["span"],n,1)
        first_seq_year = full_data[first_stats[problem]]["year"]

        best_algo = best_stats[problem][2024]["br alg"]
        print(f"Problem: {problem}, Best algo: {best_algo}, Parallel: {full_data[best_algo].get('parallel')}")

        #best algorithm
        best_algo=best_stats[problem][2024]["br alg"]
        #if parallel
        if (full_data[best_algo]["parallel"]==1):
            best_rt = get_measure_value(measure, full_data[best_algo]["work"], full_data[best_algo]["span"],n,p)
            impr_ratio = first_rt / best_rt
            print(f"  Seq RT: {best_seq_rt}, Par RT: {best_rt}, Ratio: {impr_ratio}")
            yearly_impr_rate = impr_ratio ** (1/(2025-first_year))-1
        else: #if no parallel algo
            yearly_impr_rate=0

        # if(p==8 and yearly_impr_rate>10):
        #     print("problem: ",problem, "; first_rt=", first_rt,"; best_rt=", best_rt)

        all_rates.append(yearly_impr_rate)

    print("finished finding improvement rates for n=", n," and p=",p)

    # find the distribution values to be plotted
    buckets = copy.deepcopy(raw_buckets)
    assert len(buckets) >= 2
    all_rates.sort()
    # print(all_rates) # (11x0.0) 14, 9, 6, 2, 3, 3, 2, 1, 1, 1, 4, 0

    buckets[0]["index"] = bisect.bisect_left(all_rates, buckets[0]["max"])
    buckets[0]["count"] = buckets[0]["index"]
    for i in range(1,len(buckets)-1):
        max_val = buckets[i]["max"]
        buckets[i]["index"] = bisect.bisect_left(all_rates, max_val)
        buckets[i]["count"] = buckets[i]["index"] - buckets[i-1]["index"]
    buckets[-1]["count"] = len(all_rates) - buckets[-2]["index"]
    for i in range(len(buckets)):
        buckets[i]["share"] = buckets[i]["count"] / len(all_rates)

    print("finished finding the distribution")
    zero_count = all_rates.count(0)  #how many 0s
    first_bucket_count = buckets[0]["count"] #how many in 1st bucket
    proportion_of_zero = zero_count / first_bucket_count #proportion

    zero_share = proportion_of_zero * buckets[0]["share"]*100  #percentage of 0 values
    non_zero_share = 100*buckets[0]["share"] - zero_share  #remaining portion of the bucket

    # drawing the distribution histogram

    #plot 1st bar
    ax.bar(0, non_zero_share,  color='tab:blue', align='center')
    ax.bar(0, zero_share, bottom=non_zero_share, color='tab:orange', label="0% par impr", align='center')
    ax.text(0, non_zero_share * 1.1, f"{non_zero_share:.1f}%", ha='center', va='bottom', fontsize=5)
    ax.text(0, (non_zero_share + zero_share) * 1.1, f"{zero_share:.1f}%", ha='center', va='bottom', fontsize=5)

    #plot the others
    for i in range(1, len(buckets)):
        values = buckets[i]["share"] * 100
        ax.bar(i, values, color='tab:blue', align='center')
        ax.text(i, values * 1.1, f"{values:.1f}%", ha='center', va='bottom', fontsize=5)


    # #define cut points
    # cut_low = 5  #bottom visible part
    # cut_high = 20  #top visible part

    # # Adjust y-axis to skip the missing section
    # ax.set_yticks(list(range(0, cut_low + 1, 10)) + list(range(cut_high, 101, 10)))  # Skip middle range

    # # Add "break" indicator on y-axis (zigzag or double slashes)
    # ax.spines['left'].set_position(('outward', 10))
    # ax.plot([-0.4, 0.4], [cut_low, cut_low], color='black', lw=1.5, linestyle='--')  # Lower cut
    # ax.plot([-0.4, 0.4], [cut_high, cut_high], color='black', lw=1.5, linestyle='--')  # Upper cut

    if (n==10**9 and p==8):
        ax.legend()

    #this makes buckets w/o the 1st one highlighting 0s
    # values = [buckets[i]["share"]*100 for i in range(len(buckets))]
    # ax.bar(list(range(len(buckets))), values, align='center')


def EVERYTHING_yearly_impr_rate_histo_grid(full_data, raw_buckets,n_values=[10**3,10**6,10**9],
                                p_values=[8,10**3,10**6],variation="default", par_data="",seq_data="", measure="rt"):
    fig, ax = plt.subplots(len(p_values),len(n_values),figsize=(7,7),dpi=200,layout='tight',sharey='all')
    #got mad about argument "layout"
    #fig, ax = plt.subplots(len(p_values),len(n_values),figsize=(7,7),dpi=200, sharey='all')

    for i in range(len(p_values)):
        p = p_values[i]
        for j in range(len(n_values)):
            n = n_values[j]
            if (variation=="default"):
                EVERYTHING_yearly_impr_rate_histo_helper(ax[i,j],full_data, raw_buckets, n, p)
            elif(variation=="seq_plus_all"):
                EVERYTHING_seq_plus_all_impr_rate_histo_helper(ax[i,j], full_data, par_data, seq_data, raw_buckets, n, p)
            elif (variation=="just_par_impr"):
                EVERYTHING_yearly_impr_rate_histo_helper_just_par(ax[i,j],full_data, raw_buckets, n, p)
            else:
                EVERYTHING_stacked_impr_rate_histo_helper(ax[i,j], full_data, par_data, seq_data, raw_buckets, n, p)

            # ax[i,j].set_title("$n="+get_nice_n(n)+"$ \# processors = "+get_nice_n(p)+"$")

    labels = [raw_buckets[i]["label"] for i in range(len(raw_buckets))]
    for j in range(len(n_values)):
        ax[len(p_values)-1,j].set_xticks(list(range(len(labels))),labels=labels, rotation=90)
        #ax[len(p_values)-1,j].set_xticks(list(range(len(labels))), rotation=90)

        for i in range(len(p_values)-1):
            ax[i,j].get_xaxis().set_visible(False)

    # max_y_lim = max(ax[i,k].get_ylim() for i in range(len(p_values)) for k in range(len(n_values)))
    # print(max_y_lim)
    for i in range(len(p_values)):
        ax[i,0].yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0f%%'))
        for j in range(1,len(n_values)):
            # ax[i,j].set_ylim(max_y_lim)
            ax[i,j].get_yaxis().set_visible(False)


    # ax[0,0].set_title("Problem size ($n$) =\n"+long_human_format(n_values[0]))
    # ax[0,1].set_title("Problem size ($n$) =\n"+long_human_format(n_values[1]))
    # ax[0,2].set_title("Problem size ($n$) =\n"+long_human_format(n_values[2]))
    ax[0,0].set_title(human_format(n_values[0])+" problem size")
    ax[0,1].set_title(human_format(n_values[1])+" problem size")
    ax[0,2].set_title(human_format(n_values[2])+" problem size")
    # ax[0,0].set_ylabel("# processors = \n"+long_human_format(p_values[0]))
    # ax[1,0].set_ylabel("# processors = \n"+long_human_format(p_values[1]))
    # ax[2,0].set_ylabel("# processors = \n"+long_human_format(p_values[2]))
    ax[0,0].set_ylabel(human_format(p_values[0])+" processors")
    ax[1,0].set_ylabel(human_format(p_values[1])+" processors")
    ax[2,0].set_ylabel(human_format(p_values[2])+" processors")

    fig.suptitle("Average Yearly Speedup from Parallelization")

    plt.savefig(SAVE_LOC+variation+'_EVERYTHING_average_improvement_rate.png')

def EVERYTHING_stacked_impr_rate_histo_helper(ax, full_data, par_data, seq_data, raw_buckets, n, p, measure="rt"):
    assert measure == "sp" or measure == "rt"
    def get_measure_value(measure,work,span,n,p):
        '''
        returns running time (if measure is "rt") or span
        :measure: either "sp" for span or "rt" for runtime
        TODO
        '''
        if measure == "sp":
            return get_comp_fn(span)(n)
        elif measure == "rt":
            return get_runtime(work,span,n,p)

    #best=smallest run time for the problem size and processor number
    par_rates = []
    seq_rates = []
    problems=get_problems(full_data) #takes all problems
    par_problems=get_problems(par_data)
    seq_problems=get_problems(seq_data)
    print("all problems: ", len(problems))
    print("paralell problems: ", len(par_problems))
    print("sequential problems: ", len(seq_problems))
    best_stats, first_stats=improvements(full_data,n,p)
    best_seq=best_seq_names(seq_data)
    for problem in problems:
        #first algorithm
        first_algo= first_stats[problem]
        #either sequential or force it to be sequential by p=1
        first_rt = get_measure_value(measure, full_data[first_algo]["work"], full_data[first_algo]["span"],n,1)
        first_year=full_data[first_algo]["year"]

        #best sequential
        if (problem in best_seq.keys()):
            #best_seq_algo=best_seq[problem]
            #trying to account for best work from a parallel algo
            best_seq_algo=best_stats[problem][2024]["bw alg"]
            best_seq_rt=get_measure_value(measure, full_data[best_seq_algo]["work"], full_data[best_seq_algo]["span"],n,1)

            seq_impr_ratio = first_rt/best_seq_rt
            seq_yearly_impr_rate = seq_impr_ratio ** (1/(2025-first_year))-1
            #seq_rates.append(seq_early_impr_rate)
            if (seq_yearly_impr_rate==0.017):
                print("17!!!!!!!!!!!")
        else:
            #best_seq_algo=first_algo
            best_seq_rt=first_rt
            #if there isn't a sequential algo, impr=0.17 a random number
            seq_yearly_impr_rate=0.017

        # seq_impr_ratio = first_rt/best_seq_rt
        # seq_early_impr_rate = seq_impr_ratio ** (1/(2025-first_year))-1
        seq_rates.append(seq_yearly_impr_rate)

        #best algorithm
        best_algo=best_stats[problem][2024]["br alg"]
        #if parallel
        if (full_data[best_algo]["parallel"]==1):
            best_rt = get_measure_value(measure, full_data[best_algo]["work"], full_data[best_algo]["span"],n,p)
            par_impr_ratio = best_seq_rt/ best_rt
            par_yearly_impr_rate = par_impr_ratio ** (1/(2025-first_year))-1
            #par_rates.append(par_yearly_impr_rate)
        else: #if no parallel algo
            par_yearly_impr_rate=0

        if(p==8 and par_yearly_impr_rate>10):
            print("problem: ",problem, "; best_seq_rt=", best_seq_rt, "; best_rt=", best_rt)

        par_rates.append(par_yearly_impr_rate)

    print("finished finding improvement rates for n=", n," and p=",p)

    # find the distribution values to be plotted
    buckets = copy.deepcopy(raw_buckets)
    assert len(buckets) >= 2
    seq_rates.sort()
    par_rates.sort()
    # print(all_rates) # (11x0.0) 14, 9, 6, 2, 3, 3, 2, 1, 1, 1, 4, 0

    for rates, key in [(par_rates, "par_count"), (seq_rates, "seq_count")]:
        buckets[0]["index"] = bisect.bisect_left(rates, buckets[0]["max"])
        buckets[0][key] = buckets[0]["index"]

        for i in range(1, len(buckets) - 1):
            max_val = buckets[i]["max"]
            buckets[i]["index"] = bisect.bisect_left(rates, max_val)
            buckets[i][key] = buckets[i]["index"] - buckets[i - 1]["index"]

        buckets[-1][key] = len(rates) - buckets[-2]["index"]

    # Compute shares
    for i in range(len(buckets)):
        buckets[i]["par_share"] = buckets[i]["par_count"] / len(par_rates)
        buckets[i]["seq_share"] = buckets[i]["seq_count"] / len(seq_rates)

    print("finished finding the distribution")

    par_zero_count = par_rates.count(0)  #how many 0s
    seq_zero_count = seq_rates.count(0)
    seq_no_algo_count = seq_rates.count(0.017)
    par_first_bucket_count = buckets[0]["par_count"] #how many in 1st bucket
    seq_first_bucket_count = buckets[0]["seq_count"]
    par_proportion_of_zero = par_zero_count / par_first_bucket_count #proportion
    seq_proportion_of_zero = seq_zero_count / seq_first_bucket_count
    seq_proportion_of_no_algo = seq_no_algo_count / seq_first_bucket_count

    par_zero_share = par_proportion_of_zero * buckets[0]["par_share"]*100  #percentage of 0 values
    seq_zero_share = seq_proportion_of_zero * buckets[0]["seq_share"]*100
    seq_no_algo_share = seq_proportion_of_no_algo * buckets[0]["seq_share"]*100
    par_non_zero_share = 100*buckets[0]["par_share"] - par_zero_share  #remaining portion of the bucket
    seq_non_zero_share = 100*buckets[0]["seq_share"] - seq_zero_share-seq_no_algo_share
    print("seq 0: ",seq_zero_share)
    print("seq no algo: ", seq_no_algo_share)
    print("seq_non_zero_share: ",seq_non_zero_share)
    print("seq bucket 1: ", 100*buckets[0]["seq_share"])
    print("seq_zero_count: ",seq_zero_count)
    print("seq_no_algo_count: ",seq_no_algo_count)
    print("seq_first_bucket_count: ", buckets[0]["seq_count"])

    # drawing the distribution histogram

    indices = np.arange(len(buckets))
    width = 0.4  # Bar width

    #plot 1st bar
    ax.bar(indices[0], seq_non_zero_share, color='tab:blue', label="Seq rates", width=width)
    ax.bar(indices[0] + width, par_non_zero_share, color='tab:cyan', label="Par rates", width=width)
    ax.bar(indices[0], seq_zero_share, bottom=seq_non_zero_share, color='tab:orange', label="No seq impr", width=width)
    ax.bar(indices[0] + width, par_zero_share, bottom=par_non_zero_share, color='tab:pink', label="No par impr", width=width)
    ax.bar(indices[0], seq_no_algo_share, bottom=seq_zero_share, color='tab:red', label="No seq algo", width=width)

    #labels for first bucket
    # ax.text(indices[0], seq_non_zero_share * 1.05, f"{seq_non_zero_share:.1f}%", ha='center', va='bottom', fontsize=6)
    # ax.text(indices[0], (seq_non_zero_share + seq_zero_share) * 1.05, f"{seq_zero_share:.1f}%", ha='center', va='bottom', fontsize=6)

    # ax.text(indices[0] + width, par_non_zero_share * 1.05, f"{par_non_zero_share:.1f}%", ha='center', va='bottom', fontsize=6)
    # ax.text(indices[0] + width, (par_non_zero_share + par_zero_share) * 1.05, f"{par_zero_share:.1f}%", ha='center', va='bottom', fontsize=6)

    #other buckets
    for i in range(1, len(buckets)):
        par_values = buckets[i]["par_share"] * 100
        seq_values = buckets[i]["seq_share"] * 100

        ax.bar(indices[i], seq_values, color='tab:blue', width=width)
        #ax.text(indices[i], seq_values * 1.05, f"{seq_values:.1f}%", ha='center', va='bottom', fontsize=6)

        ax.bar(indices[i] + width, par_values, color='tab:cyan', width=width)
        #ax.text(indices[i] + width, par_values * 1.05, f"{par_values:.1f}%", ha='center', va='bottom', fontsize=6)

    if (n==10**9 and p==8):
        ax.legend()

    #this makes buckets w/o the 1st one highlighting 0s
    # values = [buckets[i]["share"]*100 for i in range(len(buckets))]
    # ax.bar(list(range(len(buckets))), values, align='center')



def EVERYTHING_seq_plus_all_impr_rate_histo_helper(ax, full_data, par_data, seq_data, raw_buckets, n, p, measure="rt"):
    assert measure == "sp" or measure == "rt"
    def get_measure_value(measure,work,span,n,p):
        '''
        returns running time (if measure is "rt") or span
        :measure: either "sp" for span or "rt" for runtime
        TODO
        '''
        if measure == "sp":
            return get_comp_fn(span)(n)
        elif measure == "rt":
            return get_runtime(work,span,n,p)

    #best=smallest run time for the problem size and processor number
    all_rates = []
    seq_rates = []
    problems=get_problems(full_data) #takes all problems
    # par_problems=get_problems(par_data)
    # seq_problems=get_problems(seq_data)
    # print("all problems: ", len(problems))
    # print("paralell problems: ", len(par_problems))
    # print("sequential problems: ", len(seq_problems))
    best_stats, first_stats=improvements(full_data,n,p)
    # best_seq=best_seq_names(seq_data)
    for problem in problems:
        #first algorithm
        first_algo= first_stats[problem]
        #either sequential or force it to be sequential by p=1
        first_rt = get_measure_value(measure, full_data[first_algo]["work"], full_data[first_algo]["span"],n,1)
        first_year=full_data[first_algo]["year"]

        #best algo by work (best seq or best par run on 1 processor)
        best_seq_algo=best_stats[problem][2024]["bw alg"]
        best_seq_rt=get_measure_value(measure, full_data[best_seq_algo]["work"], full_data[best_seq_algo]["span"],n,1)
        seq_impr_ratio = first_rt/best_seq_rt
        seq_yearly_impr_rate = seq_impr_ratio ** (1/(2025-first_year))-1
        seq_rates.append(seq_yearly_impr_rate)

        #best runtime overall
        best_algo=best_stats[problem][2024]["br alg"]
        best_rt = get_measure_value(measure, full_data[best_algo]["work"], full_data[best_algo]["span"],n,p)
        all_impr_ratio = first_rt/ best_rt
        all_yearly_impr_rate = all_impr_ratio ** (1/(2025-first_year))-1


        # if(p==8 and all_yearly_impr_rate>10):
        #     print("problem: ",problem, "; best_seq_rt=", best_seq_rt, "; best_rt=", best_rt)

        all_rates.append(all_yearly_impr_rate)

    print("finished finding improvement rates for n=", n," and p=",p)

    # find the distribution values to be plotted
    buckets = copy.deepcopy(raw_buckets)
    assert len(buckets) >= 2
    seq_rates.sort()
    all_rates.sort()
    # print(all_rates) # (11x0.0) 14, 9, 6, 2, 3, 3, 2, 1, 1, 1, 4, 0

    for rates, key in [(all_rates, "all_count"), (seq_rates, "seq_count")]:
        buckets[0]["index"] = bisect.bisect_left(rates, buckets[0]["max"])
        buckets[0][key] = buckets[0]["index"]

        for i in range(1, len(buckets) - 1):
            max_val = buckets[i]["max"]
            buckets[i]["index"] = bisect.bisect_left(rates, max_val)
            buckets[i][key] = buckets[i]["index"] - buckets[i - 1]["index"]

        buckets[-1][key] = len(rates) - buckets[-2]["index"]

    # Compute shares
    for i in range(len(buckets)):
        buckets[i]["all_share"] = buckets[i]["all_count"] / len(all_rates)
        buckets[i]["seq_share"] = buckets[i]["seq_count"] / len(seq_rates)

    print("finished finding the distribution")

    # all_zero_count = all_rates.count(0)  #how many 0s
    # seq_zero_count = seq_rates.count(0)
    # # seq_no_algo_count = seq_rates.count(0.017)
    # all_first_bucket_count = buckets[0]["all_count"] #how many in 1st bucket
    # seq_first_bucket_count = buckets[0]["seq_count"]
    # all_proportion_of_zero = all_zero_count / all_first_bucket_count #proportion
    # seq_proportion_of_zero = seq_zero_count / seq_first_bucket_count
    # # seq_proportion_of_no_algo = seq_no_algo_count / seq_first_bucket_count

    # all_zero_share = all_proportion_of_zero * buckets[0]["all_share"]*100  #percentage of 0 values
    # seq_zero_share = seq_proportion_of_zero * buckets[0]["seq_share"]*100
    # # seq_no_algo_share = seq_proportion_of_no_algo * buckets[0]["seq_share"]*100
    # all_non_zero_share = 100*buckets[0]["all_share"] - all_zero_share  #remaining portion of the bucket
    # #seq_non_zero_share = 100*buckets[0]["seq_share"] - seq_zero_share-seq_no_algo_share
    # seq_non_zero_share = 100*buckets[0]["seq_share"] - seq_zero_share
    # # print("seq 0: ",seq_zero_share)
    # # # print("seq no algo: ", seq_no_algo_share)
    # # print("seq_non_zero_share: ",seq_non_zero_share)
    # # print("seq bucket 1: ", 100*buckets[0]["seq_share"])
    # # print("seq_zero_count: ",seq_zero_count)
    # # # print("seq_no_algo_count: ",seq_no_algo_count)
    # # print("seq_first_bucket_count: ", buckets[0]["seq_count"])

    # # drawing the distribution histogram

    # indices = np.arange(len(buckets))
    # width = 0.4  # Bar width

    # #plot 1st bar
    # ax.bar(indices[0], seq_non_zero_share, color='tab:blue', label="Seq rates", width=width)
    # ax.bar(indices[0] + width, all_non_zero_share, color='tab:cyan', label="All rates", width=width)
    # ax.bar(indices[0], seq_zero_share, bottom=seq_non_zero_share, color='tab:orange', label="0% seq impr", width=width)
    # ax.bar(indices[0] + width, all_zero_share, bottom=all_non_zero_share, color='tab:pink', label="0% impr", width=width)
    # # ax.bar(indices[0], seq_no_algo_share, bottom=seq_zero_share, color='tab:red', label="No seq algo", width=width)

    # #labels for first bucket
    # # ax.text(indices[0], seq_non_zero_share * 1.05, f"{seq_non_zero_share:.1f}%", ha='center', va='bottom', fontsize=6)
    # # ax.text(indices[0], (seq_non_zero_share + seq_zero_share) * 1.05, f"{seq_zero_share:.1f}%", ha='center', va='bottom', fontsize=6)

    # # ax.text(indices[0] + width, par_non_zero_share * 1.05, f"{par_non_zero_share:.1f}%", ha='center', va='bottom', fontsize=6)
    # # ax.text(indices[0] + width, (par_non_zero_share + par_zero_share) * 1.05, f"{par_zero_share:.1f}%", ha='center', va='bottom', fontsize=6)

    # #other buckets
    # for i in range(1, len(buckets)):
    #     par_values = buckets[i]["all_share"] * 100
    #     seq_values = buckets[i]["seq_share"] * 100

    #     ax.bar(indices[i], seq_values, color='tab:blue', width=width)
    #     #ax.text(indices[i], seq_values * 1.05, f"{seq_values:.1f}%", ha='center', va='bottom', fontsize=6)

    #     ax.bar(indices[i] + width, par_values, color='tab:cyan', width=width)
    #     #ax.text(indices[i] + width, par_values * 1.05, f"{par_values:.1f}%", ha='center', va='bottom', fontsize=6)

    # if (n==10**9 and p==8):
    #     ax.legend()

    #this makes buckets w/o the 1st one highlighting 0s
    indices = np.arange(len(buckets))
    width = 0.4  # width of each bar

    # Extract values
    seq_values = [b["seq_share"] * 100 for b in buckets]
    all_values = [b["all_share"] * 100 for b in buckets]

    # Plot bars
    ax.bar(indices - width/2, seq_values, width=width, color='tab:blue', label="Seq rates")
    ax.bar(indices + width/2, all_values, width=width, color='tab:cyan', label="All rates")

    #value labels
    # for i, (s, a) in enumerate(zip(seq_values, all_values)):
    #     ax.text(indices[i] - width/2, s + 1, f"{s:.1f}%", ha='center', va='bottom', fontsize=6)
    #     ax.text(indices[i] + width/2, a + 1, f"{a:.1f}%", ha='center', va='bottom', fontsize=6)
    #legend
    if (n==10**9 and p==8):
        ax.legend()



# def three_bar_chart(all_data,par_data,n=1000000,p=1000):
#     all_problems=get_problems(all_data)
#     par_problems=get_problems(par_data)
#     has_parallel = len(par_problems)/len(all_problems)
#     best_stats, first_stats=improvements(all_data,n,p)

#     parallel_faster_count=0
#     prob_speedups=[]
#     for prob in par_problems:
#         best_algo = best_stats[prob][2024]["br alg"]
#         best_algo_rt=get_runtime(all_data[best_algo]["work"], all_data[best_algo]["span"],n,p)
#         # print(best_algo)
#         # print(all_data[best_algo])
#         if (all_data[best_algo]["parallel"]==1):
#             parallel_faster_count+=1
#         best_work = best_stats[prob][2024]["bw alg"]
#         best_work_rt=get_runtime(all_data[best_work]["work"], all_data[best_work]["span"],n,1)
#         speedup= best_work_rt/best_algo_rt
#         prob_speedups.append(speedup)

#     # prob_speedups.sort()
#     parallel_faster=parallel_faster_count/len(par_problems)

#     # Define speedup bins
#     speedup_bins = ["1-10x", "10-100x", "100-1000x", "1000x+"]
#     speedup_values = [0, 0, 0, 0]

#     # Categorize speedups
#     for s in prob_speedups:
#         if 1 <= s < 10:
#             speedup_values[0] += 1
#         elif 10 <= s < 100:
#             speedup_values[1] += 1
#         elif 100 <= s < 1000:
#             speedup_values[2] += 1
#         else:
#             speedup_values[3] += 1

#     # Convert counts to proportions
#     speedup_total = sum(speedup_values)
#     speedup_values = [v / speedup_total for v in speedup_values]

#     # Data for the first two bars
#     bar1 = [has_parallel, 1 - has_parallel]
#     bar2 = [parallel_faster, 1 - parallel_faster]

#     # Set up bar positions
#     x = np.array([1, 2, 3])
#     width = 0.5

#     fig, ax = plt.subplots()

#     # First bar (Proportion with parallel algorithms)
#     ax.bar(x[0], bar1[0], width, label="Has Parallel", color='blue')
#     ax.bar(x[0], bar1[1], width, bottom=bar1[0], label="No Parallel", color='gray')

#     # Second bar (Among parallel problems, is parallel faster?)
#     ax.bar(x[1], bar2[0], width, label="Parallel Faster", color='green')
#     ax.bar(x[1], bar2[1], width, bottom=bar2[0], label="Parallel Not Faster", color='red')

#     # Third bar (Speedup distribution of faster parallel problems)
#     bottom = 0
#     for i in range(len(speedup_bins)):
#         ax.bar(x[2], speedup_values[i], width, bottom=bottom, label=speedup_bins[i] if x[2] == 3 else "", alpha=0.8)
#         bottom += speedup_values[i]

#     # Labels and legend
#     ax.set_xticks(x)
#     ax.set_xticklabels(["Parallel Existence", "Parallel Faster", "Speedup"])
#     ax.set_ylabel("Proportion")
#     ax.set_title("Analysis of Parallel Algorithms and Speedup")
#     ax.legend()

#     plt.show()

def sankey_style_graph(all_data, par_data, n=1000000, p=1000):
    all_problems = get_problems(all_data)
    par_problems = get_problems(par_data)
    has_parallel = len(par_problems) / len(all_problems)
    best_stats, first_stats = improvements(all_data, n, p)

    parallel_faster_count = 0
    prob_speedups = []
    #print(par_problems)
    #print(best_stats)
    #print(best_stats.keys())
    for prob in par_problems:
        best_algo = best_stats[prob][2024]["br alg"]
        if all_data[best_algo]["parallel"] == 1:
            parallel_faster_count += 1
            best_algo_rt = get_runtime(all_data[best_algo]["work"], all_data[best_algo]["span"], n, p)
            best_work = best_stats[prob][2024]["bw alg"]
            best_work_rt = get_runtime(all_data[best_work]["work"], all_data[best_work]["span"], n, 1)
            speedup = best_work_rt / best_algo_rt
            prob_speedups.append(speedup)
            # if (speedup>1000):
            #     print("speedup: ", speedup)
            #     print("best algo: ",best_algo, " work, span: ",all_data[best_algo]["work"], all_data[best_algo]["span"], " runtime: ", best_algo_rt)
            #     print("best algo work: ",all_data[best_algo]["work"], get_seq_runtime(all_data[best_algo]["work"],n))
            #     print("best seq algo: ", best_work, " work, span: ",all_data[best_work]["work"], all_data[best_work]["span"], " runtime: ", best_work_rt)

        else:
            parallel=False

    parallel_faster = parallel_faster_count / len(par_problems)

    # speedup_bins = ["1-10x", "10-100x", "100-1000x"]
    # speedup_values = [0, 0, 0]
    # # speedup_bins = ["1-10x", "10-100x", "100-1000x", "1000-10000x"]
    # # speedup_values = [0, 0, 0, 0]

    # for s in prob_speedups:
    #     if 1 <= s < 10:
    #         speedup_values[0] += 1
    #     elif 10 <= s < 100:
    #         speedup_values[1] += 1
    #     elif 100 <= s < 1000:
    #         speedup_values[2] += 1
    #     else:
    #         raise ValueError("There is now a speedup more than 1000, update code buckets")
    #     # elif 1000 <= s < 10000:
    #     #     speedup_values[3] += 1
    #     # else:
    #     #     raise ValueError("There is now a speedup more than 10000, update code buckets")



    speedup_bins = ["1-2x", "2x-4x", "4x-8x", "8x-16x", "16x-32x", "32x-64x", "64x-128x", "128x-256x",
                    "256x-512x", "512x-1024x", "oh no"]
    speedup_values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for s in prob_speedups:
        if 1 < s < 2:
            speedup_values[0] += 1
        elif 2 <= s < 4:
            speedup_values[1] += 1
        elif 4 <= s < 8:
            speedup_values[2] += 1
        elif 8 <= s < 16:
            speedup_values[3] += 1
        elif 16 <= s < 32:
            speedup_values[4] += 1
        elif 64 <= s < 128:
            speedup_values[6] += 1
        elif 128 <= s < 256:
            speedup_values[7] += 1
        elif 256 <= s < 512:
            speedup_values[8] += 1
        elif 512 <= s < 1024:
            speedup_values[9] += 1
        elif 1024 <= s < 2048: #oh no
            speedup_values[10] += 1
        else:
            raise ValueError("There is now a speedup more than 1024!")


    speedup_total = sum(speedup_values)
    speedup_values = [v / speedup_total for v in speedup_values]

    fig, ax = plt.subplots(figsize=(8, 6))
    bar_width = 0.7

    cb_colors = sns.color_palette("colorblind")
    # Pick distinct, high-contrast colors
    bar1_color_top = cb_colors[0]   # blue
    bar1_color_bottom = cb_colors[1]  # orange

    bar2_color_top = cb_colors[2]   # green
    bar2_color_bottom = cb_colors[3]  # red

    # Bar 1 - Parallel Existence
    bar1 = [has_parallel, 1 - has_parallel]

    ax.bar(1, bar1[1], width=bar_width, color=bar1_color_bottom)
    ax.bar(1, bar1[0], width=bar_width, bottom=bar1[1], color=bar1_color_top)

    # Add labels to Bar 1
    ax.text(1, bar1[1] / 2, f"No Parallel\nAlgorithm Exists\n{bar1[1]* 100:.0f}%", ha='center', va='center', color='white')
    ax.text(1, bar1[1] + bar1[0] / 2, f"Parallel\nAlgorithm Exists\n{bar1[0]* 100:.0f}%", ha='center', va='center', color='white')

    # Add proportion on top of Bar 1 (100%)
    ax.text(1, 1.02, f"{100:.0f}%", ha='center', va='bottom', color='black')

    # Bar 2 - Parallel Faster
    bar2 = [parallel_faster, 1 - parallel_faster]
    ax.bar(2, bar2[1], width=bar_width, color=bar2_color_bottom)
    ax.bar(2, bar2[0], width=bar_width, bottom=bar2[1], color=bar2_color_top)

    # Add labels to Bar 2
    ax.text(2, bar2[1] / 2, f"Parallel Algorithm\nNot Faster\n{bar2[1]* 100:.0f}%", ha='center', va='center', color='white')
    ax.text(2, bar2[1] + bar2[0] / 2, f"Parallel Algorithm\nFaster\n{bar2[0]* 100:.0f}%", ha='center', va='center', color='white')

    # Add proportion on top of Bar 2
    ax.text(2, 1.02, f"{has_parallel * 100:.0f}%", ha='center', va='bottom', color='black')

    # # Bar 3 - Speedup Distribution
    # bottom = 0
    # for i in range(len(speedup_bins)):
    #     ax.bar(3, speedup_values[i], width=bar_width, bottom=bottom, alpha=0.8)
    #     if speedup_values[i]>0:
    #         #ax.text(3, bottom + speedup_values[i] / 2, f"{speedup_bins[i]}", ha='center', va='center', color='black')
    #         ax.text(3, bottom + speedup_values[i] / 2, f"{speedup_bins[i]}\n{speedup_values[i]* 100:.2f}%", ha='center', va='center', color='black')
    #     # ax.text(3, bottom + speedup_values[i] / 2, f"{speedup_bins[i]}", ha='center', va='center', color='black')
    #     bottom += speedup_values[i]

    bottom = 0
    label_base_x = 3 + bar_width / 2 + 0.03  # starting x position
    stagger_x_offset = 0.07  # offset for second-level stagger
    nonzero_idx = 0  # counts only non-empty bins

    #picking a colormap
    greens = [cm.Greens(x) for x in np.linspace(0.3, 0.95, len(speedup_bins))]
    for i in range(len(speedup_bins)):
        value = speedup_values[i]
        ax.bar(3, value, width=bar_width, bottom=bottom, alpha=0.8, color=greens[i])

        if value > 0:
            mid_y = bottom + value / 2

            # Percentage inside the bar
            ax.text(3, mid_y, f"{speedup_bins[i]}", ha='center', va='center', fontsize=8, color='black')

            # Horizontal line to label
            ax.plot([3 + bar_width / 2, label_base_x], [mid_y, mid_y], color='black', lw=0.5)

            # Stagger labels only among non-empty categories
            level = nonzero_idx % 2
            label_x = label_base_x + (stagger_x_offset if level else 0)
            ax.text(label_x, mid_y, f"{value * 100:.2f}%", ha='left', va='center', fontsize=8)
            nonzero_idx += 1

        bottom += value
        # # Draw curly bracket on the right of bar 3 using LaTeX
        # curly_bracket = FancyArrowPatch(
        #     (3, bottom),  # Start point of the bracket
        #     (3, 0),       # End point of the bracket
        #     connectionstyle="arc3,rad=0.3",  # This adds a curved style to simulate the curly bracket
        #     mutation_scale=30,  # Controls the size of the bracket
        #     color="black",
        #     linewidth=2,
        # )

        # # Add the curly bracket to the plot
        # ax.add_patch(curly_bracket)



    # Add proportion on top of Bar 3 (Has Parallel x Faster)
    ax.text(3, 1.02, f"{has_parallel * parallel_faster*100:.0f}%", ha='center', va='bottom', color='black')

    # Draw dotted lines
    ax.plot([1 + bar_width / 2, 2 - bar_width / 2], [1, 1], linestyle='--', color='black')
    ax.plot([1 + bar_width / 2, 2 - bar_width / 2], [bar1[1], 0], linestyle='--', color='black')

    ax.plot([2 + bar_width / 2, 3 - bar_width / 2], [1, 1], linestyle='--', color='black')
    ax.plot([2 + bar_width / 2, 3 - bar_width / 2], [bar2[1], 0], linestyle='--', color='black')


    # Remove spines (borders)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # Keep y-axis visible
    # ax.spines['left'].set_visible(True)
    # or remove it?
    ax.spines['left'].set_visible(True)

    # Labels and title
    ax.set_xticks([1, 2, 3])
    ax.tick_params(axis='x', length=0)
    ax.set_xticklabels(["Algorithm Problems", "Algorithm Problems\nwith Parallel Algorithms", "Speedup"])
    # ax.set_ylabel("Proportion")
    # ax.tick_params(axis='y', length=0)
    ax.tick_params(axis='y', length=5)
    ax.set_ylabel('')
    ax.set_ylabel("Percentage of Algorithm Problems", fontsize=12)
    # ax.set_yticklabels([])
    ax.set_title(f"Proportion of Algorithm Problems, n={n}, p={p}")

    plt.savefig(SAVE_LOC+'sankey_style_graph_n_'+str(n)+'_p_'+str(p)+'.png')
    # plt.show()

def EVERYTHING_yearly_impr_rate_histo_helper_just_par(ax,full_data, raw_buckets, n, p, measure="rt"):
    assert measure == "sp" or measure == "rt"
    def get_measure_value(measure,work,span,n,p):
        '''
        returns running time (if measure is "rt") or span
        :measure: either "sp" for span or "rt" for runtime
        TODO
        '''
        if measure == "sp":
            return get_comp_fn(span)(n)
        elif measure == "rt":
            return get_runtime(work,span,n,p)

    #best=smallest run time for the problem size and processor number

    all_rates = []
    problems=get_problems(full_data) #takes all problems
    best_stats, first_stats=improvements(full_data,n,p)
    for problem in problems:
        #best seq algo
        best_seq_algo= best_stats[problem][2024]["bw alg"]
        #either sequential or force it to be sequential by p=1
        best_seq_rt = get_measure_value(measure, full_data[best_seq_algo]["work"], full_data[best_seq_algo]["span"],n,1)
        best_seq_year=full_data[best_seq_algo]["year"]
        first_seq_year=full_data[first_stats[problem]]["year"]

        #best algorithm
        best_algo=best_stats[problem][2024]["br alg"]
        #if parallel
        if (full_data[best_algo]["parallel"]==1):
            best_rt = get_measure_value(measure, full_data[best_algo]["work"], full_data[best_algo]["span"],n,p)
            impr_ratio = best_seq_rt / best_rt
            yearly_impr_rate = impr_ratio ** (1/(2025-first_seq_year))-1
            # yearly_impr_rate = impr_ratio ** (1/(2025-best_seq_year))-1
        else: #if no parallel algo
            yearly_impr_rate=0

        # if(p==8 and yearly_impr_rate>10):
        #     print("problem: ",problem, "; first_rt=", first_rt,"; best_rt=", best_rt)

        all_rates.append(yearly_impr_rate)

    print("finished finding improvement rates for n=", n," and p=",p)
    print(f"Total problems: {len(all_rates)}")
    print(f"Non-zero rates: {sum(1 for r in all_rates if r != 0)}")
    if len(all_rates) > 0:
        print(f"Sample rates (first 5): {all_rates[:5]}")
        print(f"Max rate: {max(all_rates):.2f}")
        print(f"Min rate: {min(all_rates):.2f}")
    # find the distribution values to be plotted
    buckets = copy.deepcopy(raw_buckets)
    assert len(buckets) >= 2
    all_rates.sort()
    # print(all_rates) # (11x0.0) 14, 9, 6, 2, 3, 3, 2, 1, 1, 1, 4, 0

    buckets[0]["index"] = bisect.bisect_left(all_rates, buckets[0]["max"])
    buckets[0]["count"] = buckets[0]["index"]
    for i in range(1,len(buckets)-1):
        max_val = buckets[i]["max"]
        buckets[i]["index"] = bisect.bisect_left(all_rates, max_val)
        buckets[i]["count"] = buckets[i]["index"] - buckets[i-1]["index"]
    buckets[-1]["count"] = len(all_rates) - buckets[-2]["index"]
    for i in range(len(buckets)):
        buckets[i]["share"] = buckets[i]["count"] / len(all_rates)

    print("finished finding the distribution")

    # drawing the distribution histogram
    values = [buckets[i]["share"]*100 for i in range(len(buckets))]
    # ax.bar(list(range(len(buckets))), values, align='center')
    bars = ax.bar(list(range(len(buckets))), values, align='center')

    # Add text labels
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + 1,  # 1 is vertical offset
                f"{values[i]:.1f}%",  # format as percent with 1 decimal
                ha='center', va='bottom', fontsize=6)

    # Get current y-limit
    ymin, ymax = ax.get_ylim()

    # Set a new y-limit with a bit of padding above the tallest bar
    ax.set_ylim(ymin, max(ymax, max(values) * 1.15))  # add 10% headroom
