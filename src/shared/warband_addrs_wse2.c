#include "warband_addrs_wse2.h"

const addr_table g_addrs_client = {
    ADDR_CUR_GAME,
    ADDR_CUR_MISSION,
    ADDR_GLOBAL_VARS_VEC,
    ADDR_GLOBAL_VARS_END,
};

const addr_table g_addrs_campaign = {
    CAMP_ADDR_CUR_GAME,
    CAMP_ADDR_CUR_MISSION,
    CAMP_ADDR_GLOBAL_VARS_VEC,
    CAMP_ADDR_GLOBAL_VARS_END,
};

const addr_table g_addrs_battle = {
    DED_ADDR_CUR_GAME,
    DED_ADDR_CUR_MISSION,
    DED_ADDR_GLOBAL_VARS_VEC,
    DED_ADDR_GLOBAL_VARS_END,
};

const addr_table *g_addrs = NULL;
