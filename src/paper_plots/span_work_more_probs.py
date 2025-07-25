from header import *
from src.thesis_plots.span_work_problem import pareto_frontier_helper

def span_vs_work_multiple_probs_pareto_frontier(par_data,seq_data,problems,allowed_models=set(model_dict.keys())):
    
    plt.style.use('default')
    fig, ax = plt.subplots(1,1,figsize=(6.55,3),dpi=200,layout='tight')

    pareto_points_dict = {}

    all_sp = set()
    all_wk = set()
    for i in range(len(problems)):
        prob = problems[i]
        color = COLORS[i]
        pareto_points, best_seq = get_pareto_points(par_data,seq_data,prob,allowed_models=allowed_models)

        if prob == "Topological Sorting":
            pareto_points = [#'56Chaudhuri (1992)',
                             #ID used to be 18 in the name but not anymore?? im changing the hardcoding and hoping for it to not mess up down the line
                             '56718Chaudhuri (1992)', 
                            #   '56719Li, Pan, Shen (2003)',
                                '56720Schudy (2008)'
                                #'13Schudy (2008)'
                                #'56Schudy (2008)'
                                ]
        elif prob == "LCS":
            pareto_points = [#'4256Aggarwal & Park (1988)', 
                            '4Aggarwal & Park (1988)', 
                            #  '4257Alves, Cáceres, Song (2003)', 
                             #'4260Babu, Saxena (1997)', 
                             #'4261Babu, Saxena (1997)', 
                              '4Babu, Saxena (1) (1997)',
                             '4Babu, Saxena (2) (1997)'
                            #  '4267Hsu, Du (1984)', 
                            #  '4270Krusche, Tiskin (2010)', 
                            #  '4272Lin, Lu, Fang (1991)'
                             ]
        elif prob == "Bipartite Graph MCM":
            pareto_points = [#'28594Shiloach, Vishkin (1982)',
                             '28Shiloach, Vishkin (1982)', 
                             #'28595Kim, Chwa (1987)'
                             '28Kim, Chwa (1987)']


        pareto_s_w_pairs = {(par_data[x]["span"],par_data[x]["work"]) for x in pareto_points}
        pareto_s_w_pairs.add((seq_data[best_seq]["time"],seq_data[best_seq]["time"]))


        for sp,wk in pareto_s_w_pairs:
            all_sp.add(sp)
            all_wk.add(wk)

        pareto_s_w_pairs = sorted(pareto_s_w_pairs, key=lambda x: (x[0],-x[1]))

        print(pareto_s_w_pairs)

        pareto_points_dict[prob] = pareto_s_w_pairs

    all_sp = sorted(all_sp)
    all_wk = sorted(all_wk)

    for i in range(len(problems)):
        prob = problems[i]
        color = COLORS[i]
        xpts = []
        ypts = []
        for span,work in pareto_points_dict[prob]:
            xpt = bisect.bisect_left(all_sp,span)
            ypt = bisect.bisect_left(all_wk,work)
            xpts.append(xpt)
            ypts.append(ypt)
            ax.scatter(xpt,ypt,c=color)
        #ax.step(xpts,ypts,c=color)
        #this should make it go horizontal first and then step down
        ax.step(xpts, ypts, c=color, where='post')

    # legend
    handles = []
    for i in range(len(problems)):
        new_patch = mpatches.Patch(color=str(COLORS[i]), label=problems[i])
        handles.append(new_patch)
    # ax.legend(handles=handles)
    #text_pos = [(3.6,0.8),(3.7,4.8),(4.2,3)]
    #manually tweaking where the labels go
    text_pos = [(2.4, 0.5), (4.2, 4.8), (2.8, 2)]
    for i in range(len(problems)):
        ax.text(text_pos[i][0],text_pos[i][1],problem_dict[problems[i]],color=COLORS[i],
                fontsize=10,verticalalignment='center')

    ax.set_xlim([-0.5, len(all_sp)-0.5])
    ax.set_ylim([-0.5, len(all_wk)-0.5])
    ax.set_xticks(list(range(len(all_sp))),["\n"*(i%2) + "$"+TIME_CODES[x][3:-2]+"$" for i,x in enumerate(all_sp)])
    ax.set_yticks(list(range(len(all_wk))),["$"+TIME_CODES[x][3:-2]+"$" for x in all_wk])
    ax.set_ylabel("Total # Computations (Work), O(.)")
    ax.set_xlabel("Computation Length (Span), O(.)")
    ax.set_title("Work - Span Tradeoff for Parallel Algorithms")

    plt.savefig(SAVE_LOC+'span_vs_work_pareto_multiple_problems.png')
    # plt.show()
    pass

