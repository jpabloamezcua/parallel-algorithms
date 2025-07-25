from header import *
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import math
import matplotlib.gridspec as gridspec
import numpy as np


# draws the best speedup for all processors (the envelope of speedup vs
# processor plots for all algorithms) for a given problem
def OLD_problem_speedup_vs_proc(par_data,seq_data,problem,n_values=[10**3],
                             allowed_models=set(model_dict.keys()),max_p=10**9):

    #find best sequential algo for given problem
    seq_algs = {k: v for k, v in seq_data.items() if v["problem"]==problem}
    best_seq = get_best_sequential(seq_algs)
    seq_time = seq_data[best_seq]["time"]
    #TODO: get best seq algo from all algos best work instead

    #set up plot
    plt.style.use('default')
    fig, ax = plt.subplots(1,1,figsize=(6.55,3),dpi=200,layout='tight')

    n_max_x = 0 #track maximum x-axis value for scaling later
    all_max_speedups = {} #store the best speedup for each n
    for n in n_values: #loop through each problem size
        #sequential runtime for problem size n
        seq_rt = get_seq_runtime(seq_time, n)
        #gets best speedup for given processor #s p
        #TODO: check that best_algos_by_speedup is correct
        #format it spits things out is list of "fragments" (tuples):
        #(interval start p, speedup, algo name, True if parallel or False otherwise)
        max_speedup = best_algos_by_speedup(par_data,seq_data,problem,n,max_p=max_p,
                            allowed_models=allowed_models)
        print("max speedup: ",max_speedup)
        all_max_speedups[n] = max_speedup #save it

        # print(n)
        # print(max_speedup)

        # computing the largest value of x that would be interesting to look at
        #basically at what # of processors to end x axis
        #TODO: understand whats going on here and comment it
        if not max_speedup[-1][3]:
            la_eff_p = max_speedup[-1][0]
        else:
            la_name = max_speedup[-1][2]
            la_work = par_data[la_name]["work"]
            la_span = par_data[la_name]["span"]
            la_eff_p = get_comp_fn(la_work)(n) / get_comp_fn(la_span)(n)
        print(la_eff_p)
        print(n_max_x)
        n_max_x = max(n_max_x,la_eff_p*2)

    # print(all_max_speedups)
    print("========================================================")

    #cap x-axis limit
    n_max_x = min(n_max_x,max_p)
    #sample 1000 points along x-axis
    sampling_rate = max(1,n_max_x/1000)
    j=0 #color index
    handles = [] #legend handles
    final_y_vals = [] #track final y-values for label positioning

    #loop through n again to plot each problem size n
    for n in n_values:
        # print(n)
        seq_rt = get_seq_runtime(seq_time, n) #runtime
        max_speedup = all_max_speedups[n] #speedup
        n_color = COLORS[j] #pick a color
        new_patch = mpatches.Patch(color=n_color, label="$n="+get_nice_n(n)+"$")
        handles.append(new_patch)
        j+=1
        # new_interval = (max_p, None, None, None)
        # max_speedup.append(new_interval)

        #plot each speedup
        #TODO: understand and comment this code bit
        for i in range(len(max_speedup)):
            start_p, int_speedup, alg_name, if_par = max_speedup[i]

            #x1 = max(1,math.floor(start_p//sampling_rate))
            #the // seems unnecessary if using math.floor idk
            x1 = max(1,math.floor(start_p/sampling_rate))
            #what's start_p/sampling_rate?
            # --> probably a number for data pts?
            if i < len(max_speedup)-1:
                largest_p_for_x2 = min(max_speedup[i+1][0],n_max_x)
                #2 = math.floor(largest_p_for_x2//sampling_rate)
                x2 = math.floor(largest_p_for_x2/sampling_rate)
            else:
                #x2 = math.ceil(n_max_x//sampling_rate)
                x2 = math.ceil(n_max_x/sampling_rate)

            x = list(range(x1,x2+1))
            x = [a*sampling_rate for a in x]
            if x1==1:
                x.insert(0,1)
            # print(x[:10])
            #i think all that^ should basically just give the x coords (number of p) for data pts
            #not 100% sure though

            #compute speedup values (y-axis) ??
            #if algo is parallel get speedup value,
            #if algo is sequential, speedup is 1
            if if_par:
                work = par_data[alg_name]["work"]
                span = par_data[alg_name]["span"]
                def abs_speedup(p):
                    #return seq_rt / get_runtime(work,span,n,p,lower=True)
                    #why were we using lower=True?
                    #GRAPH CHANGES SIGNIFICANTLY!!
                    return seq_rt / get_runtime(work,span,n,p)
                #okay, so for every number of proc data pt, get speedup
                y = [abs_speedup(z) for z in x]
            else:
                y = [1 for z in x] #baseline ??

            ax.plot(x,y,c=n_color)
        final_y_vals.append(y[-1])


    #add annotations for problem sizes
    ax.text(n_max_x*1.05,final_y_vals[2]*10,"Problem \nSize (n)",color="black",fontsize=10,verticalalignment='center')
    ax.text(n_max_x*1.05,final_y_vals[0],"1 thousand",color=COLORS[0],fontsize=10,verticalalignment='center')
    ax.text(n_max_x*1.05,final_y_vals[1],"1 million",color=COLORS[1],fontsize=10,verticalalignment='center')
    ax.text(n_max_x*1.05,final_y_vals[2],"1 billion",color=COLORS[2],fontsize=10,verticalalignment='center')

    #dashed line for breakeven (speedup=1)
    ax.hlines(y=1,xmin=1,xmax=n_max_x,color='black',linestyle='dashed')
    ax.text(n_max_x*1.05,0.3,"Breakeven\nPoint",color="black",fontsize=10,verticalalignment='center')

    #set axis to log scale
    ax.set_xscale('log')
    ax.set_yscale('log')

    #label axis
    # ax.legend(handles=handles)
    ax.set_ylabel("Speedup")
    ax.set_xlabel("Number of processors")

    #format tick labels
    ax.set_yticks(ax.get_yticks(),[str(round(x))+"$\\times$" if round(x)>2 else "1$\\times$" if
            round(x)==1 else "1/"+str(round(1/x))+"$\\times$" for x in ax.get_yticks()])
    ax.set_xticks(ax.get_xticks(),[long_human_format(x) for x in ax.get_xticks()])
    ax.tick_params(axis='both', which='major', labelsize=7)

    #axis limits
    ax.set_xlim(0.8,n_max_x*1.04)
    ax.set_ylim(10**-3.1,10**3.3)
    # print(x[-1])
    # print(y[-1])
    # ax.set_ylim(0,y[-1])
    # ax.set_xlim(0,n_max_x)

    #title
    ax.set_title("Speed of Parallel\n"+problem_dict[problem])


    # plt.show()
    #print(n_max_x)
    plt.savefig(SAVE_LOC+'OLD_speedup_vs_proc'+'.png')

    pass

