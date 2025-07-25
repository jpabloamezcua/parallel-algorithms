from src.thesis_plots.strong_scaling import *
from src.thesis_plots.incremental_benefit_table import *
from src.thesis_plots.span_work_imprvmnt import *
from src.thesis_plots.span_perf_imprvmnt import *
from src.thesis_plots.relative_speedup import *
from src.thesis_plots.span_overhead import *
from src.thesis_plots.share_of_progress import *
from src.thesis_plots.work_eff_vs_overall_span import *
from src.thesis_plots.improved_families import *
from src.thesis_plots.decade_progress import *
from src.thesis_plots.pareto_frontier import *
from src.thesis_plots.aggregated_relative_speedup import *
from src.thesis_plots.span_work_problem import *
from src.thesis_plots.new_parallelism import *
from src.thesis_plots.weak_scaling import *
from src.thesis_plots.models import *
from src.thesis_plots.varying_scaling import *
from src.paper_plots import average_imprvmnt_rates
from src.paper_plots.span_work_more_probs import *
from src.paper_plots.num_overhead_vs_span import *
from src.paper_plots.problem_overhead_vs_proc import *
from src.paper_plots.problem_speedup_vs_proc import *
from src.paper_plots.aggregate_switch_to_work_ineff import *

from converter import *
from data.processor_data_acquisition import *
from src.processed_data import full_data, rel_speedup_seq_data, aux_data, top_processor_data, pc_processor_data, VERSION

from src.processed_data import *
import matplotlib.pyplot as plt



print("starting main")

def patch_data_with_parallel_field(data_dict):
    """
    Adds missing 'parallel' field to all entries in the data dictionary.
    Uses 'par' field to determine if algorithm is parallel (parallel=True if par > 0).
    """
    for name, entry in data_dict.items():
        if "parallel" not in entry:
            if "par" in entry and entry["par"] > 0:
                entry["parallel"] = 1
            else:
                entry["parallel"] = 0


################################################################################
################## DATA ########################################################
################################################################################

########## Refactor data
#import src.data_processing
#print(src.data_processing.raw_database.populate_raw_database_parallel())
# IDK WHAT'S GOING ON HERE
#import src.processed_data
#print(src.processed_data.raw_database.populate_raw_database_parallel())



########## End of refactor data

# print(find_proc_increase_supercomputer())
# print(find_best_top_every_year("top500_pre_2008"))

# print(find_best_top_every_year("cpu_short"))
# print(find_proc_increase_commercial())

model_sheet_name = "data/par_models_FEB18"
old_sheet_name = "past_data/parallel_sheet_for_models_JAN_8"
mod_map = {
    100: 130,
    110: 110,
    120: 120,
    130: 130,
    131: 130,
    132: 130,
    133: 130,
    135: 130,
    200: 200,
    210: 200,
    220: 200,
    300: 300,
    310: 300,
    320: 300,
    330: 300,
    400: 400,
    500: 500,
    510: 500,
    520: 500,
    600: 600,
    610: 600,
    700: 700,
    800: 600}
# make_model_plots(model_sheet_name,mod_map)

# convert_csv_to_json("data/par_algos_1")
# apply_various_operations_to_change_the_json_file_so_its_usable(name="data/par_algos_1",
#         wanted_fields=PARALLEL_ALGO_FIELDS,
#         unwanted_values=PARALLEL_DISCARABLE_FIELD_VALUES,
#         allowed_model_list = PARALLEL_ALLOWABLE_MODELS)


# create_seq_data("data/Sheet1"+VERSION,"data/Sheet1_New_Entries"+VERSION)
# create_par_data("data/Parallel_Algos"+VERSION)

