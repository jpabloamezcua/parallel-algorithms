from header import *
from src.thesis_plots.relative_speedup import *


# this computes the relative speedup curve of every problem
# (as runtime/first-(seq)-algorithm-runtime for all algos with rt improvements),
# then aggregates it across all problems as follows: for every year, we take
# the 25th percentile, median, and 75th percentile speedup. We then plot the
# 3 curves obtained that way.

def aggregated_relative_speedup(parallel_data,sequential_data,n=10**6):
    """
    
    """
    seq_final_data, pc_final_data, sc_final_data = aggregated_relative_speedup_data(parallel_data,
                                                                                sequential_data,n)

    par_names = list(parallel_data.keys())
    par_names.sort(key= lambda name: (parallel_data[name]["year"]))
    first_year =parallel_data[par_names[0]]["year"]
    years = range(first_year, CUR_YEAR+1)
    plt.style.use('default')
    local_colors = PROCESSOR_COLORS
    nice_n = "$10^"+str(int(math.log(n,10)+1))+"$"

    datasets = {
        "Sequential": seq_final_data,
        "Personal Computer": pc_final_data,
        "Supercomputer": sc_final_data
    }

    for name in datasets:
        dataset = datasets[name]
        fig, ax = plt.subplots(1,1)
        ax.grid(axis='y', alpha=0.4)

        for i in range(len(dataset)):
            perc = dataset[i]
            col = local_colors[i]
            ax.step(years, perc, c=str(col), where='post')
            ax.hlines(y=perc[-1],xmin=years[-1],xmax=CUR_YEAR+1,color=str(col))

        ax.set_yscale('log')
        ax.set_title(name+" Aggregated Relative Speedup\nfor n="+nice_n)
        ax.set_ylabel("Relative Speedup")
        ax.set_xlabel("Year")
        ax.set_xlim(first_year-1,CUR_YEAR+1)
        #plt.show()


def new_aggregated_relative_speedup_graph(parallel_data,sequential_data,n=10**6):
    """
    
    """
    final_data_25, final_data_50, final_data_75 = perc_based_aggr_rel_speedup_data(parallel_data,
                                                                                sequential_data,n)

    # print(final_data_75)

    par_names = list(parallel_data.keys())
    par_names.sort(key= lambda name: (parallel_data[name]["year"]))
    first_year =parallel_data[par_names[0]]["year"]
    years = range(first_year, CUR_YEAR+1)
    plt.style.use('default')
    local_colors = PROCESSOR_COLORS
    nice_n = "$10^"+str(int(math.log(n,10)+1))+"$"

    datasets = {
        "25th percentile": final_data_25,
        "50th percentile": final_data_50,
        "75th percentile": final_data_75,
    }

    fig, ax = plt.subplots(3,1,sharex=True,figsize=(6.5,8),dpi=150,layout='tight')
    # ax.grid(axis='y', alpha=0.4)
    j=0
    for ds_name in datasets:
        dataset = datasets[ds_name]

        for i in range(len(dataset)):
            perc = dataset[i]
            col = local_colors[i]
            ax[j].step(years, perc, c=str(col), where='post')
            ax[j].hlines(y=perc[-1],xmin=years[-1],xmax=CUR_YEAR+1,color=str(col))
            print(ds_name + " " + str(i) + ": " + str(perc[-1]))

        # arrows
        def offset_arrow(arrow_y=2018.5,base_curve=dataset[2],curve=dataset[0],size="normal",endpt=0):
            # print(base_curve)
            # print(years)
            pre_year_index = bisect.bisect(years, arrow_y)-1
            prev_index_seq = base_curve[pre_year_index]
            prev_index_top = curve[pre_year_index]
            ax[j].annotate(text='', xy=(arrow_y,prev_index_seq+endpt), xytext=(arrow_y,prev_index_top),
                        arrowprops=dict(arrowstyle='<->',shrinkA=0,shrinkB=0,lw=1.2),zorder=6)
            offset = round(prev_index_top/prev_index_seq)
            text_pos=10**(math.log(prev_index_seq,10)+(math.log(prev_index_top,10)-math.log(prev_index_seq,10))/2)
            ftsize = 7.5 if size == "small" else 10
            wght = 'roman' if size == "small" else size
            ax[j].annotate(text=str(int(offset))+'$\\times$', xy=(arrow_y,text_pos-2.65),
                ha='center',backgroundcolor='white',zorder=7,size=ftsize,weight=wght)
            pass
        offset_arrow()
        if j == 2:
            offset_arrow(arrow_y=2022,base_curve=[1.0]*len(years),curve=dataset[2],endpt=-0.2)
        else:
            offset_arrow(arrow_y=2022,curve=dataset[1],size="small")

        ax[j].grid(axis='y', alpha=0.3)
        ax[j].set_yscale('log')
        ax[j].title.set_text(ds_name)
        ax[j].set_xlim(first_year-1,CUR_YEAR+1)

        j+=1

    max_y_lim = (min(ax[k].get_ylim()[0] for k in range(len(datasets))),
                 max(ax[k].get_ylim()[1] for k in range(len(datasets))))
    for j in range(len(datasets)):
        ax[j].set_ylim(max_y_lim)

    ax[1].set_ylabel("Relative Speedup")
    ax[2].set_xlabel("Year")

    # legend
    handles = []
    handles.append(mpatches.Patch(color=PROCESSOR_COLORS[0], label="Top Supercomputers"))
    handles.append(mpatches.Patch(color=PROCESSOR_COLORS[1], label="Personal Computers"))
    handles.append(mpatches.Patch(color=PROCESSOR_COLORS[2], label="Sequential"))
    model_legend = ax[0].legend(handles=handles,loc="upper left", bbox_to_anchor=(0, 1))
    # ax[0].add_artist(model_legend)

    extra_title = "Relative Speedup Percentiles for all Problems\nfor n="+nice_n
    ax[0].set_title(extra_title+"\n"+"25th percentile")
    # plt.savefig(SAVE_LOC+'aggr_rel_speedup.png')
    #plt.show()