def get_processor_breakpoints(algorithms, n,
                               min_processors=1, max_processors=10_000_000):
    """
    Find processor breakpoints where the best algorithm changes and return them as a dictionary.

    Parameters:
    - algorithms: dictionary
        algorithms[name][...]
    - n: int
        Problem size `n` to be passed into the runtime function.
    - min_processors: int
        Minimum number of processors to test (default: 1).
    - max_processors: int
        Maximum number of processors to test (default: 10 million).
    - num_points: int
        Number of processor values to test (logarithmically spaced).

    Returns:
    - breakpoints_dict: dict[int, str]
        A dictionary mapping each breakpoint processor count to the best algorithm used
        from that point onward until the next breakpoint.
    """

    algorithms = dict(sorted(
        algorithms.items(),
        key=lambda item: item[1].get("work", float("inf"))
    ))

    def best_algo_at(p):
        runtimes = {}
        works = {}
        print(f"\nbest_algo_at called with p={p}")
        print(f"Number of algorithms available: {len(algorithms)}")
        print(f"First 5 algorithms: {list(algorithms.keys())[:5]}")

        for algo in algorithms:
            try:
                work = algorithms[algo]["work"]
                span = algorithms[algo]["span"]
                parallel = algorithms[algo]["parallel"]
                rt = get_runtime(work, span, n, p, parallel)
                runtimes[algo] = rt
                works[algo] = get_seq_runtime(work,n)
                print(f"Algorithm {algo}: work={work}, span={span}, parallel={parallel}, runtime={rt}")
            except Exception as e:
                print(f"Error processing algorithm {algo}: {e}")
                print(f"Available fields: {algorithms[algo].keys()}")

        if not runtimes:
            print("WARNING: No valid runtimes computed!")
            print(f"n={n}, p={p}")
            print(f"Total algorithms processed: {len(algorithms)}")
            print("First 3 algorithms details:")
            for algo in list(algorithms.keys())[:3]:
                print(f"{algo}: {algorithms[algo]}")

        best = min(runtimes, key=runtimes.get)
        print(f"Selected best algorithm: {best} with runtime {runtimes[best]}")
        return best, runtimes[best], works[best]

    def search_breakpoints(start, end, start_algo, start_runtime, end_algo, end_runtime):
        if end - start <= 1:
            return {}

        mid = (start + end) // 2
        # mid_algo, mid_runtime = best_algo_at(mid)
        mid_algo, mid_runtime, mid_work = best_algo_at(mid)

        breakpoints = {}
        if start_algo != mid_algo:
            left_breaks = search_breakpoints(start, mid, start_algo, start_runtime, mid_algo, mid_runtime)
            breakpoints.update(left_breaks)
            # breakpoints[mid] = {"algorithm": mid_algo, "runtime": mid_runtime}
            breakpoints[mid] = {"algorithm": mid_algo, "runtime": mid_runtime, "work": mid_work}

        if mid_algo != end_algo:
            right_breaks = search_breakpoints(mid, end, mid_algo, mid_runtime, end_algo, end_runtime)
            breakpoints.update(right_breaks)

        return breakpoints

    # Initialize endpoints
    # start_algo, start_runtime = best_algo_at(min_processors)
    # end_algo, end_runtime = best_algo_at(max_processors)
    start_algo, start_runtime, start_work = best_algo_at(min_processors)
    end_algo, end_runtime, end_work = best_algo_at(max_processors)

    breakpoints = {}

    if start_algo != end_algo:
        breakpoints = search_breakpoints(min_processors, max_processors,
                                         start_algo, start_runtime,
                                         end_algo, end_runtime)
        # breakpoints[min_processors] = {"algorithm": start_algo, "runtime": start_runtime}
        # breakpoints[max_processors] = {"algorithm": end_algo, "runtime": end_runtime}
        breakpoints[min_processors] = {"algorithm": start_algo, "runtime": start_runtime, "work": start_work}
        breakpoints[max_processors] = {"algorithm": end_algo, "runtime": end_runtime, "work": end_work}
    else:
        # breakpoints[min_processors] = {"algorithm": start_algo, "runtime": start_runtime}
        breakpoints[min_processors] = {"algorithm": start_algo, "runtime": start_runtime, "work": start_work}

    # Remove redundant entries where the algorithm hasn't changed
    # cleaned_breakpoints = {}
    # prev_algo = None
    # for p in sorted(breakpoints):
    #     algo = breakpoints[p]["algorithm"]
    #     if algo != prev_algo:
    #         cleaned_breakpoints[p] = breakpoints[p]
    #         prev_algo = algo
    cleaned_breakpoints = {}
    prev_algo = None
    sorted_keys = sorted(breakpoints)
    for i, p in enumerate(sorted_keys):
        algo = breakpoints[p]["algorithm"]
        is_last = (i == len(sorted_keys) - 1)
        if algo != prev_algo or is_last:
            cleaned_breakpoints[p] = breakpoints[p]
            prev_algo = algo

    # print("cleaned breakpoints",cleaned_breakpoints)
    return cleaned_breakpoints

    #this was the old func (trying every proc value)
    # breakpoints_dict = {}
    # prev_best = None


    # for p in range(min_processors,max_processors+1):
    #     # print("p:",p)
    #     runtimes = {algo: get_runtime(algorithms[algo]["work"],algorithms[algo]["span"], n, p, algorithms[algo]["parallel"]) for algo in algorithms}
    #     # print("runtimes",runtimes)
    #     best_algo = min(runtimes, key=runtimes.get)
    #     # print("best algo", best_algo)
    #     best_runtime = runtimes[best_algo]

    #     if best_algo != prev_best:
    #         breakpoints_dict[p] = {
    #             "algorithm": best_algo,
    #             "runtime": best_runtime
    #         }
    #         prev_best = best_algo
    # print("breakpoints dict",breakpoints_dict)
    # return breakpoints_dict

