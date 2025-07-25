# collection of aggregate graphs for speedup vs processors
from header import *
from matplotlib.ticker import PercentFormatter


# what percentage of families have their best (in terms of speedup) algo be
# work inefficient, be work efficient, be sequential, and have no parallel algos
# as a function of the number of processors
def problems_work_efficiency_by_processors_graph(par_data,seq_data,problems,
                            n = 10**6, max_p=10**9,
                            allowed_models=set(model_dict.keys())):

# first get two lines - work inefficient line, parallel we line - and plot them

    # for each problem, for each p, need to know if its best algo is we-par, wi, or seq
    # use best_algos_by_speedup
        # given an algo returned by that, how do we know if it's efficient or not?

# then plot the "no parallel algo exists" line

    # no par algo exist is a constant line
        # iirc how the datasets are currently built this line is at 100%
        # 1. double check that; also find the # of fams + # of fams with no par algo
        # 2. if true, need to pad all the data at the end (can be hardcoded for now)

    # TODO

    plt.style.use('default')
    #fig, ax = plt.subplots(1,1,figsize=(6.55,3),dpi=200,layout='tight')
    #v1:
    # fig, ax = plt.subplots(1, 1, figsize=(6.55, 4), dpi=200)  #took away layout="tight" and increased size to 4
    #v2:
    fig, ax = plt.subplots(1, 1, figsize=(8, 3), dpi=200)  #width and height changes

    local_colors = ['#79d8f3','#a7f379','red','#f4e474']

    #total # problems - sequential and parallel
    #TODO: do we care about thesis weight vs equal weight here?
    problem_nr=len(get_problems(full_data))
    #print("PROBLEM NR",problem_nr)
    perc_no_par = len(problems)/problem_nr #where is 140 coming from?? --> changed it

    j=0
    handles = []
    all_x_values = set()
    y_val_dict = {}
    x_val_dict = {}
    for ineff in [True,False]:
        # colors
        n_color = local_colors[2-j]
        # new_patch = mpatches.Patch(color=n_color, label="$n="+get_nice_n(n)+"$")
        # handles.append(new_patch)

        # getting the x and y values
        list_of_ps = problems_switch_to_work_inefficient(par_data,seq_data,problems,
                            n,max_p=max_p,allowed_models=allowed_models,ineff=ineff)
        switch_percentage = len(list_of_ps)/len(problems)*100*perc_no_par
        int_list_of_ps = [math.ceil(x) for x in list_of_ps]
        x_values = []
        y_values = []
        for x in int_list_of_ps:
            if len(x_values)==0:
                x_values.append(x)
                y_values.append(1)
            elif not(x_values[-1] == x):
                x_values.append(x)
                y_values.append(y_values[-1]+1)
            else:
                y_values[-1] += 1
        y_values = [y/len(problems)*100*perc_no_par for y in y_values]
        print(y_values)

        x_values.insert(0,x_values[0])
        x_values.insert(0,1)
        y_values.insert(0,1)
        y_values.insert(0,1)

        ax.plot(x_values,y_values,color=n_color)

        all_x_values.update(x_values)
        y_val_dict[j] = y_values
        x_val_dict[j] = x_values

        # arrow showing the pecentage switched
        # ax.annotate(text='', xy=(x_values[-1]-j*10**6.8,1), xytext=(x_values[-1]-j*10**6.8,y_values[-1]),
        #                 arrowprops=dict(arrowstyle='<->',shrinkA=0,shrinkB=0,lw=1.2,color=n_color),zorder=6)
        # ax.annotate(text=str(int(switch_percentage))+'%', xy=(x_values[-1]-j*10**6.8,y_values[-1]/2+j*4),
        #     ha='center',backgroundcolor='white',color=n_color,zorder=7) #,size=ftsize,weight=wght)

        j+=1

    all_x_values = sorted(all_x_values)
    j = 0
    for ineff in [True,False]:
        y_values = y_val_dict[j]
        x_values = x_val_dict[j]
        new_y_values = []
        y = 0
        for x in all_x_values:
            if x in x_values:
                index = x_values.index(x)
                y = y_values[index]
            new_y_values.append(y)
        y_val_dict[j] = new_y_values
        j += 1

    print(all_x_values)
    # ax.fill_between(x=[1, 3, 20, 21, 23, 75, 398, 631, 4618, 19932, 62698, 1000000, 1000001, 12166508],y1=100,y2=perc_no_par*100,color=local_colors[0])
    ax.fill_between(x=all_x_values,y1=100,y2=perc_no_par*100,color=local_colors[0])
    ax.fill_between(x=all_x_values,y1=perc_no_par*100,y2=y_val_dict[1],color=local_colors[1])
    ax.fill_between(x=all_x_values,y1=y_val_dict[0],y2=0,color=local_colors[3])
    ax.fill_between(x=all_x_values,y1=y_val_dict[1],y2=y_val_dict[0],color=local_colors[2])

    # Remove text annotations inside the plot
    #ax.text(20,75,"No Parallel Algorithm Exists",fontsize=10,verticalalignment='center')
    #ax.text(7,35,"Sequential Algorithm Fastest",fontsize=10,verticalalignment='center')
    #ax.text(0.8*10**3,18,"Work Efficient Algorithm Fastest",fontsize=10,verticalalignment='center')
    #ax.text(0.4*10**4,5.5,"Work Inefficient Algorithm Fastest",fontsize=10,verticalalignment='center')
    # Add legend with square color patches
    #v1:
    # legend_labels = [
    #     "No Parallel Algorithm Exists",
    #     "Sequential Algorithm Fastest",
    #     "Work Efficient Algorithm Fastest",
    #     "Work Inefficient Algorithm Fastest"
    # ]
    # legend_patches = [mpatches.Patch(color=color, label=label) for color, label in zip(local_colors, legend_labels)]
    # ax.legend(handles=legend_patches, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)

    #v2:
    legend_labels = [
        "No Parallel\nAlgorithm Exists",        # Split into two lines
        "Sequential\nAlgorithm Fastest",        # Split into two lines
        "Work Efficient\nAlgorithm Fastest",    # Split into two lines
        "Work Inefficient\nAlgorithm Fastest"   # Split into two lines
    ]
    legend_patches = [mpatches.Patch(color=color, label=label) for color, label in zip(local_colors, legend_labels)]
    ax.legend(handles=legend_patches, loc='center left', bbox_to_anchor=(1.0, 0.5), ncol=1)

    ###


    ax.hlines(y=perc_no_par*100,xmin=1,xmax=x_values[-1],color=local_colors[0])

    # new_patch = mpatches.Patch(color=n_color, label="No Parallel Algorithm Exists")
    # handles.append(new_patch)
    # new_patch = mpatches.Patch(color=n_color, label="Sequential Algorithm Fastest")
    # handles.append(new_patch)
    # new_patch = mpatches.Patch(color=n_color, label="Work Efficient Algorithm Fastest")
    # handles.append(new_patch)
    # new_patch = mpatches.Patch(color=n_color, label="Work Inefficient Algorithm Fastest")
    # handles.append(new_patch)

    # ax.legend(handles=handles)
    ax.set_xscale('log')
    ax.set_ylim(0,100)
    ax.set_ylabel("Percentage of problem families",rotation=90)
    ax.set_xlabel("Number of processors")
    ax.set_yticks(ax.get_yticks(),[str(round(x))+"%" for x in ax.get_yticks()])
    ax.set_title("Work Efficiency of the Fastest Algorithm\nfor $n = "+get_nice_n(n)+"$")

    #layout tweak to hopefully prevent overlap
    fig.tight_layout()
    #v1:
    #fig.subplots_adjust(bottom=0.3)  #extra space for the legend
    #v2:
    fig.subplots_adjust(right=0.75)

    # plt.show()
    plt.savefig(SAVE_LOC+'work_efficiency_fastest_algo'+'.png')

    pass

