#define _POSIX_C_SOURCE 199309L
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

enum { SIDE = 4096 };

static double now_seconds(void) {
    struct timespec time;
    clock_gettime(CLOCK_MONOTONIC, &time);
    return (double)time.tv_sec + (double)time.tv_nsec / 1e9;
}

static double visit_row_major(const uint64_t *array, uint64_t *sum) {
    double start = now_seconds();
    uint64_t total = 0;
    for (int row = 0; row < SIDE; row++) {
        for (int col = 0; col < SIDE; col++) {
            total += array[(size_t)row * SIDE + col];
        }
    }
    *sum = total;
    return now_seconds() - start;
}

static double visit_column_major(const uint64_t *array, uint64_t *sum) {
    double start = now_seconds();
    uint64_t total = 0;
    for (int col = 0; col < SIDE; col++) {
        for (int row = 0; row < SIDE; row++) {
            total += array[(size_t)row * SIDE + col];
        }
    }
    *sum = total;
    return now_seconds() - start;
}

int main(void) {
    size_t elements = (size_t)SIDE * SIDE;
    uint64_t *array = malloc(elements * sizeof(*array));
    if (!array) {
        perror("malloc");
        return 1;
    }

    for (size_t index = 0; index < elements; index++) {
        array[index] = index % 251;
    }

    printf("run,order,seconds,ns_per_element,checksum\n");
    for (int run = 1; run <= 3; run++) {
        for (int step = 0; step < 2; step++) {
            int row_first = run % 2 == 1;
            int do_row = (step == 0) == row_first;
            uint64_t checksum;
            double elapsed = do_row
                ? visit_row_major(array, &checksum)
                : visit_column_major(array, &checksum);
            printf("%d,%s,%.9f,%.3f,%" PRIu64 "\n",
                   run, do_row ? "row-major" : "column-major", elapsed,
                   elapsed * 1e9 / (double)elements, checksum);
        }
    }

    free(array);
    return 0;
}