def perc_based_aggr_rel_speedup_data(parallel_data,sequential_data,n):
    '''
    returns 3 lists, one for each 25, 50, 75 percentiles; each of those returns
    3 lists: supercomputer, pc, seq
    '''
    seq_final_data, pc_final_data, sc_final_data = aggregated_relative_speedup_data(parallel_data,
                                                                                sequential_data,n)

    # print(type(seq_final_data))
    # print(seq_final_data)
    final_data_25 = []
    final_data_50 = []
    final_data_75 = []

    for p,fin_data in [(0,final_data_25),(1,final_data_50),(2,final_data_75)]:
        fin_data.append(sc_final_data[p])
        fin_data.append(pc_final_data[p])
        fin_data.append(seq_final_data[p])

    return final_data_25, final_data_50, final_data_75


def debug(parallel_data,sequential_data,n=10**6):
    print("Starting debugging!")
    problems = get_problems(parallel_data)
    print(problems)
    local_colors = list(mcolors.TABLEAU_COLORS.values())
    for problem in problems:
        print(problem)
        seq_problem_curve = problem_relative_speedup_data(parallel_data,sequential_data,
                                                 problem,n=n,p=1)
        [pc_problem_curve, sc_problem_curve] = new_data_for_speedup_for_available_processors(parallel_data,
                                            sequential_data,problem,top_proc_data=top_processor_data,
                                            pc_proc_data=pc_processor_data,n=n) # TODO: unhardcode processor data

        # print(seq_problem_curve)
        # print(pc_problem_curve)
        # print(sc_problem_curve)

        fig, ax = plt.subplots(1,1)
        datasets = [seq_problem_curve, sc_problem_curve, pc_problem_curve]
        for j in range(3):
            dataset = datasets[j]
            # print(dataset)
            col = local_colors[j]

            years = []
            perc = []
            names = []
            for k,v in sorted(dataset.items()):
                years.append(k)
                perc.append(v[0])
                names.append(v[2])
            ax.step(years, perc, c=str(col), where='post')
            ax.hlines(y=perc[-1],xmin=years[-1],xmax=CUR_YEAR+1,color=str(col))

        ax.set_yscale('log')
       # plt.show()
        # break
    pass




# This function initializes 3 dicts for seq, pc, and sc. TODO