# helper function for problems_work_efficiency_by_processors_graph
#
# returns two direct access arrays (lists)
# result1[i] is # of processors at which i problems have switched to inefficient algorithms
# result2[i] is # of processors at which i problems have no useful parallel algos
# (the fastest algo isn't parallel)
# theoretically, results2[i] >= results1[i]
def problems_work_efficiency_by_processors(par_data,seq_data,problems,
                            n = 10**6, max_p=10**9,
                            allowed_models=set(model_dict.keys())):
    # for each problem, for each p, need to know if its best algo is we-par, wi, or seq
    # use best_algos_by_speedup
        # given an algo returned by that, how do we know if it's efficient or not?

    # TODO
    pass

# graphing problems_switch_to_work_inefficient() for various values of n
# also shows how many problems never switch to work inefficient
def problems_switch_to_work_inefficient_graph(par_data,seq_data,problems,
                            n_values = [10**3,10**6,10**9],max_p=10**9,
                            allowed_models=set(model_dict.keys())):

    plt.style.use('default')
    fig, ax = plt.subplots(1,1,figsize=(6.55,4.5),dpi=200,layout='tight')

    j=0
    handles = []
    for n in n_values:
        # colors
        n_color = COLORS[j]
        new_patch = mpatches.Patch(color=n_color, label="$n="+get_nice_n(n)+"$")
        handles.append(new_patch)
        j+=1

        # getting the x and y values
        list_of_ps = problems_switch_to_work_inefficient(par_data,seq_data,problems,
                            n,max_p=max_p,allowed_models=allowed_models)
        switch_percentage = len(list_of_ps)/len(problems)*100
        int_list_of_ps = [math.ceil(x) for x in list_of_ps]
        x_values = []
        y_values = []
        for x in int_list_of_ps:
            if len(x_values)==0:
                x_values.append(x)
                y_values.append(1)
            elif not(x_values[-1] == x):
                x_values.append(x)
                y_values.append(y_values[-1]+1)
            else:
                y_values[-1] += 1
        y_values = [y/len(problems)*100 for y in y_values]

        ax.plot(x_values,y_values,color=n_color)

        # arrow showing the pecentage switched
        ax.annotate(text='', xy=(x_values[-1],1), xytext=(x_values[-1],y_values[-1]),
                        arrowprops=dict(arrowstyle='<->',shrinkA=0,shrinkB=0,lw=1.2,color=n_color),zorder=6)
        ax.annotate(text=str(int(switch_percentage))+'%', xy=(x_values[-1],y_values[-1]/2),
            ha='center',backgroundcolor='white',color=n_color,zorder=7) #,size=ftsize,weight=wght)


    ax.legend(handles=handles)
    ax.set_xscale('log')
    # ax.set_ylim(0,100)
    ax.set_ylabel("Percentage of problems that \nswitch to work-inefficient algorithms",rotation=90)
    ax.set_xlabel("Number of processors")
    ax.set_title("Percentage of problems that switch to work-inefficient algorithms")

    plt.show()


    pass



