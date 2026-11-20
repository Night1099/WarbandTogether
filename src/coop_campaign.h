#pragma once

#include "exe_personality.h"

void campaign_init_from_ini(const char *dll_dir);
void campaign_shutdown(void);
coop_mode_t campaign_get_mode(void);
