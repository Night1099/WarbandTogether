/* browser_row -- the "COOP Direct" row the ASI adds to the MP browser.
 *
 * Every scan wipes g_multiplayerData.m_serverList and the engine never
 * updates a row in place, so the row is pushed once after each scan, with
 * the right address and flags at push time. The row is an mbnetServer
 * (0x180 bytes; findings_table_widget.md); the browser lists it only when
 * m_moduleName matches the running module's directory name.
 */

#ifndef COOP_BROWSER_ROW_H
#define COOP_BROWSER_ROW_H

#define BROWSER_ROW_SIZE 0x180
#define BROWSER_ROW_NAME "COOP Direct"

/* 1 when a row in [first, last) (BROWSER_ROW_SIZE apart) already has this
   ip AND port: a re-Search inside 20 s re-pings the current list without
   clearing it. */
int browser_row_exists(const char *first, const char *last, const char *ip, int port);

/* Writes the row's fields over an engine-constructed mbnetServer. */
void browser_row_fill(char *row, const char *ip, int port, const char *module, int passworded);

/* Per-frame injection gate. Every early-out is edge-logged so a missing row
   is diagnosable from the log. */
typedef struct browser_inject {
    int last_mode;           /* gameType last logged */
    int searching_prev;
    int scan_was_active;     /* a scan ran since the process started */
    int injected;            /* the row was pushed since the last scan */
    int pending_logged;
    int null_table_logged;
} browser_inject;

#define BROWSER_INJECT_INIT { 0x7FFFFFFF, 0, 0, 0, 0, 0 }

/* Returns 1 when the row must be pushed now (and marks it pushed): on a
   campaign client (gameType 4), after a scan has finished, once per scan,
   never while the Steam client verdict is pending (cli_state, read only at
   that point; the row would latch a LAN address), and only once the
   browser's table widget exists. */
int browser_inject_step(browser_inject *st, int game_type, int searching,
                        int (*cli_state)(void), const void *table);

#endif
