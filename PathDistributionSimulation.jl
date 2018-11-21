using PathDistribution
using DelimitedFiles

adj_matrix = readdlm("/home/joao/Desktop/lndRoutingStudy/adjMatrix.txt", '\t', Int, '\n')

no_path_est = monte_carlo_path_number(1, 8, adj_matrix, 50, 100)

print(no_path_est)

samples = monte_carlo_path_sampling(1, size(adj_matrix,1), adj_matrix)
x_data_est, y_data_est = estimate_cumulative_count(samples)
