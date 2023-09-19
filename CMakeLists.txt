cmake_minimum_required(VERSION 3.1...3.5)
project(sliding-puzzle CXX)
set(CMAKE_CXX_FLAGS "-std=c++20 -Wall -Wextra -O2")
add_executable(
    main 
    main.cpp
    ./modules/Solver/Solver.cpp 
    ./modules/Vec2/Vec2.cpp
)