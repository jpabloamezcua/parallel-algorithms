from header import *


def numerical_overhead_vs_span(par_data,seq_data,problems,n=10**6,allowed_models=set(model_dict.keys())):
    '''
    TODO
    '''
    plt.style.use('default')
    fig, ax = plt.subplots(1,1,figsize=(6.55,3),dpi=200,layout='tight')

    for i in range(len(problems)):
        problem = problems[i]
        color = COLORS[i]
        pareto_points, best_seq = get_pareto_points(par_data,seq_data,problem,
                                        allowed_models=allowed_models)
        print(problem)
        for pt in pareto_points:
            print("span = "+str(par_data[pt]["span"])+"; work = "+str(par_data[pt]["work"]))
        print(pareto_points)
        seq_time = seq_data[best_seq]["time"]
        if problem == "Topological Sorting":
            pareto_points = ['56Chaudhuri (1992)',
                             #ID used to be 18 in the name but not anymore?? im changing the hardcoding and hoping for it to not mess up down the line
                             #'56718Chaudhuri (1992)',
                            #   '56719Li, Pan, Shen (2003)',
                            #'56720Schudy (2008)',
                            #'13Schudy (2008)'
                            '56Schudy (2008)'
                            ]
        elif problem == "LCS":
            pareto_points = [#'4256Aggarwal & Park (1988)',
                            '4Aggarwal & Park (1988)',

                            #  '4257Alves, Cáceres, Song (2003)',
                            '4Babu, Saxena (1997)'
                            # '4260Babu, Saxena (1997)',
                             #'4261Babu, Saxena (1997)',
                             #'4Babu, Saxena (1) (1997)',
                             #'4Babu, Saxena (2) (1997)'
                            #  '4267Hsu, Du (1984)',
                            #  '4270Krusche, Tiskin (2010)',
                            #  '4272Lin, Lu, Fang (1991)'
                             ]
        elif problem == "Bipartite Graph MCM":
            pareto_points = [#'28594Shiloach, Vishkin (1982)',
                             '28Shiloach, Vishkin (1982)',
                              #'28595Kim, Chwa (1987)'
                              '28Kim, Chwa (1987)'
                              ]

        adj_points = []
        for p_name in pareto_points:
            span = par_data[p_name]["span"]
            work = par_data[p_name]["work"]

            # computing speedup relative to the work efficient algorithm
            # ratio between seq time and parallel time?? span for now
            xpt = get_seq_runtime(seq_time,n)/get_comp_fn(span)(n)

            # computing work overhead
            # ratio between parallel work and seq time
            ypt = get_comp_fn(work)(n)/get_seq_runtime(seq_time,n)

            adj_points.append((xpt,ypt))
        adj_points.append((1,1))

        adj_points.sort()

        ax.scatter([x[0] for x in adj_points],[x[1] for x in adj_points],c=color)
        ax.step([x[0] for x in adj_points],[x[1] for x in adj_points],c=color)

    handles = []
    for i in range(len(problems)):
        new_patch = mpatches.Patch(color=str(COLORS[i]), label=problems[i])
        handles.append(new_patch)
    # ax.legend(handles=handles)
    text_pos = [(10**4,10**4),(10**4,7),(10**3,10**5)]
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
