/*
 * dot_test.cpp
 *
 *  Created on: 1 Jun 2020
 *      Author: Maxim Masterov
 *     Company: SURFSara
 */

#include <iostream>
#include <vector>
#include <random>
#include <iterator>
#include <algorithm>
#include <sys/time.h>
#include <string>

#ifdef USE_OPENMP
#include <omp.h>
#endif

template<typename T>
class array {
    T *data;
    size_t num_elts;
public:
    array() {
        data = nullptr;
        num_elts = 0;
    }

    ~array() {
        clear();
    }

    void resize(size_t _size) {
        data = new T [_size];
        num_elts = _size;
    }

    void clear() {
        if (data != nullptr) delete[] data;
        data = nullptr;
        num_elts = 0;
    }

    inline T &operator[](size_t _n) {
        return data[_n];
    }

    inline size_t size() {
        return num_elts;
    }
};

inline double getRealTime() {
    struct timeval tv;
    gettimeofday(&tv, 0);
    return (double)tv.tv_sec + 1.0e-6 * (double)tv.tv_usec;
}

inline std::pair<size_t, std::string> getNumElementsFromCommanLine(int argc,
        char** argv) {
    size_t num_elts = 1e6;
    std::string type = "seq";

    if (argc >= 2) {
        num_elts = std::atoi(argv[1]);
        // if (argc == 3) type = argv[2];
    }

    return {num_elts, type};
}

double fillVectorsSequential(array<double> &v1, array<double> &v2) {

    double elp_time;

    elp_time = getRealTime();
#ifdef USE_OPENMP
#pragma omp parallel for schedule(static)
#endif
    for(size_t n = 0; n < v1.size(); ++n) {
        v1[n] = n;
        v2[n] = n;
    }
    elp_time = getRealTime() - elp_time;

    return elp_time;
}

int main(int argc, char** argv) {

    // std::vector<double> v1, v2;
    array<double> v1, v2;
    double res = 0.0;
    int error = EXIT_SUCCESS;
    std::pair<size_t, std::string> input_data = getNumElementsFromCommanLine(
            argc, argv);
    double elp_time;

    std::cout << "\n";

#pragma omp parallel
    {
        int tid = 0;
        int num_thr = 1;
#ifdef USE_OPENMP
        tid = omp_get_thread_num();
        num_thr = omp_get_num_threads();
#endif
//        std::cout << "###  Hi there! " << tid << std::endl;
#pragma omp master
        std::cout << "### Running with " << num_thr << " thread(s)" << "\n";

        if (num_thr > input_data.first) {
#pragma omp master
            std::cout
                    << "### Error: number of elements is less than the number of threads"
                    << std::endl;
            error = EXIT_FAILURE;
        }
    }

    if (error == EXIT_FAILURE)
        return error;

    v1.resize(input_data.first);
    v2.resize(input_data.first);

    std::cout << "### Population type: " << input_data.second << "\n";
    elp_time = fillVectorsSequential(v1, v2);
    std::cout << "### Vector population time: " << elp_time << " seconds"
            << "\n";

    elp_time = getRealTime();
#ifdef USE_OPENMP
#pragma omp parallel for reduction(+:res) schedule(static)
#endif
    for(size_t n = 0; n < input_data.first; ++n) {
        res += v1[n] * v2[n];
    }
    elp_time = getRealTime() - elp_time;

    std::cout << "### Dot-product time: " << elp_time << " seconds" << "\n";
    std::cout << "### Result: " << res << "\n";
    std::cout << std::endl;

    v1.clear();
    v2.clear();
    
    return error;
}