# parallel data is simulated on main model data
def aggregated_relative_speedup_data(parallel_data,sequential_data,n):
    '''
    For each of (sequential, PC, supercomputer), return dict of years mapped to 
    dict of {"25":,"50":,75":} to respective percentile values
    '''
    par_names = list(parallel_data.keys())
    par_names.sort(key= lambda name: (parallel_data[name]["year"]))
    first_year =parallel_data[par_names[0]]["year"]
    # print(first_year)

    problems = sorted(list(get_problems(parallel_data)))

    # dict of years mapped to list of best speedups for all problems
    sequential_aggregate_per_year_data = {}
    personal_c_aggregate_per_year_data = {}
    super_comp_aggregate_per_year_data = {}
    for year in range(first_year,CUR_YEAR+1):
        sequential_aggregate_per_year_data[year] = []
        personal_c_aggregate_per_year_data[year] = []
        super_comp_aggregate_per_year_data[year] = []

    for problem in problems:
        seq_problem_curve = problem_relative_speedup_data(parallel_data,sequential_data,
                                                 problem,n=n,p=1)
        [pc_problem_curve, sc_problem_curve] = new_data_for_speedup_for_available_processors(parallel_data,
                                            sequential_data,problem,top_proc_data=top_processor_data,
                                            pc_proc_data=pc_processor_data,n=n) # TODO: unhardcode processor data

        # add all year values to their lists
        seq_curve_years = sorted(seq_problem_curve.keys())
        pc_curve_years = sorted(pc_problem_curve.keys())
        sc_curve_years = sorted(sc_problem_curve.keys())
        for year in range(first_year,CUR_YEAR+1):
            # seq
            if year < seq_curve_years[0]:
                sequential_aggregate_per_year_data[year].append(1)
            else:
                last_impr_y = seq_curve_years[bisect.bisect(seq_curve_years,year)-1]
                sequential_aggregate_per_year_data[year].append(seq_problem_curve[last_impr_y][0])
            # pc
            if year < pc_curve_years[0]:
                personal_c_aggregate_per_year_data[year].append(1)
            else:
                last_impr_y = pc_curve_years[bisect.bisect(pc_curve_years,year)-1]
                personal_c_aggregate_per_year_data[year].append(pc_problem_curve[last_impr_y][0])
            # supercomputer
            if year < sc_curve_years[0]:
                super_comp_aggregate_per_year_data[year].append(1)
            else:
                last_impr_y = sc_curve_years[bisect.bisect(sc_curve_years,year)-1]
                super_comp_aggregate_per_year_data[year].append(sc_problem_curve[last_impr_y][0])

    seq_final_data = [[],[],[]]
    pc_final_data = [[],[],[]]
    sc_final_data = [[],[],[]]

    num_prob = len(problems)
    for year in range(first_year,CUR_YEAR+1):
        assert len(sequential_aggregate_per_year_data[year]) == num_prob
        assert len(personal_c_aggregate_per_year_data[year]) == num_prob
        assert len(super_comp_aggregate_per_year_data[year]) == num_prob

        # get the percentiles
        for (final_data, agg_per_year_data) in [(seq_final_data, sequential_aggregate_per_year_data),
                                                  (pc_final_data, personal_c_aggregate_per_year_data),
                                                  (sc_final_data, super_comp_aggregate_per_year_data)]:
            for i in range(3):
                final_data[i].append(percentile(sorted(agg_per_year_data[year]),(i+1)*25))

    # return the percentiles as 3 lists per seq,pc,sc option
    return seq_final_data, pc_final_data, sc_final_data


def percentile(a,q):
    '''
    Reimplementing percentile to account for Huge numbers
    requires a to be sorted
    '''
    assert all(a[i] <= a[i+1] for i in range(len(a)-1))
    denum = len(a)-1
    index = int(q / (100/denum))
    if q % (100/denum) == 0:
        return a[index]

    val1 = a[index]
    val2 = a[1+index]
    return (val2-val1)*(q % (100/denum))/ (100/denum) + val1















# TODO
def aggregated_relative_speedup_data_aspect(parallel_data,sequential_data,n,aspect):
    '''
    For each of (sequential, PC, supercomputer), return dict of years mapped to 
    dict of {"25":,"50":,75":} to respective percentile values
    '''
    if aspect == "seq":
        pass
    elif aspect == "pc":
        pass
    elif aspect == "sc":
        pass
    else:
        raise RuntimeError("Aspect needs to be one of seq, pc, or sc")

    par_names = list(parallel_data.keys())
    par_names.sort(key= lambda name: (parallel_data[name]["year"]))
    first_year =parallel_data[par_names[0]]["year"]
    # print(first_year)

    problems = get_problems(parallel_data)

    # dict of years mapped to list of best speedups for all problems
    sequential_aggregate_per_year_data = {}
    for year in range(first_year,CUR_YEAR+1):
        sequential_aggregate_per_year_data[year] = []

    for problem in problems:
        seq_problem_curve = problem_relative_speedup_data(parallel_data,sequential_data,
                                                 problem,n=n,p=1)
        [pc_problem_curve, sc_problem_curve] = new_data_for_speedup_for_available_processors(parallel_data,
                                            sequential_data,problem,n=n)

        # add all year values to their lists
        seq_curve_years = sorted(seq_problem_curve.keys())
        for year in range(first_year,CUR_YEAR+1):
            # seq
            if year < seq_curve_years[0]:
                sequential_aggregate_per_year_data[year].append(0)
            else:
                last_impr_y = seq_curve_years[bisect.bisect(seq_curve_years,year)-1]
                sequential_aggregate_per_year_data[year].append(seq_problem_curve[last_impr_y])

    seq_final_data = [[],[],[]]

    num_prob = len(problems)
    perc_25 = int(0.25*num_prob)
    perc_50 = int(0.5*num_prob)
    perc_75 = int(0.75*num_prob)
    for year in range(first_year,CUR_YEAR+1):
        assert len(sequential_aggregate_per_year_data) == num_prob

        # sort the lists
        sequential_aggregate_per_year_data[year].sort()

        # get the percentiles
        seq_final_data[0].append(sequential_aggregate_per_year_data[year][perc_25])
        seq_final_data[1].append(sequential_aggregate_per_year_data[year][perc_50])
        seq_final_data[2].append(sequential_aggregate_per_year_data[year][perc_75])

    # return the percentiles as 3 lists
    return seq_final_data
