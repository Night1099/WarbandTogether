#pragma once
#include <stdint.h>

/* Initialize IPC channel. Returns 0 on success.
   is_listener=1: campaign server listens on port for up to max_peers
                  battle servers.
   is_listener=0: battle server connects to localhost:port (max_peers
                  ignored, single outbound peer). */
int  bnet_init(int is_listener, int port, int max_peers);
void bnet_poll(void);

/* Outbound send on the single client-mode peer (battle server side). */
void bnet_send(const uint8_t *data, int len);

/* Client mode only: re-issue the connect after a drop. No-op while a
   connect is pending or established. */
void bnet_reconnect(void);

void bnet_shutdown(void);
int  bnet_is_connected(void);

typedef void (*bnet_recv_cb)(void *peer, const uint8_t *data, int len);
void bnet_set_recv_callback(bnet_recv_cb cb);

/* connected=1 on ENet CONNECT, 0 on DISCONNECT. Fires in both modes. */
typedef void (*bnet_event_cb)(void *peer, int connected);
void bnet_set_event_callback(bnet_event_cb cb);
