#include "./nlohmann/json.hpp"

#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>

const std::string CONFIG_FILEPATH = "./config/params.json";

std::string board_to_string(const std::vector<std::vector<int>>& board, const std::vector<int>& block_types) {
    std::string str = "";
    for (auto row : board) {
        for (auto cell : row) {
            str += static_cast<char>(cell != -1 ? static_cast<int>('A') + block_types[cell] : 'x');
        }
    }
    return str;
}

bool is_movable(const std::vector<std::vector<int>>& board, const int block_idx, const char direction, const std::map<char, std::pair<int, int>>& DIRECTIONS) {
    std::vector<std::pair<int, int>> block_coords;
    for (std::size_t i = 0; i < board.size(); i++) {
        for (std::size_t j = 0; j < board[0].size(); j++) {
            if (board[i][j] == block_idx) {
                block_coords.push_back({i, j});
            }
        }
    }

    for (const auto& coord : block_coords) {
        auto next_coord = coord;
        next_coord.first += DIRECTIONS.at(direction).first;
        next_coord.second += DIRECTIONS.at(direction).second;
        if (next_coord.first < 0 || next_coord.first >= static_cast<int>(board.size()) || next_coord.second < 0 || next_coord.second >= static_cast<int>(board[0].size())) {
            return false;
        }
        if (board[next_coord.first][next_coord.second] == block_idx) {
            continue;
        }
        if (board[next_coord.first][next_coord.second] != -1) {
            return false;
        }
    }
    return true;
}

int main() {
    // std::random_device seed_gen;
    // std::mt19937 rand_engine(seed_gen());
    // auto rand = [&rand_engine](int max) -> int { return rand_engine() % max; };

    std::ifstream ifs(CONFIG_FILEPATH);
    nlohmann::json config;
    ifs >> config;

    std::pair<int, int> SIZE = {config["height"].get<int>(), config["width"].get<int>()};
    std::vector<std::vector<int>> board = config["board"];
    std::vector<int> BLOCK_TYPES = config["block_types"];

    int GOAL_BLOCK_IDX = config["goal_block_idx"].get<int>();
    std::vector<std::vector<int>> GOAL_COORDS = config["goal_coords"];

    std::map<char, std::pair<int, int>> DIRECTIONS = {
        {'U', {-1, 0}},
        {'R', {0, 1}},
        {'D', {1, 0}},
        {'L', {0, -1}},
    };

    std::queue<std::vector<std::vector<int>>> board_que;
    board_que.push(board);
    std::queue<std::string> path_que;
    path_que.push("");
    std::set<std::string> seen;
    seen.insert(board_to_string(board, BLOCK_TYPES));

    while (!board_que.empty() && !path_que.empty()) {
        auto curr_board = board_que.front();
        board_que.pop();
        auto curr_path = path_que.front();
        path_que.pop();

        std::vector<std::pair<int, int>> space_coords;
        for (int i = 0; i < SIZE.first; i++) {
            for (int j = 0; j < SIZE.second; j++) {
                if (curr_board[i][j] == -1) {
                    space_coords.push_back({i, j});
                }
            }
        }

        for (const auto& space_coord : space_coords) {
            for (auto& [key, value] : DIRECTIONS) {
                auto block_coord = space_coord;
                block_coord.first += value.first;
                block_coord.second += value.second;
                if (block_coord.first < 0 || block_coord.first >= SIZE.first || block_coord.second < 0 || block_coord.second >= SIZE.second) {
                    continue;
                }
                if (curr_board[block_coord.first][block_coord.second] == -1) {
                    continue;
                }

                auto swap_block_idx = curr_board[block_coord.first][block_coord.second];
                auto next_board = curr_board;
                char direction = key;
                switch (key) {
                    case 'U':
                        direction = 'D';
                        break;
                    case 'R':
                        direction = 'L';
                        break;
                    case 'D':
                        direction = 'U';
                        break;
                    case 'L':
                        direction = 'R';
                        break;
                }

                if (!is_movable(curr_board, swap_block_idx, direction, DIRECTIONS)) {
                    continue;
                }

                std::vector<std::pair<int, int>> swapping_coords;
                for (int i = 0; i < SIZE.first; i++) {
                    for (int j = 0; j < SIZE.second; j++) {
                        if (curr_board[i][j] == swap_block_idx) {
                            next_board[i][j] = -1;
                            swapping_coords.push_back({i, j});
                        }
                    }
                }
                for (auto& coord : swapping_coords) {
                    coord.first += DIRECTIONS.at(direction).first;
                    coord.second += DIRECTIONS.at(direction).second;
                    next_board[coord.first][coord.second] = swap_block_idx;
                }

                auto next_board_str = board_to_string(next_board, BLOCK_TYPES);
                if (seen.contains(next_board_str)) {
                    continue;
                }
                seen.insert(next_board_str);

                auto next_path = curr_path + std::to_string(swap_block_idx) + direction;
                board_que.push(next_board);
                path_que.push(next_path);

                if (swap_block_idx != GOAL_BLOCK_IDX) {
                    continue;
                }

                bool is_goal = true;
                for (const auto& goal_coord : GOAL_COORDS) {
                    if (next_board[goal_coord[0]][goal_coord[1]] != GOAL_BLOCK_IDX) {
                        is_goal = false;
                        continue;
                    }
                }
                if (is_goal) {
                    std::cout << "goal!" << std::endl;
                    std::cout << "steps: " << next_path.size() / 2 << std::endl;
                    std::cout << next_path << std::endl;
                    return 0;
                }
            }
        }
    }
}