# for all problems, at what point does it make sense for them to switch from the
# work-efficient algorithm (potentially sequential) to a work-inefficient algo?
# for the number of processors
# (helper function)
# returns direct access array (list) result[i] is # of processors at which i
# problems have switched to inefficient algorithms
def problems_switch_to_work_inefficient(par_data,seq_data,problems,n,max_p=10**9,
                          allowed_models=set(model_dict.keys()),ineff=False):

    list_of_ps = []
    for prob in problems:
        p_par,p_ineff = work_inefficiency_switching_point(par_data,seq_data,prob,n,max_p=max_p,
                          allowed_models=allowed_models)
        if ineff:
            p = p_ineff
        else:
            p = p_par
        if p is not None:
            list_of_ps.append(p)
            print(prob)

    print(str(len(list_of_ps))+" / "+str(len(problems))+" switched to work-inefficient algos")
    print("Porportion of problems that never switch to work-inefficient algos is "+
                    str((len(problems)-len(list_of_ps))/len(problems)*100)+" %")
    # print("Proportion of problems that use a sequential ")

    list_of_ps.sort()
    return list_of_ps


# (draws the graph)
# for a given p, what's the work overhead snapshot of that switch to
# work-inefficiency? i.e. histogram (in line form) of how many problems fall
# into each work overhead bucket
def work_overhead_histogram_graph_multiple_p(par_data,seq_data,problems,p_values=[10**3,10**6,10**9],n_values=[10**3,10**6,10**9],
                            upper_bounds=[0,10,50,100,math.inf],
                            max_p=10**9,allowed_models=set(model_dict.keys())):

    plt.style.use('default')
    fig, ax = plt.subplots(1,len(p_values),sharey=True,figsize=(6.5,2.5),dpi=200,layout='tight')

    for i in range(len(p_values)):
        p = p_values[i]
        print("p = " + str(p))
        ax[i] = work_overhead_histogram_graph_helper(ax[i],par_data,seq_data,problems,p,
                                        n_values,upper_bounds,max_p,allowed_models)

        ax[i].set_title("$p = " + str(get_nice_n(p))+"$")

    ax[int(len(p_values)/2)].set_xlabel("Work Overhead")
    ax[0].set_ylabel("Percentage of Algorithm Problems")
    fig.suptitle("Work Overhead for the fastest algorithm")

    plt.savefig(SAVE_LOC+'work_overhead_histo_different_ps_HISTOGRAM.png')
    #plt.show()

    pass


