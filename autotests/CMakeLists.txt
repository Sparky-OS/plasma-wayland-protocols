# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileCopyrightText: 2024 David Redondo <kde@david-redondo.de>

find_package(Python3 REQUIRED COMPONENTS Interpreter)
add_test(NAME virtual-stereo-contract COMMAND Python3::Interpreter ${PROJECT_SOURCE_DIR}/tests/virtual-stereo-contract.py)

file(GLOB PROTOCOLS CONFIGURE_DEPENDS ${PROJECT_SOURCE_DIR}/src/protocols/*.xml)

foreach(PROTOCOL IN LISTS PROTOCOLS)
    get_filename_component(PROTOCOL_BASENAME ${PROTOCOL} NAME_WE)
    set(CLIENT_HEADER  ${PROTOCOL_BASENAME}-client-protocol.h)
    set(SERVER_HEADER ${PROTOCOL_BASENAME}-server-protocol.h)
    set(CODE ${PROTOCOL_BASENAME}-protocol.c)
    add_test(NAME ${PROTOCOL_BASENAME}_client-header COMMAND Wayland::Scanner --strict client-header ${PROTOCOL} ${CLIENT_HEADER})
    add_test(NAME ${PROTOCOL_BASENAME}_server-header COMMAND Wayland::Scanner --strict server-header ${PROTOCOL} ${SERVER_HEADER})
    add_test(NAME ${PROTOCOL_BASENAME}_code COMMAND Wayland::Scanner --strict private-code ${PROTOCOL} ${CODE})
    set_tests_properties(${PROTOCOL_BASENAME}_client-header ${PROTOCOL_BASENAME}_server-header ${PROTOCOL_BASENAME}_code PROPERTIES FIXTURES_SETUP ${PROTOCOL_BASENAME}_protocol)
    # fail if there is any warning from wayland-scanner, except plasma-window-managment which has preexisting issues
    if (NOT ${PROTOCOL_BASENAME} STREQUAL "plasma-window-management")
        set_tests_properties(${PROTOCOL_BASENAME}_client-header ${PROTOCOL_BASENAME}_server-header ${PROTOCOL_BASENAME}_code PROPERTIES FAIL_REGULAR_EXPRESSION ".+")
    endif()
    configure_file(build.c build-${PROTOCOL_BASENAME}.c @ONLY)
    add_test(NAME ${PROTOCOL_BASENAME}_build COMMAND ${CMAKE_C_COMPILER} build-${PROTOCOL_BASENAME}.c ${CODE} -I ${Wayland_INCLUDE_DIRS} -Wl,--unresolved-symbols=ignore-all)
    set_tests_properties(${PROTOCOL_BASENAME}_build PROPERTIES FIXTURES_REQUIRED ${PROTOCOL_BASENAME}_protocol)
endforeach()

find_package(Threads REQUIRED)
find_package(Wayland REQUIRED COMPONENTS Client Server)
add_executable(screencast-properties ../tests/screencast-properties.c)
set(SCREENCAST_XML ${PROJECT_SOURCE_DIR}/src/protocols/zkde-screencast-unstable-v1.xml)
foreach(KIND client server)
    set(HEADER ${CMAKE_CURRENT_BINARY_DIR}/zkde-screencast-unstable-v1-${KIND}-protocol.h)
    add_custom_command(OUTPUT ${HEADER}
        COMMAND Wayland::Scanner --strict ${KIND}-header ${SCREENCAST_XML} ${HEADER}
        DEPENDS ${SCREENCAST_XML})
    target_sources(screencast-properties PRIVATE ${HEADER})
endforeach()
set(SCREENCAST_CODE ${CMAKE_CURRENT_BINARY_DIR}/zkde-screencast-unstable-v1-wire.c)
add_custom_command(OUTPUT ${SCREENCAST_CODE}
    COMMAND Wayland::Scanner --strict private-code ${SCREENCAST_XML} ${SCREENCAST_CODE}
    DEPENDS ${SCREENCAST_XML})
target_sources(screencast-properties PRIVATE ${SCREENCAST_CODE})
target_include_directories(screencast-properties PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
target_link_libraries(screencast-properties PRIVATE Wayland::Client Wayland::Server Threads::Threads m)
target_compile_options(screencast-properties PRIVATE -UNDEBUG)
add_test(NAME screencast-properties COMMAND screencast-properties)
set_tests_properties(screencast-properties PROPERTIES TIMEOUT 10)

add_executable(output-viewport ../tests/output-viewport.c)
set(OUTPUT_XML ${PROJECT_SOURCE_DIR}/src/protocols/kde-output-device-v2.xml)
foreach(KIND client server)
    set(HEADER ${CMAKE_CURRENT_BINARY_DIR}/kde-output-device-v2-${KIND}-protocol.h)
    add_custom_command(OUTPUT ${HEADER}
        COMMAND Wayland::Scanner --strict ${KIND}-header ${OUTPUT_XML} ${HEADER}
        DEPENDS ${OUTPUT_XML})
    target_sources(output-viewport PRIVATE ${HEADER})
endforeach()
set(OUTPUT_CODE ${CMAKE_CURRENT_BINARY_DIR}/kde-output-device-v2-wire.c)
add_custom_command(OUTPUT ${OUTPUT_CODE}
    COMMAND Wayland::Scanner --strict private-code ${OUTPUT_XML} ${OUTPUT_CODE}
    DEPENDS ${OUTPUT_XML})
target_sources(output-viewport PRIVATE ${OUTPUT_CODE})
target_include_directories(output-viewport PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
target_link_libraries(output-viewport PRIVATE Wayland::Client Wayland::Server Threads::Threads)
target_compile_options(output-viewport PRIVATE -UNDEBUG)
add_test(NAME output-viewport COMMAND output-viewport)
set_tests_properties(output-viewport PROPERTIES TIMEOUT 10)
