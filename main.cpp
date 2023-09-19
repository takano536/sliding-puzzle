#include "./nlohmann/json.hpp"

#include <fstream>
#include <random>
#include <string>

const std::string CONFIG_FILEPATH = "./config/params.json";

int main() {
    std::random_device seed_gen;
    std::mt19937 rand_engine(seed_gen());
    auto rand = [&rand_engine](int max) -> int { return rand_engine() % max; };

    std::ifstream ifs(CONFIG_FILEPATH);
    nlohmann::json config;
    ifs >> config;
}