def problem_speedup_vs_proc(all_data, problem, n_values=[10**3],max_p=10**9):

    #TODO: rewrite this bit
    all_data_prob = {
        name: info
        for name, info in all_data.items()
        if info.get("problem") == problem
    }

    #setup plot
    # plt.figure(figsize=(10, 6))
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), sharex=True)


    # colors = plt.cm.viridis(np.linspace(0, 1, len(n_values)))
    n_colors = ["blue","orange","green"]
    marker_styles = ['o', 's', '^', 'D', 'P', '*', 'v', 'X', 'h']
    algorithm_markers = {}
    legend_handles = {}
    marker_index = 0  # Keep track of which marker to assign next


    #for each n in n_values
    # for n in n_values:
    for i, n in enumerate(n_values):
        # print("n:",n)
        #get breakpoints
        processor_data = get_processor_breakpoints(all_data_prob,n,min_processors=1,max_processors=max_p)
        # print("processor data",processor_data)
        processor_counts = list(processor_data.keys())
        # print("processor counts",processor_counts)

        speedups = []
        work_overheads = []

        for p in processor_counts:
            data = processor_data[p]
            algo = data.get("algorithm", "unknown")

            # Assign a marker to this algorithm if it hasn't been seen
            if algo not in algorithm_markers:
                algorithm_markers[algo] = marker_styles[marker_index % len(marker_styles)]
                marker_index += 1

            marker = algorithm_markers[algo]
            color = n_colors[i]

            speedup = processor_data[1]["runtime"] / data["runtime"]
            overhead = data["work"] / processor_data[1]["work"]

            speedups.append(speedup)
            work_overheads.append(overhead)

            # Plot point
            # Apply same y-offset to keep markers visually aligned with the line
            # if i == 1:
            #     speedup *= 1.04
            #     overhead *= 1.04
            # elif i == 0:
            #     speedup *= 1.08
            #     overhead *=1.08


            ax1.scatter(p, speedup, marker=marker, color=color)
            ax2.scatter(p, overhead, marker=marker, color=color)

            # Create legend entry for the algorithm
            if algo not in legend_handles:
                legend_handles[algo] = ax1.scatter([], [], marker=marker, color='black', label=algo)

        # Draw connecting lines (color by n)
        # Slight y-offset for the first line segment to avoid overlap
        plot_speedups = speedups.copy()
        # if i == 1:  # Second line: push first two points slightly up
        #     plot_speedups[0] *= 1.04
        #     plot_speedups[1] *= 1.04
        #     work_overheads[0] *= 1.04
        #     work_overheads[1] *= 1.04
        # elif i == 0:  # Third line: push first two points slightly down
        #     plot_speedups[0] *= 1.08
        #     plot_speedups[1] *= 1.08
        #     work_overheads[0] *= 1.08
        #     work_overheads[1] *= 1.08

        # Now draw the slightly modified speedup line
        ax1.plot(processor_counts, plot_speedups, linestyle='-', color=n_colors[i])
        # ax1.plot(processor_counts, speedups, linestyle='-', color=n_colors[i])
        ax2.step(processor_counts, work_overheads, where='post', linestyle='-', color=n_colors[i])

        # Annotate the n value at the end of the line
        ax1.text(processor_counts[-1] *1.10, speedups[-1], f"n={get_nice_n(n)}", va="center", fontsize=9, color=n_colors[i])
        ax2.text(processor_counts[-1] *1.10, work_overheads[-1], f"n={get_nice_n(n)}", va="center", fontsize=9, color=n_colors[i])


    #     # Compute speedups
    #     speedups = [
    #         processor_data[1]["runtime"] / processor_data[p]["runtime"]
    #         for p in processor_counts
    #     ]

    #     # Compute work overheads
    #     serial_work = processor_data[1]["work"]
    #     work_overheads = [
    #         processor_data[p]["work"] / serial_work
    #         for p in processor_counts
    #     ]

    #     # #compute speedups at breakpoints
    #     # speedups = [
    #     #     processor_data[1]["runtime"] / processor_data[p]["runtime"] #1 processor will give best seq
    #     #     for p in processor_counts
    #     # ]
    #     # print("speedups:", speedups)

    #     # # plt.plot(processor_counts, speedups, linestyle='--', marker=None, label=f"n = {n}")
    #     # # plt.scatter(processor_counts, speedups, marker='o')
    #     # ax1.plot(processor_counts, speedups, linestyle='--', marker=None, label=f"n = {n}")
    #     # ax1.scatter(processor_counts, speedups, marker='o')

    #     # serial_work = processor_data[1]["work"]
    #     # work_overheads = [
    #     #     processor_data[p]["work"] / serial_work
    #     #     for p in processor_counts
    #     # ]
    #     # # ax2.plot(processor_counts, work_overheads, linestyle='--', marker=None, label=f"n = {n}")
    #     # ax2.step(processor_counts, work_overheads, where='post', linestyle='--', label=f"n = {n}")
    #     # ax2.scatter(processor_counts, work_overheads, marker='o')
    #     # Line plots for speedup and work
    #     # ax1.plot(processor_counts, speedups, linestyle='--', color='gray', alpha=0.5, label=f"n = {n}")
    #     # ax2.step(processor_counts, work_overheads, where='post', linestyle='--', color='gray', alpha=0.5, label=f"n = {n}")

    #     # # Scatter points with algorithm markers
    #     # for i, p in enumerate(processor_counts):
    #     #     algo = processor_data[p]["algorithm"]
    #     #     marker = algo_to_marker[algo]
    #     #     ax1.scatter(p, speedups[i], marker=marker, label=algo if algo not in used_algos else "", s=60)
    #     #     ax2.scatter(p, work_overheads[i], marker=marker, label=algo if algo not in used_algos else "", s=60)
    #     #     used_algos.append(algo)
    #     # Line for each n (same color for both subplots)
    #     color = next(ax1._get_lines.prop_cycler)['color']
    #     # ax1.plot(processor_counts, speedups, linestyle='-', color=color, label=f"n = {n}")
    #     # ax2.step(processor_counts, work_overheads, where='post', linestyle='-', color=color, label=f"n = {n}")

    #     # # Dots with algorithm-specific marker, using color of the line
    #     # for i, p in enumerate(processor_counts):
    #     #     marker = algo_to_marker[algos[i]]
    #     #     ax1.scatter(p, speedups[i], marker=marker, color=color, s=60,
    #     #                 label=algos[i] if algos[i] not in used_algos else "")
    #     #     ax2.scatter(p, work_overheads[i], marker=marker, color=color, s=60,
    #     #                 label=algos[i] if algos[i] not in used_algos else "")
    #     #     used_algos.add(algos[i])
    #     # Plot speedups and work overheads for the current `n`
    #     ax1.plot(processor_counts, speedups, linestyle='-', color=colors[i], label=f"n = {n}")
    #     ax1.scatter(processor_counts, speedups, marker=markers[i % len(markers)], color=colors[i])

    #     ax2.step(processor_counts, work_overheads, where='post', linestyle='-', color=colors[i])
    #     ax2.scatter(processor_counts, work_overheads, marker=markers[i % len(markers)], color=colors[i])

    #     # Add custom legend entries for the algorithm symbols (not the n values)
    #     for j, p in enumerate(processor_counts):
    #         # For each algorithm, create a scatter with the correct marker and color
    #         legend_entries.append(ax1.scatter([], [], marker=markers[j % len(markers)], color=colors[i], label=f"Algorithm {j+1}"))

    #     # # Add custom legend entries for the algorithms (markers only)
    #     # legend_entries.append(ax1.scatter([], [], marker=markers[i % len(markers)], color=colors[i], label=f"Algorithm {i+1}"))
    #     # legend_entries.append(ax2.scatter([], [], marker=markers[i % len(markers)], color=colors[i], label=f"Algorithm {i+1}"))

    #     # Annotate last point for speedup line on ax1
    #     ax1.text(
    #         processor_counts[-1] * 1.05,  # Shift slightly to the right
    #         speedups[-1],
    #         f"n = {get_nice_n(n)}",
    #         va="center",
    #         fontsize=9,
    #         color=colors[i]
    #     )

    #     # Annotate last point for work overhead line on ax2
    #     ax2.text(
    #         processor_counts[-1] * 1.05,  # Shift slightly to the right
    #         work_overheads[-1],
    #         f"n = {get_nice_n(n)}",
    #         va="center",
    #         fontsize=9,
    #         color=colors[i]
    #     )


    # # Add a legend manually with custom entries
    # ax1.legend(handles=legend_entries, loc='center left', bbox_to_anchor=(1, 0.5), title="Algorithms", fontsize=9)



    # #final plot formatting
    # plt.xscale('log')
    # plt.xlabel('Number of Processors (log scale)')
    # # plt.xlabel('Number of Processors')
    # plt.ylabel('Speedup (Best Serial / Best Parallel Runtime)')
    # plt.title(f"Speedup vs Processors for Problem: {problem}")
    # plt.grid(True, which='both', ls='--', linewidth=0.5)
    # plt.legend()
    # plt.tight_layout()

    # plt.savefig(SAVE_LOC+'speedup_vs_proc_'+problem+'.png')

    ax1.legend(handles=list(legend_handles.values()), title="Algorithms", loc='center left', bbox_to_anchor=(1, 0.5))

    ax1.set_xscale('log')
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax1.set_yscale('log')
    ax1.axhline(y=1, color='gray', linestyle=':', linewidth=1)
    ax2.axhline(y=1, color='gray', linestyle=':', linewidth=1)

    ax1.set_ylabel('Speedup (Best Serial / Parallel Runtime) (log scale)')
    ax1.set_title(f"Speedup and Work Overhead vs Processors for Problem: {problem}")
    ax1.grid(True, which='both', ls='--', linewidth=0.5)
    ax1.legend()

    ax2.set_xlabel('Number of Processors (log scale)')
    ax2.set_ylabel('Work Overhead (Parallel Work / Serial Work) (log scale)')
    ax2.grid(True, which='both', ls='--', linewidth=0.5)
    ax2.legend()

    plt.tight_layout()
    plt.savefig(SAVE_LOC + f'speedup_and_work_overhead_{problem}.png')