def make_model_dataset(par_algos):
    jsonArray = []
    for name in par_algos:
        year = par_algos[name]["year"]
        model = par_algos[name]["model"]
        alg_id = par_algos[name]["id"]
        parallel = True
        jsonArray.append({"year":year,"model":model,"id":alg_id,"parallel":parallel})

    newJsonFilePath = r'./data/par_models_JUL21.json'
    with open(newJsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonString = json.dumps(jsonArray, indent=4)
        jsonf.write(jsonString)
    pass

make_model_dataset(simulated_par_data)

# Patch all data dictionaries to ensure they have the parallel field
patch_data_with_parallel_field(full_data)
patch_data_with_parallel_field(simulated_par_data)
patch_data_with_parallel_field(rel_speedup_seq_data)
all_problem_names = set(info.get("problem") for info in full_data.values() if info.get("problem"))
for elem in simulated_par_data:
    # print(simulated_par_data[elem]['id'])
    # print(type(simulated_par_data[elem]['id']))
    # break
    if simulated_par_data[elem]['id'] == '533':
        print(simulated_par_data[elem]['id'])

create_aux_data(simulated_par_data,full_seq_data)
create_aux_data(full_data,rel_speedup_seq_data)


# helpers

print(best_algos_by_speedup(simulated_par_data,full_seq_data,"LCS",n=10**6,
                          allowed_models=set(model_dict.keys())))

print(get_pareto_points(simulated_par_data,full_seq_data,'LCS',allowed_models=PRAM_LIKE_MODELS))





################## Extra Functions ############################

def year_stats():
    problems = get_problems(simulated_par_data)
    year_dict = {}
    for alg in simulated_par_data:
        yr = simulated_par_data[alg]["year"]
        pr = simulated_par_data[alg]["problem"]
        if pr in year_dict:
            year_dict[pr] = min(year_dict[pr], yr)
        else:
            year_dict[pr] = yr
    year_list = year_dict.values()
    print(year_list)
    dec_dict = {}
    for yr in year_list:
        dc = get_decade(yr)
        if dc not in dec_dict:
            dec_dict[dc] = 1
        else:
            dec_dict[dc] += 1
    print(dec_dict)
# year_stats()

def overflow_debugging():
    code1 = 8011.0
    code2 = 8010.0
    n = 10**3

    huge1 = Huge(max(math.log(max(math.log(n,2),1),2),1),n-1)
    huge1 = huge1 * (n * max(math.log(n,2),1))
    base2 = max(math.log(max(math.log(n,2),1),2),1)
    huge2 = Huge(base2, n+math.log(n,base2))

    print(huge1)
    print(huge2)
    print(huge1.evaluate())
    print(huge1 > huge2)
    print(huge1 == huge2)

    print("--------------------------------------")

    print(max(math.log(n,2),1))
    print(max(math.log(max(math.log(n,2),1),2),1))
    print(decimal.Decimal(int(n-1)))

    print(get_seq_runtime(code1,n)==huge1)
    print(get_seq_runtime(code1,n)==huge1.evaluate())

    print("--------------------------------------")

    print(get_seq_runtime(code1,n))
    print(log(get_seq_runtime(code1,n),10))

    print(get_seq_runtime(code2,n))

    rt = get_runtime(code1,code2,n,p=1)

    print("runtime:")
    print(rt)

    pass
# overflow_debugging()




# {'k Nearest Neighbors Search', 'undirected SSSP', 'Polygon Clipping with Arbitrary Clipping Polygon',
# 'Non-comparison Sorting', 'Bipartite Graph MCM', 'kth Order Statistic', '2-dimensional space',
# 'Single String Search', '2-Dimensional Delaunay Triangulation', 'Max Flow', 'DFA Minimization',
# '2-D Polynomial Interpolation', 'General Linear Programming', 'APSP', 'General Graph MCM',
# 'General Linear System', 'CC', 'Matrix Chain Scheduling Problem', 'Matrix Multiplication',
# 'Greatest Common Divisor', 'General Maximum-Weight Matching', 'SCCs', 'Intersection detection',
# 'Boolean Matrix Multiplication', 'Constructing Suffix Trees', 'directed SSSP', 'Variance Calculations',
# 'Line Drawing', '2-Player', '2-dimensional', 'undirected nonneg SSSP', 'Approximate MCOP',
# 'k-dimensional space', 'Reporting intersection points', '2D Maximum Subarray', 'directed MST; MST',
# 'CC; SCCs', 'Point-in-Polygon', 'Multiplication', '1D Maximum Subarray', 'MST', 'Matrix LU Decomposition',
# 'Topological Sorting', 'Comparison Sorting', '3-dimensional', 'General Permutations', 'LCS', 'OBST',
# 'Constructing Eulerian Trails in a Graph', 'Lossless Compression', 'General Root Computation',
# 'Constuct Voronoi Diagram', 'Edit Distance, constant-size alphabet',
# 'Transitive Reduction Problem of Directed Graphs', 'directed nonneg SSSP', 'Discrete Fourier Transform'}


# {'Matrix Multiplication', 'k Nearest Neighbors Search', 'directed nonneg SSSP',
# 'directed MST', 'Topological Sorting', 'MST', 'Enumerating Maximal Cliques', 'Multiplication',
# 'Boolean Matrix Multiplication', 'APSP', 'Matrix LU Decomposition', 'Bipartite Graph MCM',
# 'General Permutations', 'Determinant of Matrices with Integer Entries', '2D Maximum Subarray',
# 'General Linear System', 'Intersection detection', 'General Root Computation',
# 'Exact Laplacian Solver', 'Maximum Cut', 'undirected SSSP', 'Comparison Sorting',
# 'Constructing Eulerian Trails in a Graph', 'Transitive Reduction Problem of Directed Graphs',
# 'All Nearest Neighbors', 'Bipartite Maximum-Weight Matching', '2-dimensional Convex Hull',
# 'Constructing Suffix Trees', 'Point-in-Polygon', 'Non-comparison Sorting',
# 'General Maximum-Weight Matching', 'Polygon Clipping with Arbitrary Clipping Polygon',
# 'Single String Search', 'Variance Calculations', 'Subset Sum', '3-dimensional Convex Hull',
# '2-Dimensional Delaunay Triangulation', '2-D Polynomial Interpolation', 'CFG Parsing',
# '2-Dimensional Poisson Problem', 'k-dimensional space Closest Pair Problem',
# '2-Player Nash Equilibria', 'Max Flow', 'Line Drawing', '1D Maximum Subarray', 'DFA Minimization',
# 'All Permutations', 'Transitive Closure', 'directed SSSP', 'Stable Marriage Problem',
# 'Edit Distance, constant-size alphabet', 'General Graph MCM', 'OBST', 'directed APSP',
# 'Lossless Compression', 'LCS', 'Reporting intersection points', 'Discrete Fourier Transform',
# 'CC', '3-Dimensional Poisson Problem', 'kth Order Statistic',
# 'Transitive Closure of a symmetric Boolean matrix', 'undirected nonneg SSSP',
# 'Constuct Voronoi Diagram', 'Matrix Chain Scheduling Problem', 'SCCs', 'MCOP',
# '2-dimensional space Closest Pair Problem', 'Greatest Common Divisor', 'General Linear Programming'}


# nice problems:
# - 'Topological Sorting' - 2 steps, 3 par points, but only 1 model (?)
# - 'LCS' - 1 step, but lots of non-boring points
# - 'Bipartite Graph MCM' - 2 steps (2 par points)
# - 'MST' - 1 step, too many par points
# - 'Comparison Sorting' - same; also check 1988 MIMD-TC algo - span is higher than bseq
# - 'General Permutations' - same
# - 'APSP' - 1 step, quite boring
# - 'SCCs' - 1 step, 1 par algo
# - 'Variance Calculations' - 1 step, 1 par algo
# - '2-dimensional' - 1 step, quite a few par points
# - 'Point-in-Polygon' - 1 step, 1 par point
# - 'directed nonneg SSSP' - 1 step, 1 par algo

#check data correctness
with open("aux.json", "w") as json_file:
    json.dump(full_problem_data, json_file, indent=4)



print("running functions to make the actual graphs for the paper")
##### overall TODO's #####
#TODO: in the google sheet, check all relevant parallel algos have subproblem
#TODO: in the google sheet, check all relevant serial algos have subproblem filled in (both sheet1 and new entries to sheet1)
#TODO: sanity check work vs lower bounds for all problems for typos/mistakes
#TODO: use newest data version
## change version in header.py and converter.py and run converter.py
## make new folder for plots according to version
#TODO: go through each figure and decide if work should be T_1 or 2T_1-T_inf
#TODO: go through each figure and check that p is never larger than maximum useful p*
#TODO: look at get_runtime in helper_functions.py and check its calculating runtime correctly for both serial and parallel
#TODO: also look at get_seq_runtime and maybe change that since some functions might be calling it directly instead of get_runtime

# this sets the histogram bucket size - consider moving somewhere else
pset = get_problems(simulated_par_data)
#{"max": 0.001, "label": "0-0.1%"},
histo_buckets = [
            {"max": 0.001, "label": "~0%"},
            {"max": 0.03, "label": "0.1-3%"},
            {"max": 0.1, "label": "3-10%"},
            {"max": 0.3, "label": "10-30%"},
            {"max": 1, "label": "30-100%"},
            # {"max": 3, "label": "100-300%"},
            # {"max": 10, "label": "300-1000%"},
            # {"max": math.inf, "label": ">1000%"},
            ]


######### FIGURE 1 #########
print("figure 1.1: Algorithm Improvements over Time")
#TODO: test if what i have is correct (check which problems have lots of variations, do they scale down intuitively)
average_improvement_over_decade_graph(simulated_par_data,full_seq_data,DECADES)
average_improvement_over_decade_graph(simulated_par_data,full_seq_data,DECADES,var_weights="thesis_weight")

print("figure ??: Number of Parallel Processors Over Time")
#TODO: change colors? #done
available_processors(top_processor_data,pc_processor_data)

print("figure ??: Parallel Performance for All Pairs Shortest Paths Problem using processors available at the time")
#TODO: fix the manual gap labels #done?
#TODO: maybe do different colors for this one and the one above #done
#TODO: this is probably sparse apsp, so why does the problem say apsp? data error?
#TODO: if later the autoformat changes then make sure the y range is bottom:1, top: whatever the top is #done?
#TODO: are these proc values correct (hardcoded?)
speedup_for_available_processors(simulated_par_data,full_seq_data,'APSP', top_processor_data,pc_processor_data,n=10**6,seq=True)


######### FIGURE 2 #########
print("sankey style figure")
#TODO: try other colors
#TODO: fix the label & title overlap
#TODO: if the rightmost bar tick marks dont overlap because of thin categories, remove the buffer so every second one is not moved out
#TODO: change titles
#personal
#sankey_style_graph(full_data,simulated_par_data, n=10**6, p=8)
# #big
#sankey_style_graph(full_data,simulated_par_data, n=10**9, p=10**3)


######### FIGURE 3 #########
print("figure 1.3: Work - Span Tradeoff for Parallel Algorithms // Computational Length")
#TODO: make sure that the hardcoded values in this graph are still ok
#span_vs_work_multiple_probs_pareto_frontier(simulated_par_data,full_seq_data, problems=['Topological Sorting','LCS','Bipartite Graph MCM'])
print("figure 1.3: Work - Span Tradeoff for Parallel Algorithms // Speedup Relative to Sequantial Time")
numerical_overhead_vs_span(simulated_par_data,full_seq_data, problems=['Topological Sorting','LCS','Bipartite Graph MCM'],n=10**6)

print("figure 1.3: Best Span vs Best Work-efficient Algorithm Span for all Problems")
#TODO: make labels look nicer #done
#TODO: fix that one dotted line (change going to 0 to going to 100%) #done?
NEW_w_seq_span_comparison_best_vs_work_efficient(full_problem_data)


######### FIGURE 4 #########
print("figure 1.2: Algorithm Problem Average Yearly Improvement Rate (Sequantial and Parallel)")
#this one (should be) just parallel improvement: measures from best seq
#TODO: add labels to axis #done
average_imprvmnt_rates.yearly_impr_rate_histo_grid(
    full_data,
    histo_buckets,
    n_values=[10**3, 10**6, 10**9],
    p_values=[8, 10**3, 10**6],
    measure="rt"
)



######### FIGURE 5 #########
print("figure 1.4: Fastest Parallel Algorithm and Work Overhead for Topological Sorting (in dense graphs)")
#TODO: beutify algo names #done?
#TODO: place algo names/ "work overhead" somewhere nicer #done
#TODO: in actual paper will need have something in caption that points to an explanation in the text about ignoring constants
#TODO: why is there a vertical break?
#TODO: change 1x-1x to just 1x #done?
#TODO: bigger fonts for everything #done
#TODO: when things dont fit, move label outside of graph and add arrow #done?
#TODO: methodology addition about how we estimate work overhead and when we use each
problem_speedup_vs_proc_three_curves(full_data, 13.1, n_values=[10**3, 10**6, 10**9], max_p=10**10)

######### FIGURE 6 #########
print("figure 1.5: Work Overhead for the fastest algorithm")
#TODO: change % to x #Done
NEW_work_overhead_histogram_graph_multiple_p(simulated_par_data,full_seq_data,pset,p_values=[8,10**3,10**6],n_values=[10**3,10**6,10**9],
                            upper_bounds=[0,100,1000,10000,math.inf],
                            max_p=10**9,allowed_models=set(model_dict.keys()))
fastest_algo_work_eff(simulated_par_data, n=10**6, min_p=1, max_p=10**6)
# Ensure full_data is properly loaded before plotting #done
fastest_algo_work_eff(full_data, simulated_par_data, n=10**6, min_p=1, max_p=10**6, step=1)




# # probs=get_problems(full_data)
# # probs_seq=get_problems(full_seq_data)
# # probs_par=get_problems(simulated_par_data)
# # with open("problems.csv", mode="w", newline="") as file:
# #     writer = csv.writer(file)

# #     # Writing header
# #     writer.writerow(["Problem", "In sequential", "In Parallel"])

# #     # Writing data rows
# #     for item in sorted(probs):  # Sorting to maintain order
# #         writer.writerow([
# #             item,
# #             1 if item in probs_seq else 0,
# #             1 if item in probs_par else 0
# #         ])

# with open("best_algos.csv", mode="w", newline="") as file:
#     writer = csv.writer(file)
#     writer.writerow(["Problem", "Best span algo", "Best span", "Best sequential/best work algo","Best work", "If par WE exists: name", "Best WE span"])
#     for prob in full_problem_data:
#         writer.writerow([
#             prob,
#             full_problem_data[prob]["bs name"],
#             full_problem_data[prob]["bs span"],
#             full_problem_data[prob]["best seq name"],
#             full_problem_data[prob]["best seq"],
#             full_problem_data[prob]["we name"],
#             full_problem_data[prob]["we span"]

#         ])



print("finished main")
