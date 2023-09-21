#pragma once

#include <algorithm>
#include <array>
#include <memory>
#include <set>
#include <string>
#include <tuple>
#include <vector>

class Solver {
  public:
    Solver(std::vector<std::vector<int>>& board, int width, int height, int goal_block_id, std::vector<std::pair<int, int>>& goal_block_coords, int block_num, std::vector<int>& block_types);
    void reset();
    void bfs();
    std::tuple<std::string, int, int> get_result() const;

  private:
    bool is_movable(const std::unique_ptr<int[]>& board, int block_id, std::vector<int>& block_idxs, int dir);
    bool is_goal(const std::unique_ptr<int[]>& board);
    std::size_t generate_hash(const std::unique_ptr<int[]>& board);

  private:
    std::vector<int> initial_board;
    int width;
    int height;

    int block_num;
    std::vector<int> block_types;

    int goal_block_id;
    std::vector<int> goal_idxs;

    std::string process;
    int steps;
    int states;

    static constexpr int DIR_NUM = 4;
    static constexpr std::array<char, DIR_NUM> DIR_CHAR = {'U', 'D', 'L', 'R'};
    static constexpr std::array<std::pair<int, int>, DIR_NUM> DIR_VEC = {{{-1, 0}, {1, 0}, {0, -1}, {0, 1}}};
};