# def fastest_algo_work_eff(data, n=10**6, min_p=1, max_p=10**6):

#     serial={}
#     we={}
#     not_we={}

#     problems=get_problems(data)
#     #for each problem
#     for problem in problems:
#     #TODO: rewrite this bit
#         data_prob = {
#             name: info
#             for name, info in data.items()
#             if info.get("problem") == problem
#         }
#         #find fastest algo cutoff points
#         #spits out dictionary of processor number and the algo name and runtime that is fastest at that point
#         processor_data = get_processor_breakpoints(data_prob,n,min_processors=min_p,max_processors=max_p)

#         # For each processor count and the fastest algo at that point
#         for proc_count in processor_data.keys():
#             algo_name=processor_data[proc_count]["algorithm"]
#             #is it serial?
#             if not data[algo_name]["parallel"]:
#                 serial[proc_count] += 1
#             #is it parallel and work efficient
#             elif data[algo_name]["parallel"] and data[algo_name].get("we", False):
#                 we[proc_count] += 1
#             #else parallel and not work efficient
#             else:
#                 not_we[proc_count] += 1

#     # Normalize counts to percentages
#     processor_range = sorted(set(serial) | set(we) | set(not_we))
#     total_problems = len(problems)

#     serial_pct = [serial[p] / total_problems for p in processor_range]
#     we_pct = [we[p] / total_problems for p in processor_range]
#     not_we_pct = [not_we[p] / total_problems for p in processor_range]