# (draws the graph)
# for a given p, what's the work overhead snapshot of that switch to
# work-inefficiency? i.e. histogram (in line form) of how many problems fall
# into each work overhead bucket
def work_overhead_histogram_graph(par_data,seq_data,problems,p,n_values=[10**3,10**6,10**9],
                            upper_bounds=[0,10,50,100,math.inf],
                            max_p=10**9,allowed_models=set(model_dict.keys())):

    plt.style.use('default')
    fig, ax = plt.subplots(1,1,figsize=(6.55,4.5),dpi=200,layout='tight')

    ax = work_overhead_histogram_graph_helper(ax,par_data,seq_data,problems,p,
                                    n_values,upper_bounds,max_p,allowed_models)
    ax.set_xlabel("Work Overhead")
    plt.show()

    pass


def work_overhead_histogram_graph_helper(ax,par_data,seq_data,problems,p,n_values=[10**3,10**6,10**9],
                            upper_bounds=[0,10,50,100,math.inf],
                            max_p=10**9,allowed_models=set(model_dict.keys())):
    j=0
    handles = []

    pos = -0.3 #to make three bars
    for n in n_values:
        # colors
        n_color = COLORS[j]
        new_patch = mpatches.Patch(color=n_color, label="$n="+get_nice_n(n)+"$")
        handles.append(new_patch)
        j+=1

        # getting the x and y values
        oh_histo = work_overhead_histogram(par_data,seq_data,problems,p,n=n,
                            upper_bounds=upper_bounds,
                            max_p=max_p,allowed_models=allowed_models)
        #hostogram in line graph form
        #ax.plot(range(len(oh_histo)),oh_histo,color=n_color)

        #histogram with 3 bars
        bin_edges = np.arange(len(oh_histo))
        ax.bar(bin_edges+pos, oh_histo, color=n_color, align='center', width=0.3)
        pos+=0.3

        # arrow showing the pecentage switched

    # upper_bounds_labels = ["$"+get_nice_n(upper_bounds[i])+"$"+"-"+"$"+get_nice_n(upper_bounds[i+1])+"$"+"%"
    #                        for i in range(len(upper_bounds)-2)]
    # upper_bounds_labels.append("$"+get_nice_n(upper_bounds[-2])+"$"+"%+")
    # upper_bounds_labels.insert(0,"0%")

    #this should move every second label down so that they are not overlapping
    upper_bounds_labels = [
    ("\n" if i % 2 == 0 else "") + "$" + get_nice_n(upper_bounds[i]) + "$" + "-" + "$" + get_nice_n(upper_bounds[i+1]) + "$" + "%"
    for i in range(len(upper_bounds) - 2)
    ]
    #fix for the last label: extend it if it should be extended
    last_label = ("\n" if (len(upper_bounds) - 2) % 2 == 0 else "") + "$" + get_nice_n(upper_bounds[-2]) + "$" + "%+"
    upper_bounds_labels.append(last_label)
    upper_bounds_labels.insert(0, "0%")

    ax.legend(handles=handles)
    ax.set_ylabel("",rotation=90)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=None, symbol='%', is_latex=False))
    ax.set_xticks(range(len(upper_bounds)),upper_bounds_labels)
    ax.tick_params(axis='both', which='major', labelsize=6.5)
    ax.set_title("")

    return ax

    pass



