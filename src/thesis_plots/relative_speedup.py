from header import *
import matplotlib.ticker as mticker

# dataset: main model simulation


def speedup_for_available_processors(parallel_data,sequential_data,problem,
                                top_proc_data,pc_proc_data,n=10**6,seq=False):
    """
    Plots the best available speedups for a given problem under the constraints
    of available numbers of processors in two scenarios - personal computers,
    and the best supercomputers. Optionally also plots the available speedups
    for sequential computation (assuming the max number of processors is 1)

    :parallel_data: *simulated* parallel dataset
    :sequential_data: sequential dataset
    :problem: problem number
    :top_proc_data: dict mapping years to the new existing max # of processors
    :pc_proc_data: dict mapping years to new # of proc available in personal computers
    :n: problem size
    :seq: True if drawing the sequential line
    """
    pc_adjusted_curve, top_adjusted_curve = new_data_for_speedup_for_available_processors(parallel_data,sequential_data,problem,top_proc_data,pc_proc_data,n=n)
    plt.style.use('default')
    fig, ax = plt.subplots(1,1,figsize=(6.55,3.25),dpi=200,layout='tight')
    ax.grid(axis='y', alpha=0.3)

    plot_colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    first_year = CUR_YEAR
    final_y_vals = []

    wanted_lines = [
        (top_adjusted_curve, plot_colors[0], " Top Supercomputers", 2),
        (pc_adjusted_curve, plot_colors[1], " Personal Computers", 3),
    ]

    if seq:
        seq_curve = problem_relative_speedup_data(parallel_data, sequential_data, problem, n, p=1)
        wanted_lines.append((seq_curve, plot_colors[2], " Sequential", 4))

    final_labels = []
    for dataset, color, label, z in wanted_lines:
        years = sorted(dataset.keys())
        values = [dataset[y][0] for y in years]

        if "Personal Computers" in label:
            values = [v * 0.85 for v in values]

        if "Top Supercomputers" in label:
            values = [v * 1.17 for v in values]

        ax.step(years, values, c=color, where='post', zorder=z, lw=1.5)
        ax.hlines(y=values[-1], xmin=years[-1], xmax=CUR_YEAR + 1, color=color, zorder=z, lw=1.5)
        first_year = min(first_year, years[0])
        final_labels.append((label, values[-1], color))

    def offset_arrow(arrow_y,base_curve,curve,size="normal"):
        pre_year_index_seq = bisect.bisect(sorted(base_curve.keys()), arrow_y)-1
        prev_index_seq = base_curve[sorted(base_curve.keys())[pre_year_index_seq]][0]
        pre_year_index_top = bisect.bisect(sorted(curve.keys()), arrow_y)-1
        prev_index_top = curve[sorted(curve.keys())[pre_year_index_top]][0]
        ax.annotate(text='', xy=(arrow_y,prev_index_seq), xytext=(arrow_y,prev_index_top),
                    arrowprops=dict(arrowstyle='<->', shrinkA=0, shrinkB=0, lw=0.8),
                    zorder=6)
        offset = round(prev_index_top/prev_index_seq,0)
        text_pos=10**(math.log(prev_index_seq,10)+(math.log(prev_index_top,10)-math.log(prev_index_seq,10))/2)
        ftsize = 4 if size == "small" else 6
        wght = 'roman' if size == "small" else size
        ax.annotate(text=long_human_format(int(offset))+'$\\times$', xy=(arrow_y+3,text_pos-2.5),
            ha='center',bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9),zorder=7,size=ftsize,weight=wght)
        pass

    top_years = sorted(top_adjusted_curve.keys())
    if len(top_years) > 1:
        arrow_year_top = top_years[len(top_years) // 2] + 0.5
        offset_arrow(arrow_y=arrow_year_top, base_curve=seq_curve, curve=top_adjusted_curve, size="normal")

    pc_years = sorted(pc_adjusted_curve.keys())
    if len(pc_years) > 1:
        arrow_year_pc = pc_years[-2] + 0.5
        offset_arrow(arrow_y=arrow_year_pc, base_curve=seq_curve, curve=pc_adjusted_curve, size="normal")

    for label, yval, color in final_labels:
        ax.text(CUR_YEAR + 1, yval, label, color=color, fontsize=8, va='center')

    ax.set_yscale('log')

    problem_name = problem_dict[problem]
    nice_n = "10^"+str(int(math.log(n,10)+1))
    ax.set_title(f"Parallel Performance for {problem_name} Problem\n"
               f"Using Processors Available at the Time\n"
               f"Problem Size n={n:,}")
    ax.set_ylabel("Parallel Speedup vs 1960 Sequential", fontsize=9)
    ax.set_xlabel("Year")
    ax.set_xlim(first_year-1,CUR_YEAR+1)
    ax.yaxis.set_major_formatter(mticker.LogFormatterMathtext())
    ax.yaxis.set_minor_locator(mticker.FixedLocator([1.0]))
    def custom_minor_formatter(val, pos):
        return "1" if val == 1.0 else ""
    ax.yaxis.set_minor_formatter(mticker.FuncFormatter(custom_minor_formatter))
    plt.savefig(SAVE_LOC+'rel_speedup_n_'+nice_n+'.png')
    # plt.show()

def new_data_for_speedup_for_available_processors(parallel_data,sequential_data,
                                    problem,top_proc_data=top_processor_data,
                                    pc_proc_data=pc_processor_data,n=10**6):
    '''
    returns first the pc, then the top curve
    '''
    to_return = []
    for dataset in [pc_proc_data, top_proc_data]:
        to_return.append(new_speedup_for_given_processors_data(parallel_data,sequential_data,
                                    problem,dataset,n=n))
    return to_return

def new_speedup_for_given_processors_data(parallel_data,sequential_data,
                                    problem,proc_data,n=10**6):
    # print(problem)
    # p_curve = problem_relative_speedup_data(parallel_data,sequential_data,problem,n,p)

    # for all values of p that we're interested in, compute their curves, then
    # for the years they're valid, check if they improve things

    # initialize final curve to the best sequential results
    final_curve = problem_relative_speedup_data(parallel_data,sequential_data,problem,n,p=1)
    cur_years = sorted(final_curve.keys())
    # print(final_curve)

    proc_impr_years = sorted(proc_data.keys())
    # print(proc_impr_years)

    for year in proc_impr_years:
        # print(year)
        if proc_data[year][0]==1 or year <= cur_years[0]:
            continue
        p = proc_data[year][0]
        # print(str(p)+" processors")
        p_curve = problem_relative_speedup_data(parallel_data,sequential_data,problem,n,p)
        # print(p_curve)

        cur_years = sorted(final_curve.keys())
        p_years = sorted(p_curve.keys())

        # print(cur_years)
        # print(p_years)

        # starting a two-finger algorithm
        cur_i = bisect.bisect(cur_years,year)-1
        p_i = bisect.bisect(p_years,year)-1

        # print("indeces:")
        # print(cur_i)
        # print(p_i)

        two_finger_year = max(year,p_years[p_i])
        # print("two_finger_year = "+str(two_finger_year))
        # print("cur_years[cur_i] = "+str(cur_years[cur_i]))
        # print("p_years[p_i] = "+str(p_years[p_i]))
        # print(final_curve)
        # print(p_curve)
        assert two_finger_year >= cur_years[cur_i]
        assert two_finger_year >= p_years[p_i]
        while p_i < len(p_years) and cur_i < len(cur_years):
            # if an improvement occurs, add it to final_curve
            if p_curve[p_years[p_i]][0] > final_curve[cur_years[cur_i]][0]:
                final_curve[two_finger_year] = p_curve[p_years[p_i]]
                cur_i += 1
                if two_finger_year not in cur_years:
                    cur_years.insert(cur_i,two_finger_year)

                # print(cur_i)
                # print(cur_years)
                # print(final_curve)
                # delete all future "improvements" that are now worse
                while (cur_i+1<len(cur_years)) and (final_curve[cur_years[cur_i+1]][0]
                                            <= final_curve[cur_years[cur_i]][0]):
                    del final_curve[cur_years[cur_i+1]]
                    del cur_years[cur_i+1]
                    # print("++++")
                    # print(cur_i)
                    # print(cur_years)
                    # print(final_curve)

            elif p_i + 1 < len(p_years):
                cur_i = bisect.bisect(cur_years,p_years[p_i+1])-1

            # continue to the next year with improvements in p processors
            p_i += 1
            if p_i==len(p_years):
                break
            two_finger_year = p_years[p_i]

    return final_curve


def available_processors(top_proc_data, pc_proc_data):
    """
    Plots the available processor data, resulting in 2 lines: one for personal
    computer processors, and the second for supercomputers

    :top_proc_data: dict mapping years to tuple of the max # of processors and supercomputer name
    :pc_proc_data: dict mapping years to new # of proc available in personal computers
    """
    plt.style.use('default')
    fig, ax = plt.subplots(1,1,figsize=(6.55,3.25),dpi=200,layout='tight')
    ax.grid(axis='y', alpha=0.4)

    mod_top_proc_data = {}
    for elem in top_proc_data:
        mod_top_proc_data[elem] = top_proc_data[elem][0]
    mod_pc_proc_data = {}
    for elem in pc_proc_data:
        mod_pc_proc_data[elem] = pc_proc_data[elem][0]

    first_year = CUR_YEAR
    final_y_vals = []
    for dataset, col, order in [(mod_top_proc_data,PROCESSOR_COLORS[0],1),
                                (mod_pc_proc_data,PROCESSOR_COLORS[1],2)]:
        top_years = sorted(dataset.keys())
        top_points = [dataset[y] for y in top_years]

        if order == 2:
            top_points = [p * 0.84 if p == 1 else p for p in top_points]

        ax.step(top_years,top_points,c=str(col), where='post',zorder=order)
        ax.hlines(y=top_points[-1],xmin=top_years[-1],xmax=CUR_YEAR+1,color=str(col),zorder=order)
        first_year = min(first_year,top_years[0])
        final_y_vals.append(top_points[-1])

    ax.text(CUR_YEAR+1,final_y_vals[0]," Top Supercomputers",color=PROCESSOR_COLORS[0],fontsize=8,verticalalignment='center')
    ax.text(CUR_YEAR+1,final_y_vals[1]," Personal Computers",color=PROCESSOR_COLORS[1],fontsize=8,verticalalignment='center')

    ax.set_yscale('log')
    ax.set_title("Number of Parallel Processors Over Time")
    ax.set_ylabel("Number of processors")
    ax.set_yticks(ax.get_yticks(),[human_format(x.get_position()[1]) for x in ax.get_yticklabels()])
    # ax.set_xlabel("Year")
    ax.set_xlim(1962-1,CUR_YEAR+1)
    ax.set_ylim(0.5,ax.get_ylim()[1])
    plt.savefig(SAVE_LOC+'avail_processors.png')
    # plt.show()


def problem_relative_speedup_graph(parallel_data,sequential_data,problems,
                                   n=10**6,possible_p=[1,8,64,512]):
    """
    Generates the relative speedup graph for the given problems - a curve for each
    value of p (the number of processors)
    Here relative speedup computed using running time

    :parallel_data: *simulated* parallel dataset
    :sequential_data: sequential dataset
    :problems: problems for which to draw the curves
    :n: problem size
    :possible_p: number of processor values
    """
    temp_colors = {14.1:{1:"#ff0000",2:"#00ff00"},
                   '1D Maximum Subarray':{1:"#00ffff",2:"#0000ff"}}
    plt.style.use('default')
    fig, ax = plt.subplots(1,1)
    ax.grid(axis='y', alpha=0.4)

    points_with_labels = set() # for not putting more than one label at the same point
    max_speedup_value = 1
    first_year = CUR_YEAR+1
    for problem in problems:
        i=0
        problem_name = problem_dict[problem]
        color1 = temp_colors[problem][1]
        color2 = temp_colors[problem][2]
        prob_colors = list(Color(color1).range_to(Color(color2),len(possible_p)+1))
        for p in sorted(possible_p, reverse=True):
            col = prob_colors[i].hex_l
            curve = problem_relative_speedup_data(parallel_data,sequential_data,problem,n,p)
            years = sorted(curve.keys())
            points = [curve[y][0] for y in years]
            ax.step(years,points,c=str(col), where='post',zorder=99+i)
            ax.hlines(y=points[-1],xmin=years[-1],xmax=CUR_YEAR+1,color=str(col),zorder=99+i)
            i+=1

            # labels
            for y in years:
                if curve[y][1]: # parallel
                    name = curve[y][2][8:]
                    if (y, curve[y][0]) not in points_with_labels:
                        ax.annotate(name, multialignment='center', fontsize=10,
                            xy=(y, curve[y][0]), xycoords='data', ha='right', va='bottom')
                        points_with_labels.add((y, curve[y][0]))
                else: # sequential
                    name = curve[y][2]
                    xy = (y+0.1,curve[y][0]*0.9)
                    if xy not in points_with_labels:
                        ax.annotate(sequential_data[name]["auth"]+'\n'+str(y),
                            multialignment='center', fontsize=10,xy=xy,
                            xycoords='data', ha='left', va='top')
                        points_with_labels.add(xy)
            max_speedup_value = max(max_speedup_value, max([curve[y][0] for y in years]))
        first_year = min(first_year,years[0])

        # legends
        handles = []
        for i in range(len(possible_p)):
            new_patch = mpatches.Patch(color=str(prob_colors[-i-2].hex_l), label=possible_p[i])
            handles.append(new_patch)
        if problem==14.1:
            locc="upper left"
        else:
            locc = "lower left"
        legend = ax.legend(handles=handles,loc=locc, bbox_to_anchor=(1, 0.5),
                                title="Number of processors for the\n"+problem_name+"\nproblem")
        ax.add_artist(legend)

    ax.set_yscale('log')
    ax.set_yticks([10**(2*i) for i in range(math.ceil(math.log(max_speedup_value,10)/2))])
    problem_name = problem_dict[problems[0]]+" problem" if len(problems)==1 else (
        problem_dict[problems[0]]+" and the "+ problem_dict[problems[1]]+" problems")
    ax.set_title("Parallel Performance for the "+problem_name+"\n$n="+get_nice_n(n)+"$")
    ax.set_ylabel("Speedup")
    ax.set_xlabel("Year")
    ax.set_xlim(first_year-1,CUR_YEAR+1)
    plt.show()


def problem_relative_speedup_data(parallel_data,sequential_data,problem,n,p):
    """
    Given n and p, returns the relative speedup curve for a given problem
    output format: dictionary mapping years when performance improves to the tuple
    (new speedup value, whether parallel, algorithm name). Only includes years
    when a perfromance improvement happens

    Gives relative speedup with respect to the first known sequential algorithm 
    for the problem (or if the first algorithm is parallel, its sequential version)

    :parallel_data: *simulated* parallel dataset
    :sequential_data: sequential dataset
    :problem: problem number
    :n: problem size
    :p: number of processors
    :returns: dictionary mapping improvement year to tuple of (new_speedup,whether
              the algo is parallel, algo name)
    """
    # print("starting pr_rel_sp_data")
    # filter by problem and sort by year
    par_data = {k: v for k, v in parallel_data.items() if v["problem"]==problem} # and v["model"] != 600} # for prev version
    par_names = list(par_data.keys())
    par_names.sort(key= lambda name: (par_data[name]["year"], par_data[name]["work"]))

    # print([par_data[v]["year"] for v in par_names])
    # print(len(par_data))

    seq_data = {k: v for k, v in sequential_data.items() if v["problem"]==problem}
    seq_names = list(seq_data.keys())
    seq_names.sort(key= lambda name: (seq_data[name]["year"], seq_data[name]["time"]))

    # print([seq_data[v]["year"] for v in seq_names])
    # print(len(seq_data))

    # computing the first algorithm runtime (to use as a relative base)
    if len(seq_data) > 0 and len(par_data) > 0:
        # print("pre-a")
        seq_time = get_comp_fn(seq_data[seq_names[0]]["time"])(n)
        par_time = get_runtime(par_data[par_names[0]]["work"],
                               par_data[par_names[0]]["span"],n,p=1)
        # print("a")
        if seq_data[seq_names[0]]["year"] < par_data[par_names[0]]["year"]:
            first_time = seq_time
            # print(seq_data[seq_names[0]]["time"])
            # print("b")
        elif seq_data[seq_names[0]]["year"] > par_data[par_names[0]]["year"]:
            first_time = par_time
            # print("c")
        else:
            first_time = min(par_time,seq_time)
            # print("d")
    elif len(seq_data) > 0:
        first_time = get_comp_fn(seq_data[seq_names[0]]["time"])(n)
    elif len(par_data) > 0:
        # print(par_data[par_names[0]]["work"])
        # print(par_data[par_names[0]]["span"])
        first_time = get_runtime(par_data[par_names[0]]["work"],
                               par_data[par_names[0]]["span"],n,p=1)
        # print(first_time)
    else:
        warnings.warn("No algorithms found (sequential or parallel) for problem "+str(problem))
        return {}
    assert first_time is not None

    # print(first_time)

    speedup_curve = {}
    best_speedup = 0
    # 2-finger for reading both datasets
    i = 0 # par
    j = 0 # seq
    while i<len(par_data) or j<len(seq_data):
        year_i = par_data[par_names[i]]["year"] if i<len(par_data) else CUR_YEAR+1
        year_j = seq_data[seq_names[j]]["year"] if j<len(seq_data) else CUR_YEAR+1
        if year_i <= year_j:
            work = par_data[par_names[i]]["work"]
            span = par_data[par_names[i]]["span"]
            par_rt = get_runtime(work,span,n,p)
            # print("par rt is "+str(par_rt))
            # print(first_time/par_rt)
            # print(best_speedup)
            # print((first_time/par_rt) > best_speedup)
            if (first_time/par_rt) > best_speedup:
                best_speedup = first_time/par_rt
                speedup_curve[year_i] = (best_speedup,True,par_names[i])
            i+=1
        else:
            time = seq_data[seq_names[j]]["time"]
            seq_rt = get_comp_fn(time)(n)
            if (first_time/seq_rt) > best_speedup:
                best_speedup = first_time/seq_rt
                speedup_curve[year_j] = (best_speedup,False,seq_names[j])
            j+=1
    # print(speedup_curve)
    return speedup_curve
