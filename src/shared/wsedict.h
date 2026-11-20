#pragma once
#include <stdint.h>

typedef struct wsedict wsedict_t;

wsedict_t *wsedict_create(void);
void       wsedict_set_int(wsedict_t *d, const char *key, int value);
void       wsedict_set_str(wsedict_t *d, const char *key, const char *value);
int        wsedict_save(wsedict_t *d, const char *path);  /* 0=ok, -1=error */
void       wsedict_free(wsedict_t *d);
