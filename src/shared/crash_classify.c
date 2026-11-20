#define WIN32_LEAN_AND_MEAN
#include <windows.h>

#include "crash_classify.h"

int crash_is_fatal(DWORD code) {
    switch (code) {
    case EXCEPTION_ACCESS_VIOLATION:
    case STATUS_HEAP_CORRUPTION:
    case EXCEPTION_STACK_OVERFLOW:
    case EXCEPTION_INT_DIVIDE_BY_ZERO:
    case EXCEPTION_ILLEGAL_INSTRUCTION:
    case EXCEPTION_ARRAY_BOUNDS_EXCEEDED:
    case EXCEPTION_FLT_DENORMAL_OPERAND:
    case EXCEPTION_FLT_DIVIDE_BY_ZERO:
    case EXCEPTION_FLT_INVALID_OPERATION:
    case EXCEPTION_FLT_OVERFLOW:
    case EXCEPTION_FLT_UNDERFLOW:
        return 1;
    default:
        return 0;
    }
}

const char *crash_av_op(ULONG_PTR kind) {
    return kind == 0 ? "READ" :
           kind == 1 ? "WRITE" : "DEP";
}
