// SPDX-License-Identifier: MIT

#include "zkde-screencast-unstable-v1-client-protocol.h"
#include "zkde-screencast-unstable-v1-server-protocol.h"

#include <assert.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <wayland-client.h>
#include <wayland-server.h>

static struct wl_display *server;
static atomic_bool done;
static int received;
static int closed;
static struct zkde_screencast_unstable_v1 *manager;

static void close_stream(struct wl_client *client, struct wl_resource *resource)
{
    ++closed;
    wl_resource_destroy(resource);
}

static const struct zkde_screencast_stream_unstable_v1_interface stream_impl = {
    .close = close_stream,
};

static void properties(struct wl_client *client, struct wl_resource *resource,
                       uint32_t id, const char *name, const char *description,
                       int32_t width, int32_t height, uint32_t refresh,
                       wl_fixed_t scale, uint32_t physical_width,
                       uint32_t physical_height, uint32_t headset, uint32_t pointer)
{
    assert(strcmp(name, "phone-test-identity") == 0);
    assert(strcmp(description, "Flat Headset (test panel)") == 0);
    assert(width == 2400 && height == 1080);
    assert(refresh == 59940);
    assert(wl_fixed_to_double(scale) == 1.25);
    assert(physical_width == 150 && physical_height == 68);
    assert(headset == 1);
    assert(pointer == ZKDE_SCREENCAST_UNSTABLE_V1_POINTER_HIDDEN);
    struct wl_resource *stream = wl_resource_create(client, &zkde_screencast_stream_unstable_v1_interface,
                                                    wl_resource_get_version(resource), id);
    assert(stream);
    wl_resource_set_implementation(stream, &stream_impl, NULL, NULL);
    ++received;
}

static void destroy_manager(struct wl_client *client, struct wl_resource *resource)
{
    wl_resource_destroy(resource);
}

static const struct zkde_screencast_unstable_v1_interface manager_impl = {
    .destroy = destroy_manager,
    .stream_virtual_output_with_properties = properties,
};

static void bind_manager(struct wl_client *client, void *data, uint32_t version, uint32_t id)
{
    struct wl_resource *resource = wl_resource_create(client, &zkde_screencast_unstable_v1_interface, version, id);
    assert(resource);
    wl_resource_set_implementation(resource, &manager_impl, NULL, NULL);
}

static void global(void *data, struct wl_registry *registry, uint32_t name, const char *interface, uint32_t version)
{
    if (strcmp(interface, zkde_screencast_unstable_v1_interface.name) == 0 && version >= 7) {
        manager = wl_registry_bind(registry, name, &zkde_screencast_unstable_v1_interface, 7);
    }
}

static void global_remove(void *data, struct wl_registry *registry, uint32_t name)
{
}

static const struct wl_registry_listener registry_listener = {global, global_remove};

static void *dispatch(void *unused)
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
    assert(socketpair(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0, sockets) == 0);
    server = wl_display_create();
    assert(server);
    assert(wl_global_create(server, &zkde_screencast_unstable_v1_interface, version, NULL, bind_manager));
    assert(wl_client_create(server, sockets[0]));
    struct wl_display *client = wl_display_connect_to_fd(sockets[1]);
    assert(client);
    manager = NULL;
    received = closed = 0;
    atomic_store(&done, false);
    pthread_t thread;
    assert(pthread_create(&thread, NULL, dispatch, NULL) == 0);
    struct wl_registry *registry = wl_display_get_registry(client);
    wl_registry_add_listener(registry, &registry_listener, NULL);
    assert(wl_display_roundtrip(client) >= 0);
    if (version >= 7) {
        assert(manager);
        struct zkde_screencast_stream_unstable_v1 *stream =
            zkde_screencast_unstable_v1_stream_virtual_output_with_properties(
                manager, "phone-test-identity", "Flat Headset (test panel)",
                2400, 1080, 59940, wl_fixed_from_double(1.25), 150, 68, 1,
                ZKDE_SCREENCAST_UNSTABLE_V1_POINTER_HIDDEN);
        assert(wl_display_roundtrip(client) >= 0);
        zkde_screencast_stream_unstable_v1_close(stream);
        zkde_screencast_unstable_v1_destroy(manager);
        assert(wl_display_roundtrip(client) >= 0);
    } else {
        assert(!manager);
    }
    atomic_store(&done, true);
    assert(pthread_join(thread, NULL) == 0);
    assert(received == (version >= 7));
    assert(closed == (version >= 7));
    wl_registry_destroy(registry);
    wl_display_disconnect(client);
    wl_display_destroy_clients(server);
    wl_display_destroy(server);
}

int main(void)
{
    run(7);
    run(6);
    puts("v7: exact panel properties and close received; v6: no fallback request");
}