# (helper function for the data)
# for a given p, what's the work overhead snapshot of that switch to
# work-inefficiency? i.e. histogram (in line form) of how many problems fall
# into each work overhead bucket
# given the number of processors p, for a given problem size n
def work_overhead_histogram(par_data,seq_data,problems,p,n=10**6,
                            upper_bounds=[0,10,50,100,math.inf],
                            max_p=10**9,allowed_models=set(model_dict.keys())):
    n_of_buckets = len(upper_bounds)

    # for every problem, find its work overhead and increment the bucket's count
    overhead_bucket_counts = [0]*n_of_buckets
    for problem in problems:
        #print(problem)
        max_speedup = best_algos_by_speedup(par_data,seq_data,problem,n=n,max_p=p+1,
                            allowed_models=allowed_models)
        # print(max_speedup)
        best_we_name = max_speedup[0][2]
        if best_we_name is None:
            par_we_time = get_best_seq_time_from_par_algos(par_data,problem)
            # print("work_overhead_histogram we time: "+str(par_we_time))
            we_time_at_n = get_comp_fn(par_we_time)(n)
        elif not max_speedup[0][3]:
            seq_time = seq_data[best_we_name]["time"]
            # print("work_overhead_histogram we time: "+str(seq_time))
            we_time_at_n = get_comp_fn(seq_time)(n)
        else:
            par_we_time = par_data[best_we_name]["work"]
            # print("work_overhead_histogram we time: "+str(par_we_time))
            we_time_at_n = get_comp_fn(par_we_time)(n)

        i = bisect.bisect([interval[0] for interval in max_speedup],p)-1
        _, _, name, if_par = max_speedup[i]
        if not if_par:
            overhead_bucket_counts[0] += 1
        else:
            work = par_data[name]["work"]
            # print("work_overhead_histogram work: "+str(work))
            work_at_n = get_comp_fn(work)(n)
            # print('work_at_n'+str(work_at_n))
            # print('we_time_at_n'+str(we_time_at_n))
            overhead = (work_at_n/we_time_at_n - 1)*100
            # print(overhead)
            # print(upper_bounds)
            j = bisect.bisect_left(upper_bounds,overhead)
            # if j>0:
            #     print(j)
            #     print(problem)
            overhead_bucket_counts[j] += 1

    #print(overhead_bucket_counts)

    return [overhead_bucket_counts[i]/sum(overhead_bucket_counts) for i in range(len(overhead_bucket_counts))]

# helper function
# for a given n, at what value of p (number of processors) does it
# make sense for a problem to switch from the work efficient (seq) algorithm to
# an inefficient version?
# seq algos are distinguished from we parallel algos
# outputs: (integer p or None,integer p or None)
# first is the parallel algo p, second is inefficient parallel algo p
def work_inefficiency_switching_point(par_data,seq_data,problem,n,max_p=10**9,
                          allowed_models=set(model_dict.keys())):
    print(problem)
    max_speedup = best_algos_by_speedup(par_data,seq_data,problem,n=n,max_p=max_p,
                          allowed_models=allowed_models)

    seq_eff_p = 1
    first_parallel_p = None
    first_ineff_p = None # this has to be parallel so ineff_p >= par_p always
    for interval in max_speedup:
        eff_p, speedup, name, if_par = interval
        if not if_par:
            seq_eff_p = eff_p
            # print("time: "+str(seq_data[name]["time"]))
        if if_par and eff_p > seq_eff_p:
            print("work: "+str(par_data[name]["work"]))
            print("span: "+str(par_data[name]["span"]))
            is_we = is_work_efficient(par_data,seq_data,problem,name,allowed_models=set(model_dict.keys()))
            if is_we and first_parallel_p is None:
                first_parallel_p = eff_p
            elif not(is_we) and first_ineff_p is None:
                first_ineff_p = eff_p
                if first_parallel_p is None:
                    first_parallel_p = eff_p
                return first_parallel_p, first_ineff_p

            # print(eff_p)
            # return eff_p

    return first_parallel_p, first_ineff_p

