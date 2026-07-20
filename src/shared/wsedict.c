#define _CRT_SECURE_NO_WARNINGS
#include "wsedict.h"
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char *key;
    char *val;
} wsedict_entry_t;

struct wsedict {
    wsedict_entry_t *entries;
    uint32_t         count;
    uint32_t         capacity;
};

static const char MAGIC[4] = { 'D', 'E', 'S', 'W' };
static const uint32_t VERSION = 2;

static int wsedict_grow(wsedict_t *d);

wsedict_t *wsedict_create(void) {
    return (wsedict_t *)calloc(1, sizeof(wsedict_t));
}

wsedict_t *wsedict_load(const char *path) {
    FILE *f;
    char hdr[4];
    uint32_t ver, count, i;
    wsedict_t *d;

    if (!path) return NULL;
    f = fopen(path, "rb");
    if (!f) return NULL;

    if (fread(hdr, 1, 4, f) != 4 || memcmp(hdr, MAGIC, 4) != 0)     goto fail;
    if (fread(&ver, 4, 1, f) != 1 || ver != VERSION)                  goto fail;
    if (fread(&count, 4, 1, f) != 1)                                   goto fail;

    d = wsedict_create();
    if (!d) goto fail;

    for (i = 0; i < count; i++) {
        uint32_t key_len, val_len;
        char *key, *val;

        if (fread(&key_len, 4, 1, f) != 1) goto fail_d;
        if (fread(&val_len, 4, 1, f) != 1) goto fail_d;

        key = (char *)malloc(key_len + 1);
        val = (char *)malloc(val_len + 1);
        if (!key || !val) { free(key); free(val); goto fail_d; }

        if (key_len && fread(key, 1, key_len, f) != key_len) { free(key); free(val); goto fail_d; }
        if (val_len && fread(val, 1, val_len, f) != val_len) { free(key); free(val); goto fail_d; }
        key[key_len] = '\0';
        val[val_len] = '\0';

        if (wsedict_grow(d) != 0) { free(key); free(val); goto fail_d; }
        d->entries[d->count].key = key;
        d->entries[d->count].val = val;
        d->count++;
    }

    fclose(f);
    return d;

fail_d:
    wsedict_free(d);
fail:
    fclose(f);
    return NULL;
}

/* Find existing entry by key, or -1 if not found */
static int wsedict_find(wsedict_t *d, const char *key) {
    uint32_t i;
    for (i = 0; i < d->count; i++) {
        if (strcmp(d->entries[i].key, key) == 0)
            return (int)i;
    }
    return -1;
}

/* Grow the entry array if at capacity */
static int wsedict_grow(wsedict_t *d) {
    uint32_t new_cap;
    wsedict_entry_t *new_entries;

    if (d->count < d->capacity)
        return 0;

    new_cap = d->capacity ? d->capacity * 2 : 16;
    new_entries = (wsedict_entry_t *)realloc(d->entries, new_cap * sizeof(wsedict_entry_t));
    if (!new_entries)
        return -1;

    d->entries = new_entries;
    d->capacity = new_cap;
    return 0;
}

int wsedict_get_int(wsedict_t *d, const char *key, int default_val) {
    int idx;
    if (!d || !key) return default_val;
    idx = wsedict_find(d, key);
    if (idx < 0) return default_val;
    return atoi(d->entries[idx].val);
}

void wsedict_set_str(wsedict_t *d, const char *key, const char *value) {
    int idx;
    char *val_dup;

    if (!d || !key || !value)
        return;

    val_dup = _strdup(value);
    if (!val_dup)
        return;

    idx = wsedict_find(d, key);
    if (idx >= 0) {
        free(d->entries[idx].val);
        d->entries[idx].val = val_dup;
        return;
    }

    if (wsedict_grow(d) != 0) {
        free(val_dup);
        return;
    }

    d->entries[d->count].key = _strdup(key);
    if (!d->entries[d->count].key) {
        free(val_dup);
        return;
    }
    d->entries[d->count].val = val_dup;
    d->count++;
}

void wsedict_set_int(wsedict_t *d, const char *key, int value) {
    char buf[32];
    _snprintf(buf, sizeof(buf), "%d", value);
    wsedict_set_str(d, key, buf);
}

int wsedict_save(wsedict_t *d, const char *path) {
    char tmp_path[MAX_PATH];
    FILE *f;
    uint32_t i, key_len, val_len;

    if (!d || !path)
        return -1;

    _snprintf(tmp_path, sizeof(tmp_path), "%s.tmp", path);

    f = fopen(tmp_path, "wb");
    if (!f)
        return -1;

    /* Header: magic + version + entry count */
    if (fwrite(MAGIC, 1, 4, f) != 4)           goto fail;
    if (fwrite(&VERSION, 4, 1, f) != 1)        goto fail;
    if (fwrite(&d->count, 4, 1, f) != 1)       goto fail;

    /* Entries */
    for (i = 0; i < d->count; i++) {
        key_len = (uint32_t)strlen(d->entries[i].key);
        val_len = (uint32_t)strlen(d->entries[i].val);

        if (fwrite(&key_len, 4, 1, f) != 1)                goto fail;
        if (fwrite(&val_len, 4, 1, f) != 1)                goto fail;
        if (key_len && fwrite(d->entries[i].key, 1, key_len, f) != key_len)
            goto fail;
        if (val_len && fwrite(d->entries[i].val, 1, val_len, f) != val_len)
            goto fail;
    }

    fclose(f);

    /* Atomic replace */
    if (!MoveFileExA(tmp_path, path, MOVEFILE_REPLACE_EXISTING)) {
        DeleteFileA(tmp_path);
        return -1;
    }

    return 0;

fail:
    fclose(f);
    DeleteFileA(tmp_path);
    return -1;
}

void wsedict_free(wsedict_t *d) {
    uint32_t i;
    if (!d) return;
    for (i = 0; i < d->count; i++) {
        free(d->entries[i].key);
        free(d->entries[i].val);
    }
    free(d->entries);
    free(d);
}