# helper function, only includes points that are at endpoints/corners of the frontier
# pareto_points: set of (span,work) pairs
# TODO: might not be needed, check how overhead vs speedup does it
def reduce_pareto_points(pareto_points):
    reduced_pareto_points = set()
    all_sp = set(sp for sp,wk in pareto_points)
    all_wk = set(wk for sp,wk in pareto_points)

    for sp,wk in sorted(pareto_points,key= lambda x: (x[0],-x[1]) ):
        pass

    pass



def span_vs_work_multiple_probs(par_data,seq_data,problems,allowed_models=set(model_dict.keys())):
    plt.style.use('default')
    fig, ax = plt.subplots(1,1,figsize=(6.55,4.5),dpi=200,layout='tight')

    # for each problem, compute its pareto frontier line (as a set of algorithms/names)
    # then compute the points numerically and plot them

    # acquiring points to plot and axis values
    pareto_endpoints = {} # for line only (only plotting the ends of the pareto frontier)
    all_sp = set()
    all_wk = set()
    for prob in problems:
        pareto_points, best_seq = get_pareto_points(par_data,seq_data,prob,allowed_models=allowed_models)
        print(pareto_points)

        pareto_s_w_pairs = {(par_data[x]["span"],par_data[x]["work"]) for x in pareto_points}
        pareto_s_w_pairs.add((seq_data[best_seq]["time"],seq_data[best_seq]["time"]))

        pareto_lft = min(pareto_s_w_pairs,key=lambda x: (x[0],x[1]))
        pareto_rgt = min(pareto_s_w_pairs,key=lambda x: (x[1],x[0]))
        pareto_endpoints[prob] = (pareto_lft,pareto_rgt)

        for sp,wk in {pareto_lft,pareto_rgt}:
            all_sp.add(sp)
            all_wk.add(wk)
    all_sp = sorted(all_sp)
    all_wk = sorted(all_wk)

    print(all_sp)
    print(all_wk)

    print(pareto_endpoints)

    # plotting each line
    for i in range(len(problems)):
        prob = problems[i]
        color = COLORS[i]
        adj_endpts = []
        for span,work in pareto_endpoints[prob]:
            # span = par_data[pname]["span"]
            # work = par_data[pname]["work"]
            xpt = bisect.bisect_left(all_sp,span)
            ypt = bisect.bisect_left(all_wk,work)
            ax.scatter(xpt,ypt,c=color)
            adj_endpts.append((xpt,ypt))
        ax.plot([adj_endpts[0][0],adj_endpts[1][0]],[adj_endpts[0][1],adj_endpts[1][1]],
                c=color,linestyle='dashed')
        
    handles = []
    for i in range(len(problems)):
        new_patch = mpatches.Patch(color=str(COLORS[i]), label=problems[i])
        handles.append(new_patch)
    ax.legend(handles=handles)

    ax.set_ylabel("Work Complexity")
    ax.set_xlabel("Span Complexity")
    ax.set_xticks(list(range(len(all_sp))),[TIME_CODES[x] for x in all_sp])
    ax.set_yticks(list(range(len(all_wk))),[TIME_CODES[x] for x in all_wk])
    plt.show()
    pass
