#include "Vec2.hpp"

bool Vec2::operator==(const Vec2& rhs) const {
    return first == rhs.first && second == rhs.second;
}

bool Vec2::operator!=(const Vec2& rhs) const {
    return !(*this == rhs);
}

bool Vec2::operator<(const Vec2& rhs) const {
    return first < rhs.first || (first == rhs.first && second < rhs.second);
}

bool Vec2::operator>(const Vec2& rhs) const {
    return first > rhs.first || (first == rhs.first && second > rhs.second);
}

bool Vec2::operator<=(const Vec2& rhs) const {
    return *this < rhs || *this == rhs;
}

bool Vec2::operator>=(const Vec2& rhs) const {
    return *this > rhs || *this == rhs;
}

const Vec2 Vec2::operator+(const Vec2& rhs) const {
    return Vec2{first + rhs.first, second + rhs.second};
}

const Vec2 Vec2::operator-(const Vec2& rhs) const {
    return Vec2{first - rhs.first, second - rhs.second};
}

Vec2& Vec2::operator+=(const Vec2& rhs) {
    first += rhs.first;
    second += rhs.second;
    return *this;
}

Vec2& Vec2::operator-=(const Vec2& rhs) {
    first -= rhs.first;
    second -= rhs.second;
    return *this;
}