active_labels = set()

def NEW_work_overhead_histogram_graph_multiple_p(par_data,seq_data,problems,p_values=[10**3,10**6,10**9],n_values=[10**3,10**6,10**9],
                            upper_bounds=[0,10,50,100,math.inf],
                            max_p=10**9,allowed_models=set(model_dict.keys())):

    plt.style.use('default')
    fig, ax = plt.subplots(1,len(p_values),sharey=True,figsize=(6.5,2.5),dpi=200,layout='tight')
    legend_patches=[[],[],[]]
    global active_labels #keep track of which categories to actually have legend for
    active_labels.clear()  # Reset active labels at the start

    for i in range(len(n_values)):
        n = n_values[i]
        print("n = " + str(n))
        ax[i],legend_patches[i] = NEW_work_overhead_histogram_graph_helper(ax[i],par_data,seq_data,problems,n,
                                        p_values,upper_bounds,max_p,allowed_models)

        ax[i].set_title("$n = " + str(get_nice_n(n))+"$")

    filtered_patches = [patch for patch in legend_patches[0] if patch.get_label() in active_labels]
    # ax[2].legend(handles=filtered_patches, title="Work Overhead", loc="center left", bbox_to_anchor=(1.2, 0.5))


    ax[i].yaxis.set_major_formatter(PercentFormatter(xmax=100))
    ax[int(len(n_values)/2)].set_xlabel("Number of processors")
    ax[0].set_ylabel("Percentage of\nAlgorithm Problems")
    fig.suptitle("Work Overhead for the fastest algorithm")

    plt.savefig(SAVE_LOC+'NEW_work_overhead_histo_different_ps.png')
    #plt.show()

    pass


def NEW_work_overhead_histogram_graph_helper(ax, par_data, seq_data, problems, n,
                                             p_values=[8, 10**3, 10**6],
                                             upper_bounds=[0, 10, 50, 100, math.inf],
                                             max_p=10**9,
                                             allowed_models=set(model_dict.keys())):

    x_positions = np.arange(len(p_values))

    # Initialize legend patches and colors
    b_color = COLORS_GRADIENT[0]
    label = "1x"
    bucket_colors = [b_color]
    legend_patches = [mpatches.Patch(color=b_color, label=label)]
    global active_labels

    # Create legend labels for subsequent buckets based on multiplicative factors
    for j in range(len(upper_bounds) - 1):
        b_color = COLORS_GRADIENT[j + 1]
        bucket_colors.append(b_color)

        lower_bound_factor = (upper_bounds[j] / 100) + 1

        if upper_bounds[j + 1] != math.inf:
            upper_bound_factor = (upper_bounds[j + 1] / 100) + 1
            lower_str = str(int(lower_bound_factor)) if lower_bound_factor.is_integer() else str(lower_bound_factor)
            upper_str = str(int(upper_bound_factor)) if upper_bound_factor.is_integer() else str(upper_bound_factor)
            label = f">{lower_str}x - {upper_str}x"
        else:
            lower_str = str(int(lower_bound_factor)) if lower_bound_factor.is_integer() else str(lower_bound_factor)
            label = f">{lower_str}x"

        legend_patches.append(mpatches.Patch(color=b_color, label=label))

    for i, p in enumerate(p_values):
        oh_histo = work_overhead_histogram(par_data, seq_data, problems, p, n=n,
                                           upper_bounds=upper_bounds,
                                           max_p=max_p, allowed_models=allowed_models)

        bottom = 0
        for frac, color, patch in zip(oh_histo, bucket_colors, legend_patches):
            if frac > 0:
                height = frac * 100
                ax.bar(x_positions[i], height, color=color, bottom=bottom, width=0.5)
                bottom += height
                active_labels.add(patch.get_label())

    ax.set_xticks(x_positions)
    ax.set_xticklabels([f"$p= {get_nice_n(i)}$" for i in p_values])
    ax.tick_params(axis='x', labelsize=6)

    if n == 10**9:
        ax.legend(handles=legend_patches, title="Work Overhead", loc="center left", bbox_to_anchor=(1.2, 0.5))

    return ax, legend_patches
