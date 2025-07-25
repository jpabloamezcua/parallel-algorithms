from header import *
from src.thesis_plots.relative_speedup import *

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