#     # Stacked area plot
#     plt.stackplot(
#         processor_range,
#         serial_pct,
#         we_pct,
#         not_we_pct,
#         labels=["Serial", "Work-Efficient Parallel", "Not Work-Efficient Parallel"],
#         colors=["#ff9999", "#99ff99", "#9999ff"]
#     )
#     plt.xlabel("Number of Processors")
#     plt.ylabel("Fraction of Problems")
#     plt.title("Fastest Algorithm Category by Processor Count")
#     plt.legend(loc="upper right")
#     plt.grid(True)
#     plt.tight_layout()
#     plt.show()



def fastest_algo_work_eff(data, n=10**6, min_p=1, max_p=10**6, step=1000):
    problems = get_problems(data)
    processor_range = list(range(min_p, max_p + 1, step))  # Step to make it tractable

    # Maps problem → {proc_count → category}
    problem_proc_to_category = {}

    for problem in problems:
        # Get problem-specific algorithm data
        data_prob = {
            name: info
            for name, info in data.items()
            if info.get("problem") == problem
        }

        # Get breakpoints for fastest algorithms
        processor_data = get_processor_breakpoints(data_prob, n, min_processors=min_p, max_processors=max_p)

        # Map of proc_count → category
        proc_to_cat = {}
        for proc_count, entry in processor_data.items():
            algo_name = entry["algorithm"]
            if not data[algo_name]["parallel"]:
                cat = "serial"
            elif data[algo_name]["parallel"] and data[algo_name].get("we", False):
                cat = "we"
            else:
                cat = "not_we"
            proc_to_cat[proc_count] = cat

        # Convert breakpoints to a full list using forward fill
        proc_list = sorted(proc_to_cat)
        filled_cat = []
        last_cat = None
        idx = 0
        for p in processor_range:
            while idx < len(proc_list) and proc_list[idx] <= p:
                last_cat = proc_to_cat[proc_list[idx]]
                idx += 1
            filled_cat.append(last_cat if last_cat is not None else "serial")  # Default to serial if no info

        problem_proc_to_category[problem] = filled_cat

    # Aggregate across all problems at each processor count
    serial_pct = []
    we_pct = []
    not_we_pct = []

    total_problems = len(problems)

    for i in range(len(processor_range)):
        serial_ct = we_ct = not_we_ct = 0
        for problem in problems:
            cat = problem_proc_to_category[problem][i]
            if cat == "serial":
                serial_ct += 1
            elif cat == "we":
                we_ct += 1
            else:
                not_we_ct += 1

        serial_pct.append(serial_ct / total_problems)
        we_pct.append(we_ct / total_problems)
        not_we_pct.append(not_we_ct / total_problems)

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.stackplot(
        processor_range,
        serial_pct,
        we_pct,
        not_we_pct,
        labels=["Serial", "Work-Efficient Parallel", "Not Work-Efficient Parallel"],
        colors=["#ff9999", "#99ff99", "#9999ff"]
    )
    plt.xlabel("Number of Processors")
    plt.ylabel("Fraction of Problems")
    plt.title("Fastest Algorithm Category by Processor Count")
    plt.legend(loc="upper right")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def count_fastest_algo_by_category(data, par_data, n=10**6, min_p=1, max_p=10**6, step=100):
    """
    Generates a stacked area plot showing the percentage of problems for which the fastest algorithm
    is sequential, work-efficient parallel, or work-inefficient parallel, as a function of the number of processors.
    This version is optimized to be efficient by reducing redundant computations.
    """
    all_problems = get_problems(data)
    par_problems = get_problems(par_data)
    no_par_problems = all_problems - par_problems

    processor_range = list(range(min_p, max_p + 1, step))
    total_problems = len(all_problems)

    counts = {
        "we": {p: 0 for p in processor_range},
        "not_we": {p: 0 for p in processor_range},
        "serial": {p: 0 for p in processor_range},
        "no_par": {p: len(no_par_problems) for p in processor_range}
    }

    for problem in par_problems:
        data_prob = {name: info for name, info in data.items() if info.get("problem") == problem}
        if not data_prob:
            continue

        breakpoints = get_processor_breakpoints(data_prob, n, min_processors=min_p, max_processors=max_p)
        if not breakpoints:
            continue

        sorted_bps = sorted(breakpoints.keys())
        bp_idx = 0

        best_seq_work = breakpoints[sorted_bps[0]]["work"]

        for i, p in enumerate(processor_range):
            while bp_idx + 1 < len(sorted_bps) and sorted_bps[bp_idx + 1] <= p:
                bp_idx += 1

            active_bp_p = sorted_bps[bp_idx]
            algo_name = breakpoints[active_bp_p]["algorithm"]
            info = data[algo_name]
            current_work = breakpoints[active_bp_p]["work"]

            if not info["parallel"]:
                counts["serial"][p] += 1
            elif current_work == best_seq_work:
                counts["we"][p] += 1
            else:
                counts["not_we"][p] += 1

    we_pct = [100 * counts["we"][p] / total_problems for p in processor_range]
    not_we_pct = [100 * counts["not_we"][p] / total_problems for p in processor_range]
    serial_pct = [100 * counts["serial"][p] / total_problems for p in processor_range]
    no_par_pct = [100 * counts["no_par"][p] / total_problems for p in processor_range]

    plt.figure(figsize=(12, 6))
    plt.stackplot(
        processor_range,
        we_pct,
        not_we_pct,
        serial_pct,
        no_par_pct,
        labels=["Parallel Work-Efficient\nAlgorithm Fastest", "Parallel Work Inefficient\nAlgorithm Fastest", "Serial Algorithm\nFastest", "No Parallel\nAlgorithm Exists"],
        colors=WORK_EFF_COLORS
    )

    plt.xlabel("Number of Processors")
    plt.ylabel("Percentage of Algorithm Problems")
    plt.title(f"Work Efficiency of the Fastest Algorithm\n$n={get_nice_n(n)}$")
    plt.legend(loc="upper right", ncol=2)
    plt.grid(True)
    plt.xscale("log")
    plt.xlim(min_p, max_p)
    plt.ylim(0, 100)
    plt.gca().yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x)}%'))
    plt.tight_layout()

    output_path = SAVE_LOC + f'work_efficiency_fastest_algo_{str(n)}.png'
    plt.savefig(output_path)
    plt.close()

