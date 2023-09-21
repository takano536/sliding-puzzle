#pragma once

#include <array>
#include <string>
#include <vector>

class Generator {
  public:
    Generator(std::vector<std::vector<int>>& board, int width, int height, int block_num, int shuffle_num);
    void shuffle();
    std::vector<std::vector<int>> get_board() const;

  private:
    bool is_movable(int block_id, std::vector<int>& block_idxs, int dir);

  private:
    std::vector<int> initial_board;
    std::vector<int> board;
    
    int width;
    int height;

    int block_num;
    int shuffle_num;

    static constexpr int DIR_NUM = 4;
    static constexpr std::array<char, DIR_NUM> DIR_CHAR = {'U', 'D', 'L', 'R'};
    static constexpr std::array<std::pair<int, int>, DIR_NUM> DIR_VEC = {{{-1, 0}, {1, 0}, {0, -1}, {0, 1}}};
};