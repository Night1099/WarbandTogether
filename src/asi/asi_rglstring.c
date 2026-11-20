#include <string.h>
#include "asi_rglstring.h"

void rglstring_init(char *rs, const char *value) {
    int len = (int)strlen(value);
    memset(rs, 0, RGLSTRING_SIZE);
    if (len > RGLSTRING_SSO_MAX) len = RGLSTRING_SSO_MAX;
    *(int *)(rs + 0x00)   = 0;
    *(char **)(rs + 0x04) = rs + 0x10;
    *(int *)(rs + 0x08)   = 48;
    *(int *)(rs + 0x0C)   = len;
    memcpy(rs + 0x10, value, len);
    rs[0x10 + len] = '\0';
}

void rglstring_set_sso(char *rs, const char *value) {
    int len = (int)strlen(value);
    if (len > RGLSTRING_SSO_MAX) len = RGLSTRING_SSO_MAX;
    memcpy(rs + 0x10, value, len);
    rs[0x10 + len] = '\0';
    *(char **)(rs + 0x04) = rs + 0x10;
    *(int *)(rs + 0x08)   = 48;
    *(int *)(rs + 0x0C)   = len;
    *(int *)(rs + 0x00)   = 0;
}

int rglstring_assign_in_place(char *rs, const char *value) {
    int cap = *(int *)(rs + 0x08);
    int len = (int)strlen(value);
    char *buf;
    if (len >= cap) return 0;
    buf = *(char **)(rs + 0x04);
    memcpy(buf, value, len);
    buf[len] = '\0';
    *(int *)(rs + 0x0C) = len;
    return 1;
}

int rglstring_is_constructed(const char *rs) {
    return *(char *const *)(rs + 0x04) != NULL;
}