def problem_speedup_vs_proc_three(all_data, problem, n_values=[10**3], max_p=10**9):
    all_data_prob = {
        name: info for name, info in all_data.items() if info.get("problem") == problem
    }

    fig, axes = plt.subplots(len(n_values), 1, figsize=(10, 5 * len(n_values)), sharex=True)

    if len(n_values) == 1:
        axes = [axes]  # Ensure axes is always iterable

    #############
    # fig = plt.figure(figsize=(10, 5 * len(n_values) + 1))  # Extra space for top bar
    # gs = gridspec.GridSpec(len(n_values) + 1, 1, height_ratios=[0.1] + [1]*len(n_values), hspace=0.4)

    # # Top bar for "Work Overhead"
    # bar_ax = fig.add_subplot(gs[0])
    # bar_ax.axis('off')
    # bar_ax.text(0.5, 0.5, "Work Overhead", ha='center', va='center', fontsize=12, weight='bold')

    # # Regular subplots below
    # axes = [fig.add_subplot(gs[i+1]) for i in range(len(n_values))]
    # top_ax = axes[0]
    # xmin, xmax = top_ax.get_xlim()
    # xmin = max(xmin, 1e-6)
    # log_min = math.log10(xmin)
    # log_max = math.log10(xmax)

    ##########
    # Adjust GridSpec to create extra rows for "Work Overhead" bars
    # fig = plt.figure(figsize=(10, 5 * len(n_values) + 1*len(n_values)))
    # gs = gridspec.GridSpec(len(n_values) * 2, 1, height_ratios=[0.2] * len(n_values) + [1] * len(n_values), hspace=0.4)

    # # Regular subplots below for data
    # axes = [fig.add_subplot(gs[i * 2 + 1]) for i in range(len(n_values))]
    # top_ax = axes[0]
    # xmin, xmax = top_ax.get_xlim()
    # xmin = max(xmin, 1e-6)
    # log_min = math.log10(xmin)
    # log_max = math.log10(xmax)

    # # Create the "Work Overhead" bars for each subplot
    # for i, ax in enumerate(axes):
    #     # Create a new axis at the top of each subplot for the "Work Overhead" label
    #     bar_ax = fig.add_subplot(gs[i * 2])  # Top bar for each subplot
    #     bar_ax.axis('off')  # Remove axis from this bar

    #     # Add "Work Overhead" label and shade the bar
    #     bar_ax.text(0.5, 0.5, "Work Overhead", ha='center', va='center', fontsize=12, weight='bold')
    #     bar_ax.set_facecolor("#d3d3d3")  # Light gray shading for the bar

    #     # Continue with plotting the actual data on the main axes (ax)
    #     processor_data = get_processor_breakpoints(all_data_prob, n_values[i], min_processors=1, max_processors=max_p)
    #     processor_counts = list(processor_data.keys())

    n_colors = ["blue", "orange", "green", "red", "purple"]
    marker_styles = ['o', 's', '^', 'D', 'P', '*', 'v', 'X', 'h']

    for i, (ax, n) in enumerate(zip(axes, n_values)):
        processor_data = get_processor_breakpoints(all_data_prob, n, min_processors=1, max_processors=max_p)
        processor_counts = list(processor_data.keys())
        # color = n_colors[i]

        # for j in range(1, max_p,100):
        #     p1 = j
        #     p2 = j+100
        #     prev_proc_pt1=1
        #     for proc_pt1 in processor_counts:
        #         if proc_pt1==p1:
        #             algo1 = processor_data[p1]["algorithm"]
        #             work=processor_data[p1]["work"]
        #             break
        #         if proc_pt1>p1:
        #             algo1=processor_data[prev_proc_pt1]["algorithm"]
        #             work=processor_data[prev_proc_pt1]["work"]
        #             break
        #         prev_proc_pt1=proc_pt1
        #     prev_proc_pt2=1
        #     for proc_pt2 in processor_counts:
        #         if proc_pt2==p2:
        #             algo2 = processor_data[p2]["algorithm"]
        #             work=processor_data[p2]["work"]
        #             break
        #         if proc_pt2>p2:
        #             algo2=processor_data[prev_proc_pt2]["algorithm"]
        #             work=processor_data[prev_proc_pt2]["work"]
        #             break
        #         prev_proc_pt2=proc_pt2

        #     rt1 = get_runtime(all_data[algo1]["work"], all_data[algo1]["span"], n, p1, all_data[algo1]["parallel"])
        #     rt2 = get_runtime(all_data[algo2]["work"], all_data[algo2]["span"], n, p2, all_data[algo2]["parallel"])

        #     speedup1 = processor_data[1]["runtime"] / rt1  # serial over parallel
        #     speedup2 = processor_data[1]["runtime"] / rt2

        #     overhead = work / processor_data[1]["work"]

        #     # # Midpoint in log space
        #     # mid_x = 10 ** ((math.log10(p1) + math.log10(p2)) / 2)
        #     # mid_y = 10 ** ((math.log10(speedup1) + math.log10(speedup2)) / 2)

        #     # Draw segment manually
        #     ax.plot([p1, p2], [speedup1, speedup2], color=color, linestyle='-')

        #     # # Label the segment
        #     # label = f"{algo2}, {overhead:.2f}×"
        #     # ax.text(mid_x, mid_y, label, fontsize=8, ha='center', va='bottom', color=color)

        ############# my attempts for a rational function
        # color = n_colors[i]
        # serial_runtime=processor_data[1]["work"]

        # for j in range(len(processor_counts)-1):
        #     p1 = processor_counts[j]
        #     p2 = processor_counts[j+1]
        #     algo= processor_data[p1]["algorithm"]
        #     work_numerical=processor_data[p1]["work"]
        #     span=all_data[algo]["span"]
        #     span_fn=get_comp_fn(span)
        #     span_numerical=span_fn(n)
        #     parallel=int(all_data[algo]["parallel"])

        #     def speedup_function(p):
        #         return serial_runtime/((work_numerical-span_numerical)/p + span_numerical + parallel)

        #     x_vals = [i for i in range(p1,p2,100)]
        #     y_vals = [speedup_function(p) for p in x_vals]

        #     plt.plot(x_vals, y_vals)

        ##############


        algorithm_markers = {}
        marker_index = 0
        color = n_colors[i]

        speedups = []
        labels = []
        shade_colors = ["#f0f0f0", "#e0e0ff"]  # alternating shades
        shade_idx = 0

        for j in range(len(processor_counts)):
            p = processor_counts[j]
            data = processor_data[p]
            algo = data["algorithm"]

            ax.axvline(x=p, color='gray', linestyle='--', linewidth=0.8)



            if algo not in algorithm_markers:
                algorithm_markers[algo] = marker_styles[marker_index % len(marker_styles)]
                marker_index += 1
            marker = algorithm_markers[algo]

            speedup = processor_data[1]["runtime"] / data["runtime"]
            overhead = data["work"] / processor_data[1]["work"]

            speedups.append((p, speedup))

            if p!=max_p:
                ax.scatter(p, speedup, marker=marker, color=color)
                labels.append((p, speedup, f"{algo}, {overhead:.2f}x"))

                # Shade region between this and next processor count
                p_next = processor_counts[j + 1]
                ax.axvspan(p, p_next, facecolor=shade_colors[shade_idx % len(shade_colors)], alpha=0.3)
                shade_idx += 1

                # Midpoint in log space for label placement
                mid_x = 10 ** ((math.log10(p) + math.log10(p_next)) / 2)
                mid_y= 10 ** ((math.log10(speedup) + math.log10(processor_data[1]["runtime"] / processor_data[p_next]["runtime"])) / 2)

                ax.text(mid_x, processor_data[1]["runtime"] / processor_data[max_p]["runtime"], f"{overhead:.0f}×",
                        fontsize=8, ha='center', va='bottom', clip_on=False)
                ax.text(mid_x, mid_y, f"{algo}",
                        fontsize=8, ha='center', va='bottom', clip_on=False)
                # ax.text(mid_x, processor_data[1]["runtime"] / processor_data[max_p]["runtime"], f"{algo}\n{overhead:.2f}×",
                #         fontsize=8, ha='center', va='bottom', clip_on=False)


        # Sort and plot line
        speedups.sort()
        x_vals, y_vals = zip(*speedups)
        ax.plot(x_vals, y_vals, color=color, label=f"$n = {get_nice_n(n)}$")

        # # Add annotations
        # for (p, y, label) in labels:
        #     ax.annotate(label, (p, y), textcoords="offset points", xytext=(5, 5), fontsize=8)

        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_ylabel("Speedup")
        ax.set_title(f"Speedup vs Processors ($n = {get_nice_n(n)}$)\nWork Overhead")
        ax.axhline(y=1, color='gray', linestyle=':', linewidth=1)
        ax.grid(True, which='both', ls='--', linewidth=0.5)
        # ax.text(10**5, ax.get_ylim()[1], "Work Overhead", ha='center', va='top', fontsize=16)

    axes[-1].set_xlabel("Number of Processors")
    plt.tight_layout()
    plt.savefig(SAVE_LOC + f'speedup_separated_{problem}.png')


