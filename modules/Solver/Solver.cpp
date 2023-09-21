#include "Solver.hpp"

#include <algorithm>
#include <functional>
#include <iomanip>
#include <iostream>
#include <memory>
#include <queue>
#include <ranges>
#include <tuple>

Solver::Solver(std::vector<std::vector<int>>& board, int width, int height, int goal_block_id, std::vector<std::pair<int, int>>& goal_coords, int block_num, std::vector<int>& block_types) {
    this->initial_board = std::vector<int>();
    for (auto& row : board) {
        std::ranges::copy(row, std::back_inserter(this->initial_board));
    }
    this->width = width;
    this->height = height;
    this->block_num = block_num;
    this->block_types = block_types;
    this->goal_block_id = goal_block_id;
    for (const auto& goal_coord : goal_coords) {
        this->goal_idxs.push_back(goal_coord.first * width + goal_coord.second);
    }
    this->process = "";
    steps = 0;
    states = 0;
}

void Solver::reset() {
    process = "";
    steps = 0;
    states = 0;
}

void Solver::bfs() {
    std::unique_ptr<int[]> board = std::make_unique<int[]>(width * height);
    std::ranges::copy(initial_board, board.get());

    std::set<std::size_t> searched_board_hashes;
    searched_board_hashes.insert(generate_hash(board));

    std::queue<std::pair<std::unique_ptr<int[]>, std::unique_ptr<std::string>>> que;
    que.push(std::pair(std::move(board), std::make_unique<std::string>(process)));

    states = 1;

    while (!que.empty()) {
        auto curr_board = std::move(que.front().first);
        auto curr_process = std::move(que.front().second);
        que.pop();

        // std::cout << "\nprocess: " << *curr_process << std::endl;
        // for (int i = 0; i < width * height; i++) {
        //    std::cout << std::setw(3) << curr_board[i] << ((i + 1) % width == 0 ? "\n" : " ");
        // }

        std::vector<std::vector<int>> idxs(block_num + 1);
        for (int i = 0; i < width * height; i++) {
            idxs[curr_board[i]].push_back(i);
        }

        for (const auto& space_idx : idxs[0]) {
            // std::cout << "space coord: " << space_idx / width << ", " << space_idx % width << std::endl;

            std::pair<int, int> space_coord = std::make_pair(space_idx / width, space_idx % width);
            for (int i = 0; i < DIR_NUM; i++) {
                std::pair<int, int> block_coord = std::make_pair(space_coord.first + DIR_VEC[i].first, space_coord.second + DIR_VEC[i].second);
                if (block_coord.first < 0 || block_coord.first >= height) {
                    continue;
                }
                if (block_coord.second < 0 || block_coord.second >= width) {
                    continue;
                }

                int block_id = curr_board[block_coord.first * width + block_coord.second];
                if (block_id == 0) {
                    continue;
                }

                int dir = i;
                switch (i) {
                    case 0:
                        dir = 1;
                        break;
                    case 1:
                        dir = 0;
                        break;
                    case 2:
                        dir = 3;
                        break;
                    case 3:
                        dir = 2;
                        break;
                }

                // std::cout << "block_id: " << block_id << ", dir: " << DIR_CHAR[dir] << std::endl;
                if (!is_movable(curr_board, block_id, idxs[block_id], dir)) {
                    // std::cout << "not movable" << std::endl;
                    continue;
                }
                // std::cout << "movable" << std::endl;

                std::unique_ptr<int[]> next_board = std::make_unique<int[]>(width * height);
                std::copy(curr_board.get(), curr_board.get() + width * height, next_board.get());

                for (const auto& idx : idxs[block_id]) {
                    next_board[idx] = 0;
                }
                for (const auto& idx : idxs[block_id]) {
                    auto first = idx / width + DIR_VEC[dir].first;
                    auto second = idx % width + DIR_VEC[dir].second;
                    next_board[first * width + second] = block_id;
                }

                auto next_hashes = generate_hash(next_board);
                if (searched_board_hashes.contains(next_hashes)) {
                    // std::cout << "already searched" << std::endl;
                    continue;
                }
                searched_board_hashes.insert(next_hashes);
                states++;

                std::string next_process = *curr_process + std::to_string(block_id) + DIR_CHAR[dir];

                // std::cout << next_process << std::endl;
                // for (int i = 0; i < width * height; i++) {
                //     std::cout << std::setw(3) << next_board[i] << ((i + 1) % width == 0 ? "\n" : " ");
                // }

                if (is_goal(next_board)) {
                    process = next_process;
                    steps = process.length() - std::ranges::count_if(process, [](char c) { return std::isdigit(c); });
                    return;
                }

                que.push(std::make_pair(std::move(next_board), std::make_unique<std::string>(next_process)));
            }
        }
    }
}

std::tuple<std::string, int, int> Solver::get_result() const {
    return std::tie(process, steps, states);
}

bool Solver::is_movable(const std::unique_ptr<int[]>& board, int block_id, std::vector<int>& block_idxs, int dir) {
    for (const auto& block_idx : block_idxs) {
        std::pair<int, int> block_coord = std::make_pair(block_idx / width, block_idx % width);
        std::pair<int, int> space_coord = std::make_pair(block_coord.first + DIR_VEC[dir].first, block_coord.second + DIR_VEC[dir].second);
        if (space_coord.first < 0 || space_coord.first >= height || space_coord.second < 0 || space_coord.second >= width) {
            return false;
        }
        if (board[space_coord.first * width + space_coord.second] == block_id) {
            continue;
        }
        if (board[space_coord.first * width + space_coord.second] != 0) {
            return false;
        }
    }
    return true;
}

bool Solver::is_goal(const std::unique_ptr<int[]>& board) {
    for (int i = 0; i < width * height; i++) {
        if (std::ranges::count(goal_idxs, i) == 0) {
            continue;
        }
        if (board[i] != goal_block_id) {
            return false;
        }
    }
    return true;
}

std::size_t Solver::generate_hash(const std::unique_ptr<int[]>& board) {
    std::string simple_board_str;
    for (int i = 0; i < width * height; i++) {
        simple_board_str += static_cast<char>(static_cast<int>('A') + (board[i] > 0 ? block_types[board[i] - 1] : 0));
    }
    return std::hash<std::string>()(simple_board_str);
}
