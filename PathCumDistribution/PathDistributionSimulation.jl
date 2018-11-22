using PathDistribution
using DelimitedFiles

# Find cumulative data for graphs with increasing mininum capacity

localPath = "/home/joao/Desktop/lndRoutingStudy/PathCumDistribution/"

for i = 1:7

    # Get the increasing capacity threshold
    capacityThreshold = 10 ^ (i-1)

    # Get the corresponding adj matrix file
    adj_matrix = readdlm(string(localPath, "adjMatrix", string(capacityThreshold), ".txt"), '\t', Int, '\n')

    samples = monte_carlo_path_sampling(1, size(adj_matrix,1), adj_matrix)
    x_data_est, y_data_est = estimate_cumulative_count(samples)

    #Print number of paths
    println(string("Capacity: ", capacityThreshold))
    println(x_data_est)
    println(y_data_est)
end
