from header import *


def numerical_overhead_vs_span(par_data, seq_data, problems, n=10**6, allowed_models=set(model_dict.keys())):
    plt.style.use('default')
    fig, ax = plt.subplots(1, 1, figsize=(6.55, 3), dpi=200, layout='tight')

    for i in range(len(problems)):
        problem = problems[i]
        color = COLORS[i]
        pareto_points, best_seq = get_pareto_points(par_data, seq_data, problem, allowed_models=allowed_models)
        seq_time = seq_data[best_seq]["time"]

        if problem == "Topological Sorting":
            pareto_points = ['56Chaudhuri (1992)',
                             '56Li, Pan, Shen (2003)',
                             '56Schudy (2008)']
        elif problem == "LCS":
            pareto_points = [#'4Aggarwal & Park (1988)',
                             #'4Alves, Cáceres, Song (2003)',
                             '4Apostolico, Atallah, Larmore, McFaddin (1990)',
                             '4Babu, Saxena (1997)',
                             #'4Hsu, Du (1984)',
                             #'4Krusche, Tiskin (2010)',
                             #'4Lin, Lu, Fang (1991)'
                             ]
        elif problem == "Bipartite Graph MCM":
            pareto_points = ['28Shiloach, Vishkin (1982)',
                             '28Kim, Chwa (1987)']

        adj_points = []
        for p_name in pareto_points:
            span = par_data[p_name]["span"]
            work = par_data[p_name]["work"]
            xpt = get_seq_runtime(seq_time, n) / get_comp_fn(span)(n)
            ypt = get_comp_fn(work)(n) / get_seq_runtime(seq_time, n)
            adj_points.append((xpt, ypt))

        adj_points.append((1, 1))
        adj_points.sort()

        if problem == "Topological Sorting":
            adj_points = [(x * 1.1489, y) for x, y in adj_points]

        ax.scatter([x[0] for x in adj_points], [x[1] for x in adj_points], c=color)
        ax.step([x[0] for x in adj_points], [x[1] for x in adj_points], c=color)


    handles = []
    for i in range(len(problems)):
        new_patch = mpatches.Patch(color=str(COLORS[i]), label=problems[i])
        handles.append(new_patch)
    # ax.legend(handles=handles)
    text_pos = [(8*10**4,10**4),(100000*10**4,50*7),(10**3,10**5)]
    for i in range(len(problems)):
        ax.text(text_pos[i][0],text_pos[i][1],problem_dict[problems[i]],color=COLORS[i],
                fontsize=10,verticalalignment='center')

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel("Speedup Relative to Sequential Time")
    ax.set_ylabel("Extra Work vs Sequential")
    max_x = round(math.log(max(ax.get_xticks().astype(np.int64)),10))
    ax.set_xticks([10**i for i in range(max_x)],even_powers_list(max_x))
    ax.set_yticks(ax.get_yticks(),["{:,}".format(int(x.get_position()[1]))+"$\\times$" for x in ax.get_yticklabels()])
    ax.set_ylim(0.5,0.9*10**6)
    plt.savefig(SAVE_LOC+'numerical_overhead_vs_span.png')
    # plt.show()
    pass

def even_powers_list(max_num):
    res = []
    for i in range(max_num):
        if i == 0:
            res.append("$1$")
        elif i%2 == 0:
            res.append("$10^{"+str(i)+"}$")
        else:
            res.append("")
    return res
