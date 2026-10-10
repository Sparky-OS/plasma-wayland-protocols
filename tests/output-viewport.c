// SPDX-License-Identifier: MIT
#include "kde-output-device-v2-client-protocol.h"
#include "kde-output-device-v2-server-protocol.h"

#include <assert.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <wayland-client.h>
#include <wayland-server.h>

static struct wl_display *server;
static atomic_bool done;
static struct kde_output_device_mode_v2 *mode;
static int panel_width, panel_height, view_width, view_height, refresh;

static void size(void *data, struct kde_output_device_mode_v2 *object, int32_t width, int32_t height)
{
    panel_width = width;
    panel_height = height;
}

static void rate(void *data, struct kde_output_device_mode_v2 *object, int32_t value)
{
    refresh = value;
}

static void viewport(void *data, struct kde_output_device_mode_v2 *object, int32_t width, int32_t height)
{
    view_width = width;
    view_height = height;
}

static const struct kde_output_device_mode_v2_listener listener = {
    .size = size, .refresh = rate, .view_size = viewport,
};

static void bind_mode(struct wl_client *client, void *data, uint32_t version, uint32_t id)
{
    struct wl_resource *resource = wl_resource_create(client, &kde_output_device_mode_v2_interface, version, id);
    assert(resource);
    kde_output_device_mode_v2_send_size(resource, 2400, 1080);
    kde_output_device_mode_v2_send_refresh(resource, 59940);
    if (version >= 25) {
        kde_output_device_mode_v2_send_view_size(resource, 1200, 1080);
    }
}

static void global(void *data, struct wl_registry *registry, uint32_t name, const char *interface, uint32_t version)
{
    if (!strcmp(interface, kde_output_device_mode_v2_interface.name)) {
        mode = wl_registry_bind(registry, name, &kde_output_device_mode_v2_interface, version);
        kde_output_device_mode_v2_add_listener(mode, &listener, NULL);
    }
}

static void global_remove(void *data, struct wl_registry *registry, uint32_t name) {}
static const struct wl_registry_listener globals = {global, global_remove};

static void *dispatch(void *data)
{
    while (!atomic_load(&done)) {
        assert(wl_event_loop_dispatch(wl_display_get_event_loop(server), 10) >= 0);
        wl_display_flush_clients(server);
    }
    return NULL;
}

static void run(uint32_t version)
{
    int sockets[2];
    assert(!socketpair(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0, sockets));
    server = wl_display_create();
    assert(server);
    // Export the mode directly to isolate its event serialization.
    assert(wl_global_create(server, &kde_output_device_mode_v2_interface, version, NULL, bind_mode));
    assert(wl_client_create(server, sockets[0]));
    struct wl_display *client = wl_display_connect_to_fd(sockets[1]);
    assert(client);
    panel_width = panel_height = view_width = view_height = refresh = 0;
    mode = NULL;
    atomic_store(&done, false);
    pthread_t thread;
    assert(!pthread_create(&thread, NULL, dispatch, NULL));
    struct wl_registry *registry = wl_display_get_registry(client);
    wl_registry_add_listener(registry, &globals, NULL);
    assert(wl_display_roundtrip(client) >= 0);
    assert(wl_display_roundtrip(client) >= 0);
    assert(mode);
    assert(panel_width == 2400 && panel_height == 1080 && refresh == 59940);
    assert(view_width == (version >= 25 ? 1200 : 0));
    assert(view_height == (version >= 25 ? 1080 : 0));
    atomic_store(&done, true);
    assert(!pthread_join(thread, NULL));
    kde_output_device_mode_v2_destroy(mode);
    wl_registry_destroy(registry);
    wl_display_disconnect(client);
    wl_display_destroy_clients(server);
    wl_display_destroy(server);
}

int main(void)
{
    run(25);
    run(24);
    puts("v25 separates panel and viewport dimensions; v24 receives no new event");
}
