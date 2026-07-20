#pragma once

/* Dedicated-server personalities; the winmm loader never loads the
   plugin into game clients (coop_loader.c). */
typedef enum { COOP_HOST, COOP_BATTLE } coop_mode_t;

void campaign_init_from_ini(const char *dll_dir);
void campaign_shutdown(void);
coop_mode_t campaign_get_mode(void);
