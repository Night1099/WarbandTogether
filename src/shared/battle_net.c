#include "battle_net.h"
#include <enet/enet.h>

extern void coop_log(const char *fmt, ...);

static ENetHost *g_bhost;
static ENetPeer *g_bpeer;          /* client mode: the outbound peer */
static ENetAddress g_baddr;        /* client mode: connect target */
static int g_is_listener;
static bnet_recv_cb  g_brecv_cb;
static bnet_event_cb g_bevent_cb;

int bnet_init(int is_listener, int port, int max_peers)
{
    if (enet_initialize() != 0) {
        coop_log("[bnet] enet_initialize failed\n");
        return -1;
    }
    g_is_listener = is_listener;

    if (is_listener) {
        ENetAddress addr;
        addr.host = ENET_HOST_ANY;
        addr.port = (enet_uint16)port;
        g_bhost = enet_host_create(&addr, (size_t)max_peers, 1, 0, 0);
        if (!g_bhost) {
            coop_log("[bnet] host create failed on port %d\n", port);
            enet_deinitialize();
            return -1;
        }
        coop_log("[bnet] listening on port %d (max %d peers)\n", port, max_peers);
    } else {
        g_bhost = enet_host_create(NULL, 1, 1, 0, 0);
        if (!g_bhost) {
            coop_log("[bnet] client host create failed\n");
            enet_deinitialize();
            return -1;
        }
        enet_address_set_host(&g_baddr, "127.0.0.1");
        g_baddr.port = (enet_uint16)port;
        g_bpeer = enet_host_connect(g_bhost, &g_baddr, 1, 0);
        if (!g_bpeer) {
            coop_log("[bnet] connect to 127.0.0.1:%d failed\n", port);
            enet_host_destroy(g_bhost);
            g_bhost = NULL;
            enet_deinitialize();
            return -1;
        }
        coop_log("[bnet] connecting to 127.0.0.1:%d\n", port);
    }
    return 0;
}

void bnet_poll(void)
{
    ENetEvent event;
    if (!g_bhost) return;

    while (enet_host_service(g_bhost, &event, 0) > 0) {
        switch (event.type) {
        case ENET_EVENT_TYPE_CONNECT:
            if (!g_is_listener) g_bpeer = event.peer;
            coop_log("[bnet] peer connected\n");
            if (g_bevent_cb) g_bevent_cb(event.peer, 1);
            break;
        case ENET_EVENT_TYPE_RECEIVE:
            if (g_brecv_cb)
                g_brecv_cb(event.peer, event.packet->data, (int)event.packet->dataLength);
            enet_packet_destroy(event.packet);
            break;
        case ENET_EVENT_TYPE_DISCONNECT:
            coop_log("[bnet] peer disconnected\n");
            if (!g_is_listener && event.peer == g_bpeer) g_bpeer = NULL;
            if (g_bevent_cb) g_bevent_cb(event.peer, 0);
            break;
        default:
            break;
        }
    }
}

void bnet_send(const uint8_t *data, int len)
{
    ENetPacket *pkt;
    if (!g_bpeer) return;

    pkt = enet_packet_create(data, (size_t)len, ENET_PACKET_FLAG_RELIABLE);
    enet_peer_send(g_bpeer, 0, pkt);
    enet_host_flush(g_bhost);
}

void bnet_reconnect(void)
{
    if (g_is_listener || !g_bhost || g_bpeer) return;
    g_bpeer = enet_host_connect(g_bhost, &g_baddr, 1, 0);
    coop_log("[bnet] reconnecting to 127.0.0.1:%d\n", (int)g_baddr.port);
}

void bnet_shutdown(void)
{
    if (g_bpeer) {
        enet_peer_disconnect_now(g_bpeer, 0);
        g_bpeer = NULL;
    }
    if (g_bhost) {
        enet_host_destroy(g_bhost);
        g_bhost = NULL;
    }
    enet_deinitialize();
    coop_log("[bnet] shutdown\n");
}

int bnet_is_connected(void)
{
    return g_bpeer != NULL && g_bpeer->state == ENET_PEER_STATE_CONNECTED;
}

void bnet_set_recv_callback(bnet_recv_cb cb)
{
    g_brecv_cb = cb;
}

void bnet_set_event_callback(bnet_event_cb cb)
{
    g_bevent_cb = cb;
}
