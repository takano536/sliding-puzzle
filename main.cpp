#include "./nlohmann/json.hpp"

#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <queue>
#include <random>
#include <string>
#include <vector>

const std::string CONFIG_FILEPATH = "./config/params.json";

int main() {
    // std::random_device seed_gen;
    // std::mt19937 rand_engine(seed_gen());
    // auto rand = [&rand_engine](int max) -> int { return rand_engine() % max; };

    std::ifstream ifs(CONFIG_FILEPATH);
    nlohmann::json config;
    ifs >> config;

    std::vector<std::vector<int>> field = config["map"];

    const std::map<char, std::pair<int, int>> DIRECTIONS = {
        {'U', {-1, 0}},
        {'R', {0, 1}},
        {'D', {1, 0}},
        {'L', {0, -1}},
    };

    auto is_movable = [&field](int block_idx, int x, int y) -> bool {
        return field[y][x] == 0;
    };
}