def problem_speedup_vs_proc_three_curves(all_data, problem, n_values=[10**3], max_p=10**9, point_number=1000):
    '''makes the speedup (and work overhead) vs processors graph
    "fastest parallel algorithm and work overhead for [problem]"
    one graph for each problem size n value, where x axis is the number of processors
    and y axis is the speedup of the fastest parallel algorithm at that processor number relative to best serial algorithm

    input:
        all_data: dictionary with all algorithms (serial and parallel combined)
        problem: string (has to match the exact problem string that the dictionary will have)
        n_values: list of problem size n values
        max_p: integer, maximum processor number to plot
        point_number: integer, how many points to logarithmically sample in each algorithm segment
    output:
        saves graph to SAVE_LOC + f'speedup_separated_{problem}_curves.png'
        (SAVE_LOC determined in header.py)
    '''
    all_data_prob = {
            name: info for name, info in all_data.items() if info.get("problem") == problem
    }

    fig, axes = plt.subplots(len(n_values), 1, figsize=(10, 5.5 * len(n_values)), constrained_layout=True)

    if len(n_values) == 1:
        axes = [axes]

    algorithm_backgrounds = {}
    background_color_index = 0
    background_colors = plt.cm.Pastel2.colors
    color = "black"


    for i, (ax, n) in enumerate(zip(axes, n_values)):
        max_y_limit = 1.0
        processor_data = get_processor_breakpoints(all_data_prob, n, min_processors=1, max_processors=max_p)
        processor_counts = sorted(list(processor_data.keys())) # Sort the breakpoints

        last_breakpoint_p = processor_counts[-1]
        serial_runtime = processor_data[processor_counts[0]]["runtime"]
        top_y_base = serial_runtime / processor_data[last_breakpoint_p]["runtime"]


        for j in range(len(processor_counts) - 1):
            p1 = processor_counts[j]
            p2 = processor_counts[j + 1]
            data = processor_data[p1]
            algo = data["algorithm"]

            # Assign background shade if it's a new algorithm
            if algo not in algorithm_backgrounds:
                algorithm_backgrounds[algo] = background_colors[background_color_index]
                background_color_index = (background_color_index + 1) % len(background_colors)

            work = data["work"]
            work_enc = all_data[algo]["work"]
            span = all_data[algo]["span"]
            parallel = int(all_data[algo]["parallel"])

            overhead = work / serial_runtime
            span_fn = get_comp_fn(span)
            span_val = span_fn(n)
            overhead_upper = overhead

            ps = np.logspace(np.log10(p1), np.log10(p2), point_number)
            speedups_curve = [serial_runtime / get_runtime(work_enc, span, n, p, parallel) for p in ps]

            ax.plot(ps, speedups_curve, color=color)

            ax.axvline(x=p1, color='gray', linestyle='--', linewidth=1.2)

            ax.axvspan(p1, p2, facecolor=algorithm_backgrounds[algo], alpha=0.3)

            stagger_level = (j % 2)
            y_pos_multiplier = 1.8 if stagger_level == 0 else 3.0
            label_y_pos = top_y_base * y_pos_multiplier
            max_y_limit = max(max_y_limit, label_y_pos)

            beautified_algo = algo.replace('_', ' ').replace('-', ' ').title()

            if round(overhead) <= 1 and round(overhead_upper) <= 1:
                overhead_str = "≈1x"
            else:
                overhead_str = f"{overhead:.1f}×" if abs(overhead - overhead_upper) < 0.1 else f"{overhead:.1f}×–{overhead_upper:.1f}×"


            mid_x = 10 ** ((math.log10(p1) + math.log10(p2)) / 2)
            label_text = f"{beautified_algo}\nWork Overhead: {overhead_str}"
            ax.text(mid_x, label_y_pos, label_text, fontsize=12, ha='center', va='top', clip_on=False)


        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_ylabel("Speedup", fontsize=16)
        ax.set_title(f"$n = {get_nice_n(n)}$", fontsize=19)

        ax.axhline(y=1, color='gray', linestyle=':', linewidth=2)
        ax.grid(True, which='major', axis='y', ls='--', linewidth=2)
        ax.set_xlim(1, max_p)
        ax.set_ylim(0.9, max_y_limit * 1.2)
        ax.tick_params(axis='both', which='major', labelsize=13.5)


    axes[-1].set_xlabel("Number of Processors", fontsize=16)
    problem_name = "Topological Sorting"
    fig.suptitle(f"Fastest Parallel Algorithm and Work Overhead for {problem_name}", fontsize=20)

    plt.savefig(SAVE_LOC + f'speedup_separated_{problem}_curves.png')
