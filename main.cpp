#include <fstream>
#include <iostream>

#include "./nlohmann/json.hpp"

#include "./modules/Generator/Generator.hpp"
#include "./modules/Solver/Solver.hpp"

const std::string CONFIG_FILEPATH = "./config/params.json";

int main() {
    std::ifstream ifs(CONFIG_FILEPATH);
    nlohmann::json config;
    ifs >> config;

    int width = config["width"].get<int>();
    int height = config["height"].get<int>();
    std::vector<std::vector<int>> board = config["input"];

    std::vector<int> block_types = config["block_types"];
    int block_num = config["block_num"].get<int>();
    int shuffle_num = config["shuffle_num"].get<int>();

    int goal_block_idx = config["goal_block_id"].get<int>();
    std::vector<std::vector<int>> coords = config["goal_coords"];
    std::vector<std::pair<int, int>> goal_coords;
    for (const auto& coord : coords) {
        goal_coords.emplace_back(coord[0], coord[1]);
    }

    Generator Generator(board, width, height, block_num, shuffle_num);
    Generator.shuffle();
    auto shuffled_board = Generator.get_board();
    std::cout << "shuffled_board: " << std::endl;
    for (const auto& row : shuffled_board) {
        for (const auto& elem : row) {
            std::cout << elem << ' ';
        }
        std::cout << std::endl;
    }

    Solver Solver(shuffled_board, width, height, goal_block_idx, goal_coords, block_num, block_types);
    Solver.bfs();
    auto [process, steps, states] = Solver.get_result();
    std::cout << "states: " << states << std::endl;
    std::cout << "steps: " << steps << std::endl;
    std::cout << process << std::endl;

    auto zero_indexed_shuffled_board = shuffled_board;
    for (int i = 0; i < height; i++) {
        for (int j = 0; j < width; j++) {
            zero_indexed_shuffled_board[i][j]--;
        }
    }

    std::vector<int> block_ids;
    std::vector<char> dirs;
    std::size_t i = 0;
    while (i < process.length()) {
        std::string id;
        while (std::isdigit(static_cast<char>(process[i]))) {
            id += process[i];
            i++;
        }
        block_ids.push_back(std::stoi(id));
        dirs.push_back(process[i]);
        i++;
    }
    std::string zero_indexed_process;
    for (std::size_t i = 0; i < block_ids.size(); i++) {
        zero_indexed_process += std::to_string(block_ids[i] - 1);
        zero_indexed_process += dirs[i];
    }

    config["output"] = zero_indexed_shuffled_board;
    config["states"] = states;
    config["steps"] = steps;
    config["process"] = zero_indexed_process;

    std::ofstream ofs(CONFIG_FILEPATH);
    ofs << config.dump(4) << std::endl;
}