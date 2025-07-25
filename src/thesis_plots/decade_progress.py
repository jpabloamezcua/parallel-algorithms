from header import *

# dataset: main model simulation


# For each decade, we look at every problem, and decide if it has had a sequential
# improvement (as determined by better runtime) and a parallel improvement (has
# the pareto forntier been pushed?). We then count how many have been improved
# and plot that

def average_improvement_over_decade_graph(par_data,seq_data,decade_list,var_weights="equal_weight"):
    all_seq_counts, all_par_counts = average_improvement_over_decade_data(par_data,seq_data,decade_list,var_weights=var_weights)

    plt.style.use('default')
    fig, ax = plt.subplots(1,1,figsize=(6.55,3.5),dpi=200,layout='tight')
    fam_num = len(get_families(par_data))

    #colors = SEQ_PAR_COLORS # list(mcolors.TABLEAU_COLORS.values())
    colors=COLORS #trying to see a different color scheme here
    ax.bar(range(len(decade_list)),[ct/fam_num*100 for ct in all_seq_counts],
           width=-0.4,align='edge',color=colors[0])
    ax.bar(range(len(decade_list)),[ct/fam_num*100 for ct in all_par_counts],
           width=0.4,align='edge',color=colors[1])

    # legend
    ax.text(1,60,"Sequential\nImprovements",color=colors[0],fontsize=12,horizontalalignment='center')
    ax.text(7,60,"Parallel\nImprovements",color=colors[1],fontsize=12,horizontalalignment='center')
    # handles = []
    # handles.append(mpatches.Patch(color=colors[0], label="Sequential Improvement"))
    # handles.append(mpatches.Patch(color=colors[1], label="Parallel Improvement"))
    # ax.legend(handles=handles)
    ax.set_title("Algorithm Improvements over Time")
    ax.set_xticks(range(len(decade_list)))
    ax.set_xticklabels([d["label"] for d in decade_list])
    #changing label to be vertical
    #ax.set_ylabel("% Problem\nFamilies with\nImprovements",rotation=0,labelpad=40.0)
    ax.set_ylabel("Percentage of\nAlgorithm Problems Improved", rotation=90, labelpad=10)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Decade")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    # ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    fig.align_ylabels()

    plt.savefig(SAVE_LOC+'par_vs_seq_imprv_'+var_weights+'.png')
    # plt.show()



MAX_CODE = 10000 # more than the maximum complexity time code possible

