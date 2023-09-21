#include "Generator.hpp"

#include <algorithm>
#include <iomanip>
#include <iostream>
#include <random>
#include <vector>

Generator::Generator(std::vector<std::vector<int>>& board, int width, int height, int block_num, int shuffle_num) {
    for (const auto& row : board) {
        std::ranges::copy(row, std::back_inserter(this->initial_board));
    }
    this->board = initial_board;
    this->width = width;
    this->height = height;
    this->block_num = block_num;
    this->shuffle_num = shuffle_num;
}

void Generator::shuffle() {
    std::random_device seed_gen;
    std::mt19937 rand_engine(seed_gen());
    auto get_rand = [&rand_engine](int max) -> int { return rand_engine() % max; };

    for (int i = 0; i < shuffle_num; i++) {
        // for (int i = 0; i < width * height; i++) {
        //    std::cout << std::setw(3) << board[i] << ((i + 1) % width == 0 ? "\n" : " ");
        //}
        std::vector<std::vector<int>> idxs(block_num + 1);
        for (int i = 0; i < width * height; i++) {
            idxs[board[i]].push_back(i);
        }

        int space_idx = idxs[0][get_rand(idxs[0].size())];
        int dir = get_rand(DIR_NUM);
        int block_idx = space_idx + DIR_VEC[dir].first * width + DIR_VEC[dir].second;
        if (block_idx < 0 || block_idx >= width * height) {
            // auto first = space_idx / width + DIR_VEC[dir].first;
            // auto second = space_idx % width + DIR_VEC[dir].second;
            // std::cout << "invalid block_coord: [" << first << ' ' << second << ']' << std::endl;
            i--;
            continue;
        }
        int block_id = board[block_idx];
        switch (dir) {
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

        // std::cout << "\nblock_id: " << block_id << ", dir: " << DIR_CHAR[dir] << std::endl;
        if (!is_movable(block_id, idxs[block_id], dir)) {
            // auto first = space_idx / width + DIR_VEC[dir].first;
            // auto second = space_idx % width + DIR_VEC[dir].second;
            // std::cout << "not movable: [" << first << ", " << second << ']' << std::endl;
            i--;
            continue;
        }

        for (const auto& idx : idxs[block_id]) {
            board[idx] = 0;
        }
        for (const auto& idx : idxs[block_id]) {
            auto first = idx / width + DIR_VEC[dir].first;
            auto second = idx % width + DIR_VEC[dir].second;
            board[first * width + second] = block_id;
        }
    }
}

std::vector<std::vector<int>> Generator::get_board() const {
    std::vector<std::vector<int>> board(height, std::vector<int>(width));
    for (int i = 0; i < width * height; i++) {
        board[i / width][i % width] = this->board[i];
    }
    return board;
}

bool Generator::is_movable(int block_id, std::vector<int>& block_idxs, int dir) {
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