# Executed mathematical model

## T1

Shelf pose is (x,y,rotation), rotation in {0,90}. Footprints must be covered by the boundary, disjoint from obstacles/other shelves, and meet min_aisle_m clearance. Locked shelves retain their pose. Constructive grid sweep varies shelf order, sweep direction and orientation priority. This is neither continuous geometry optimization nor an infeasibility proof.

## T2

Binary x_cs assigns category c to shelf s. Sum_s x_cs = 1. Sum_c required_width_c*x_cs <= sum usable level widths * shelf faces. Fixed assignments forbid other shelves. Near/separate restrictions forbid violating centroid-distance pairs.

Minimize sum_cs x_cs * distance_weight * demand_c*priority_c/sum(demand*priority) * distance(entrance,centroid_s)/floor_diagonal. The objective is dimensionless. It is not T4 walking distance. Several categories may share a shelf; category splitting and soft affinity are unsupported.

## T3

Each option specifies SKU, shelf, face, level, orientation, layers and depth_units. Width = facings*(oriented_width+clearance). Capacity = facings*layers*depth_units. Load = capacity*weight. Exactly one option per SKU; summed widths obey each level/face limit and loads share one limit across all faces of a level.

Maximize sum demand_sku*capacity_option*z_option. Demand is an objective weight, not a demand-satisfaction constraint. Blocks are concatenated along x, without mixed-SKU depth lanes or vertical interleaving. Every physically admissible layer/depth combination is enumerated. More than 20,000 options yields PROBLEM_LIMIT, not truncated-model infeasibility. OPTIMAL/INFEASIBLE apply only to this finite fixed-facing strip model.

## T4 and integrated selection

Route length includes grid segments plus both entrance connectors. Elapsed time = distance/speed + sum(quantity*dwell) + resource waiting. SKU pickup is tied to its T3 face.

Score is weighted_mean(mean_distance/floor_diagonal, mean_wait/horizon, sum positive(demand-capacity)/max(1,total demand)). Nondominance minimizes these three components over successfully evaluated candidates only. Baseline candidate 0 participates; ties select the smallest index. There is no global Pareto or joint optimality claim.