def average_improvement_over_decade_data(par_data,seq_data,decade_list,var_weights):
    """ 
    :par_data: *simulated* parallel dataset
    :seq_data: sequential dataset
    :decade_list: list of dicts with the form {"max":,"label"}
    :var_weights: type of weighting for variations (use "thesis_weight" for treating all 
            vars as independent problems, 
            use "equal_weight" to assign proportional weight to improvements for problems from the same family)
    """
    par_names = list(par_data.keys())
    par_names.sort(key= lambda name: (par_data[name]["year"], -1*par_data[name]["work"]))

    seq_names = list(seq_data.keys())
    seq_names.sort(key= lambda name: (seq_data[name]["year"], -1*seq_data[name]["time"]))

    variations = get_problems(par_data)
    fams = get_families(par_data)
    par_i, seq_i = 0, 0
    # all_par_improvements = [{prob: False for prob in fams} for _ in range(len(decade_list))]
    # all_seq_improvements = [{prob: False for prob in fams} for _ in range(len(decade_list))] # keeps track of seq imprs for each decade
    all_par_improvements = [{prob: False for prob in variations} for _ in range(len(decade_list))]
    all_seq_improvements = [{prob: False for prob in variations} for _ in range(len(decade_list))] # keeps track of seq imprs for each decade

    # keeps track of all algorithms on the pareto frontier for each problem
    par_all_so_far = {prob: set() for prob in variations}
    # and the fastest sequential time (initialized to MAX_CODE)
    seq_best_so_far = {prob: MAX_CODE for prob in variations}

    for dec_i in range(len(decade_list)):
        dec = decade_list[dec_i]
        # sequential
        # go through all the seq algos in this decade
        # if their time is better, replace the seq_best_so_far, inc count
        while seq_i<len(seq_names) and seq_data[seq_names[seq_i]]["year"] <= dec["max"]:
            var = seq_data[seq_names[seq_i]]["problem"]
            if var not in variations:
                seq_i += 1
                continue
            try:
                fam = var_weight_dict[var]["family"]
            except KeyError:
                print(str(var)+" not found")
                continue
            cur_time = seq_data[seq_names[seq_i]]["time"]
            if seq_best_so_far[var] > cur_time:
                seq_best_so_far[var] = cur_time
                # all_seq_improvements[dec_i][fam] = True
                all_seq_improvements[dec_i][var] = True
            seq_i+=1

        # parallel
        # go through all the par algos is this decade
        # if they push the pareto frontier, replace par_so_far, inc count
        while par_i<len(par_names) and par_data[par_names[par_i]]["year"] <= dec["max"]:
            var = par_data[par_names[par_i]]["problem"]
            fam = var_weight_dict[var]["family"]
            cur_span = par_data[par_names[par_i]]["span"]
            cur_work = par_data[par_names[par_i]]["work"]

            # improvement = better in at least one respect than all the algos
            frontier_push = True
            for prev in par_all_so_far[var]:
                if prev[2] < dec['max'] and prev[0] <= cur_span and prev[1] <= cur_work:
                    frontier_push = False
                    break
            if frontier_push:
                par_all_so_far[var].add((cur_span,cur_work,dec['max']))
                #all_par_improvements[dec_i][fam] = True
                all_par_improvements[dec_i][var] = True

            par_i+=1

    # all_par_counts = [0 for _ in range(len(decade_list))]
    # all_seq_counts = [0 for _ in range(len(decade_list))]
    # for dec_i in range(len(decade_list)):
    #     for fam in all_par_improvements[dec_i]:
    #         if all_par_improvements[dec_i][fam]:
    #             all_par_counts[dec_i] += 1

    #     for fam in all_seq_improvements[dec_i]:
    #         if all_seq_improvements[dec_i][fam]:
    #             all_seq_counts[dec_i] += 1

    all_par_counts = [0 for _ in range(len(decade_list))]
    all_seq_counts = [0 for _ in range(len(decade_list))]
    for dec_i in range(len(decade_list)):
        for var in all_par_improvements[dec_i]:
            if all_par_improvements[dec_i][var]:
                all_par_counts[dec_i] += var_weight_dict[var][var_weights]

        for var in all_seq_improvements[dec_i]:
            if all_seq_improvements[dec_i][var]:
                all_seq_counts[dec_i] += var_weight_dict[var][var_weights]

    # all_par_counts = [sum(var_weight_dict[fam][var_weights] for fam in all_par_improvements[dec_i] if all_par_improvements[dec_i][fam])
    #               for dec_i in range(len(decade_list))]

    # all_seq_counts = [sum(var_weight_dict[fam][var_weights] for fam in all_seq_improvements[dec_i] if all_seq_improvements[dec_i][fam])
    #               for dec_i in range(len(decade_list))]

    return all_seq_counts, all_par_counts


# from average_improvement_rates, caculate with respect to first sequential, then
# separate serial and parallel - this should be done per decade, same as average
# improvement rates

def decade_progress(par_data,seq_data,decade_list,n,p):
    # this is assuming that no parallel algorithms are created before sequential ones
    par_names = list(par_data.keys())
    par_names.sort(key= lambda name: (par_data[name]["year"], -1*par_data[name]["span"]))

    seq_names = list(seq_data.keys())
    seq_names.sort(key= lambda name: (seq_data[name]["year"], -1*seq_data[name]["time"]))

    worst_algs = {} # dict of problems started and their worst alg found (name,runtime,year)
    all_seq_rates = {} # dict mapping decades to a list of seq yearly improvment rates
    all_par_rates = {}
    for i in range(len(decade_list)):
        all_seq_rates[decade_list[i]["label"]] = []
        all_par_rates[decade_list[i]["label"]] = []

    dec_i = 0 # keep track of the decade being considered
    decade = decade_list[dec_i]["label"]

    for name in seq_names:
        algo = seq_data[name]
        # update current decade if necessary
        while algo["year"] > decade_list[dec_i]["max"]:
            dec_i += 1
            decade = decade_list[dec_i]["label"]

        if algo["problem"] not in worst_algs:
            worst_rt = get_seq_runtime(algo["time"],n)
            worst_algs[algo["problem"]] = (worst_rt,algo["year"])
        else:
            worst_rt, worst_year = worst_algs[algo["problem"]]
            # only consider legal algorithms (with a valid rate of improvement)
            print(algo)
            algo_rt = get_seq_runtime(algo["time"],n)
            if algo["year"] > worst_year and algo_rt <= worst_rt:
                impr_ratio = worst_rt / algo_rt
                yearly_impr_rate = impr_ratio ** (1/(algo["year"]-worst_year))-1
                all_seq_rates[decade].append(yearly_impr_rate)

    dec_i = 0 # keep track of the decade being considered
    decade = decade_list[dec_i]["label"]
    for name in par_names:
        algo = par_data[name]
        # update current decade if necessary
        while algo["year"] > decade_list[dec_i]["max"]:
            dec_i += 1
            decade = decade_list[dec_i]["label"]

        if algo["problem"] not in worst_algs:
            worst_rt = get_runtime(algo["work"], algo["span"],n,p)
            worst_algs[algo["problem"]] = (worst_rt,algo["year"])
        else:
            worst_rt, worst_year = worst_algs[algo["problem"]]

            # only consider legal algorithms (with a valid rate of improvement)
            algo_rt = get_runtime(algo["work"], algo["span"],n,p)
            if algo["year"] > worst_year and algo_rt <= worst_rt:
                impr_ratio = worst_rt / algo_rt
                yearly_impr_rate = impr_ratio ** (1/(algo["year"]-worst_year))-1
                all_par_rates[decade].append(yearly_impr_rate)


    seq_dec_impr_rates = [sum(all_seq_rates[d["label"]])/max(1,len(all_seq_rates[d["label"]]))
                          for d in decade_list]
    par_dec_impr_rates = [sum(all_par_rates[d["label"]])/max(1,len(all_par_rates[d["label"]]))
                          for d in decade_list]
    seq_dec_impr_rates = [round(100*x,1) for x in seq_dec_impr_rates]
    par_dec_impr_rates = [round(100*x,1) for x in par_dec_impr_rates]

    plt.style.use('default')
    fig, ax = plt.subplots(1,1)

    colors = ['#F0B27A','#58D68D'] #list(mcolors.TABLEAU_COLORS.values())
    ax.bar(range(len(decade_list)), seq_dec_impr_rates,
           width=-0.4,align='edge',color=colors[0])
    ax.bar(range(len(decade_list)), par_dec_impr_rates,
           width=0.4,align='edge',color=colors[1])

    # legend
    handles = []
    handles.append(mpatches.Patch(color=colors[0], label="Sequential Improvement"))
    handles.append(mpatches.Patch(color=colors[1], label="Parallel Improvement"))
    ax.legend(handles=handles)
    nice_n = "$10^"+str(int(math.log(n,10)+1))+"$"
    ax.set_title("Comparing Sequential and Parallel Improvement per Decade\nfor n="+nice_n+" and p="+str(p))
    ax.set_xticks(range(len(decade_list)))
    ax.set_xticklabels([d["label"] for d in decade_list])

    plt.show()
    pass
